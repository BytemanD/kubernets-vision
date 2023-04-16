import json
import logging
import yaml
import inspect

from tornado import web
from kubevision.k8s import api
from kubevision.k8s import objects

from kubevision.common import conf
from kubevision.common import constants
from kubevision.common import exceptions
from kubevision.common import utils
from kubevision.common import wsgi

LOG = logging.getLogger(__name__)
CONF = conf.CONF

CONF_DB_API = None
RUN_AS_CONTAINER = False
ROUTES = []
EXEC_HOSTORY = [];

def registry_route(url):

    def registry(cls):
        global ROUTES

        ROUTES.append((url, cls))
        return cls
    return registry


class ObjectMixin(object):

    @classmethod
    def to_yaml(cls, obj):
        # TODO
        # move this code to objects
        obj_dict = obj.to_dict()
        metadata = obj_dict.get('metadata')

        utils.format_time(metadata, 'creation_timestamp')
        if 'managed_fields' in metadata:
            metadata['managed_fields'] = None

        status = obj_dict.get('status')
        if 'conditions' in status:
            for condition in status.get('conditions') or []:
                utils.format_time(condition, 'last_heartbeat_time')
                utils.format_time(condition, 'last_transition_time')

        return yaml.dump(obj_dict)


@registry_route(r'/')
class Index(wsgi.BaseReqHandler):

    def get(self):
        if CONF.index_redirect:
            self.redirect(CONF.index_redirect)
        else:
            self.redirect('index.html')


@registry_route(r'/.+\.html')
class Html(wsgi.BaseReqHandler):

    def get(self):
        try:
            self.render(self.request.path[1:])
        except FileNotFoundError:
            self.set_status(404)
            self.finish({'error': f'{self.request.path[1:]} not found'})


@registry_route(r'/config.json')
class ConfigJson(wsgi.BaseReqHandler):

    def get(self):
        try:
            self.render(self.request.path[1:])
        except FileNotFoundError:
            self.set_status(404)
            self.finish({'error': f'{self.request.path[1:]} not found'})


@registry_route(r'/version')
class ConfigJson(wsgi.BaseReqHandler):

    @utils.with_response()
    def get(self):
        return {'version': {'backend': utils.get_version()}}


@registry_route(r'/node')
class Nodes(wsgi.RequestContext):

    @utils.response
    def get(self):
        items = api.CLIENT.list_node()
        return {'nodes': [item.__dict__ for item in items]}


@registry_route(r'/node/(.*)')
class Node(wsgi.BaseReqHandler, ObjectMixin):

    @utils.response
    def get(self, name):
        node = api.CLIENT.get_node(name)
        return {'node': self.to_yaml(node)}


@registry_route(r'/namespace')
class Namespaces(wsgi.BaseReqHandler):

    @utils.response
    def get(self):
        namespaces = api.CLIENT.list_namespace()
        return {'namespaces': [item.__dict__ for item in namespaces]}


@registry_route(r'/namespace/(.+)')
class Namespace(wsgi.BaseReqHandler, ObjectMixin):

    @utils.response
    def get(self, name):
        namespace = api.CLIENT.get_namespace(name)
        fmt = self.get_argument('format', 'json')
        if fmt and fmt not in ['json', 'yaml']:
            raise exceptions.ApiException(400, f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.Namespace.from_object(namespace).__dict__
        elif fmt == 'yaml':
            result = self.to_yaml(namespace)
        return {'namespace': result}


@registry_route(r'/deployment')
class Deployments(wsgi.RequestContext):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_deploy(ns=context.namespace)
        return {'deployments': [item.__dict__ for item in items]}


@registry_route(r'/daemonset')
class Daemonsets(wsgi.RequestContext):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_daemonset(ns=context.namespace)
        return {'daemonsets': [item.__dict__ for item in items]}


@registry_route(r'/deployment/(.+)')
class Deployment(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self, name):
        context = self.get_context()
        deploy = api.CLIENT.get_deploy(name, ns=context.namespace)
        fmt = self.get_argument('format', 'json')
        if fmt and fmt not in ['json', 'yaml']:
            raise exceptions.ApiException(400, f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.Deployment.from_object(deploy).__dict__
        elif fmt == 'yaml':
            result = self.to_yaml(deploy)
        return {'deployment': result}

    @utils.with_response(return_code=204)
    def delete(self, name):
        context = self.get_context()
        api.CLIENT.delete_deploy(name, ns=context.namespace)


@registry_route(r'/daemonset/(.+)')
class Daemonset(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self, name):
        context = self.get_context()
        daemonset = api.CLIENT.get_daemonset(name, ns=context.namespace)
        fmt = self.get_argument('format', 'json')
        if fmt and fmt not in ['json', 'yaml']:
            raise exceptions.ApiException(400, f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.DaemonSet.from_object(daemonset).__dict__
        elif fmt == 'yaml':
            result = self.to_yaml(daemonset)
        return {'daemonset': result}

    @utils.with_response(return_code=204)
    def delete(self, daemonset):
        context = self.get_context()
        api.CLIENT.delete_daemonset(daemonset, ns=context.namespace)

    @utils.with_response(return_code=202)
    def put(self, daemonset):
        """
        body:
        {
            daemonset: {
                containers: {
                    <container name>: {
                        name: <container name>,
                        image: <image name>,
                    }
                }
            }
        }
        """
        context = self.get_context()
        data = self._get_body().get('daemonset', {})
        force = data.get('force', False)
        containers = data.get('containers', {})
        ds = api.CLIENT.get_daemonset(daemonset, ns=context.namespace)
        if containers:
            for container in ds.spec.template.spec.containers:
                new_image =  containers.get(container.name, {}).get('image')
                if not new_image:
                    continue
                container.image = new_image
                LOG.info('container %s new image: %s', container.name, container.image)

        if force:
            # TODO
            api.CLIENT.replace_daemonset(daemonset, ds, ns=context.namespace,
                                         _request_timeout=0)
        else:
            api.CLIENT.replace_daemonset(daemonset, ds, ns=context.namespace)
        return {}


@registry_route(r'/pod')
class Pods(wsgi.RequestContext):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_pod(ns=context.namespace)
        return {'pods': [item.__dict__ for item in items]}


@registry_route(r'/pod/(.+)')
class Pod(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self, name):
        context = self.get_context()
        pod = api.CLIENT.get_pod(name, ns=context.namespace)
        fmt = self.get_argument('format', 'json')
        if fmt and fmt not in ['json', 'yaml']:
            raise exceptions.ApiException(400, f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.Pod.from_object(pod).__dict__
        elif fmt == 'yaml':
            result = self.to_yaml(pod)
        return {'pod': result}

    @utils.with_response(return_code=204)
    def delete(self, name):
        context = self.get_context()
        LOG.debug('options request')
        api.CLIENT.delete_pod(name, ns=context.namespace)


@registry_route(r'/service')
class Service(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_service(ns=context.namespace)
        return {'services': [item.__dict__ for item in items]}


@registry_route(r'/cronjob')
class Cronjob(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_cron_job(ns=context.namespace)
        return {'cronjobs': [item.__dict__ for item in items]}


@registry_route(r'/job')
class Job(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_service(ns=context.namespace)
        return {'services': [item.__dict__ for item in items]}


@registry_route(r'/configmap')
class ConfigMaps(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_configmap(ns=context.namespace)
        return {'configmaps': [item.__dict__ for item in items]}


@registry_route(r'/action')
class Action(wsgi.BaseAction):

    @utils.register_action('deleteLabel')
    def _action_delete_label(self, context, data):
        kind = data.get('kind')
        if kind == 'node':
            return api.CLIENT.delete_node_label(data.get('name'),
                                                data.get('label'))

    @utils.register_action('addLabel')
    def _action_add_label(self, context, data):
        """Add Label

        Args:
            body (dict): request body
        """
        kind = data.get('kind')
        if kind == 'node':
            return api.CLIENT.add_node_label(data.get('name'),
                                             data.get('labels'))

    @utils.register_action('exec')
    def _action_exec_on_pod(self, context, data):
        if 'pod' not in data or 'command' not in data:
            raise exceptions.ApiException(400, 'pod and command must set')
        result = api.CLIENT.exec_on_pod(data.get('pod'), data.get('command'),
                                        ns=context.namespace,
                                        container=data.get('container'))
        return {'exec': result}

    @utils.register_action('addExecHistory')
    def _action_add_exec_history(self, context, data):
        global EXEC_HOSTORY

        exec = data.get('exec', '').strip()
        if not exec:
            raise exceptions.ApiException(400, 'exec is empty')
        if exec not in EXEC_HOSTORY:
            EXEC_HOSTORY.insert(0, exec)

    @utils.register_action('getExecHistory')
    def _action_get_exec_history(self, context, data):
        global EXEC_HOSTORY

        # TODO
        return {'history': EXEC_HOSTORY[:10]}

    @utils.register_action('getLog')
    def _action_get_logs(self, context, data):
        pod = data.get('pod')
        lines = int(data.get('lines', constants.DEFAULT_LOG_LINES))
        params = {}
        if 'container' in data:
            params['container'] = data.get('container')
        logs = api.CLIENT.get_pod_logs(pod, ns=context.namespace,
                                       tail_lines=lines,
                                       **params)
        return {'logs': logs}

    @utils.register_action('getClusterInfo')
    def _action_get_cluster_info(self, context, data):
        return {'cluster_info': api.CLIENT.get_cluster_info()}


class Configs(web.RequestHandler):

    def get(self):
        global CONF_DB_API

        self.set_status(200)
        self.finish({'configs': [
            item.to_dict() for item in CONF_DB_API.list()]
        })


class Cluster(web.RequestHandler):

    def get(self):
        cluster_list = api.query_cluster()
        self.set_status(200)
        self.finish({
            'clusters': [cluster.to_dict() for cluster in cluster_list]
        })

    def post(self):
        data = json.loads(self.request.body)
        cluster = data.get('cluster', {})
        LOG.debug('add cluster: %s', data)
        try:
            api.create_cluster(cluster.get('name'), cluster.get('authUrl'),
                               cluster.get('authProject'),
                               cluster.get('authUser'),
                               cluster.get('authPassword'))
            self.set_status(200)
            self.finish(json.dumps({}))
        except Exception as e:
            LOG.exception(e)
            self.set_status(400)
            self.finish({'error': str(e)})

    def delete(self, cluster_id):
        deleted = api.delete_cluster_by_id(cluster_id)
        if deleted >= 1:
            self.set_status(204)
            self.finish()
        else:
            self.set_status(404)
            self.finish({'error': f'cluster {cluster_id} is not found'})
        return


def get_routes():
    return ROUTES
