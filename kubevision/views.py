import json
import logging
import yaml

from tornado import web
from kubevision.k8s import api
from kubevision.k8s import objects

from easy2use import fs
from easy2use.web import application

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
EXEC_HOSTORY = []


def registry_route(url):

    def registry(cls):
        global ROUTES

        if url in [route[0] for route in ROUTES]:
            raise exceptions.RouteExists(route=url)
        LOG.info('register route %s %s', url, cls)
        ROUTES.append((url, cls))
        return cls
    return registry


class ObjectMixin(object):


    def _get_obj(self, k8s_obj, cls: objects.BaseDataObject, fmt=None,
                 **kwargs):
        if fmt and fmt not in ['json', 'yaml']:
            raise exceptions.InvalidRequest(f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = cls.from_object(k8s_obj, **kwargs).__dict__
        elif fmt == 'yaml':
            result = cls.to_yaml(k8s_obj)
        return result


@registry_route(r'/config.json')
class ConfigJson(wsgi.RequestContext):

    def get(self):
        try:
            self.render(self.request.path[1:])
        except FileNotFoundError:
            self.set_status(404)
            self.finish({'error': f'{self.request.path[1:]} not found'})


@registry_route(r'/version')
class Version(wsgi.RequestContext):

    @application.with_response()
    def get(self):
        return {'version': {'backend': utils.get_version()}}


@registry_route(r'/node')
class Nodes(wsgi.RequestContext):

    @utils.response
    def get(self):
        items = api.CLIENT.list_node()
        return {'nodes': [item.__dict__ for item in items]}


@registry_route(r'/node/(.*)')
class Node(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self, name):
        node = api.CLIENT.get_node(name)
        return {'node': objects.Node.to_yaml(node)}


@registry_route(r'/namespace')
class Namespaces(wsgi.RequestContext):

    @utils.response
    def get(self):
        namespaces = api.CLIENT.list_namespace()
        return {'namespaces': [item.__dict__ for item in namespaces]}


@registry_route(r'/namespace/(.+)')
class Namespace(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self, name):
        namespace = api.CLIENT.get_namespace(name)
        fmt = self.get_argument('format', 'json')
        if fmt and fmt not in ['json', 'yaml']:
            raise exceptions.InvalidRequest(f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.Namespace.from_object(namespace).__dict__
        elif fmt == 'yaml':
            result = objects.Namespace.to_yaml(namespace)
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
            raise exceptions.InvalidRequest(f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.Deployment.from_object(deploy).__dict__
        elif fmt == 'yaml':
            result = objects.Deployment.to_yaml(deploy)
        return {'deployment': result}

    @application.with_response(return_code=204)
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
            raise exceptions.InvalidRequest(f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.DaemonSet.from_object(daemonset).__dict__
        elif fmt == 'yaml':
            result = objects.DaemonSet.to_yaml(daemonset)
        return {'daemonset': result}

    @application.with_response(return_code=204)
    def delete(self, daemonset):
        context = self.get_context()
        api.CLIENT.delete_daemonset(daemonset, ns=context.namespace)

    @application.with_response(return_code=202)
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
                new_image = containers.get(container.name, {}).get('image')
                if not new_image:
                    continue
                container.image = new_image
                LOG.info('container %s new image: %s',
                         container.name, container.image)

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
            raise exceptions.InvalidRequest(f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.Pod.from_object(pod).__dict__
        elif fmt == 'yaml':
            result = objects.Pod.to_yaml(pod)
        return {'pod': result}

    @application.with_response(return_code=204)
    def delete(self, name):
        context = self.get_context()
        LOG.debug('options request')
        api.CLIENT.delete_pod(name, ns=context.namespace)


@registry_route(r'/service')
class Services(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_service(ns=context.namespace)
        return {'services': [item.__dict__ for item in items]}


@registry_route(r'/service/(.+)')
class Service(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self, name):
        context = self.get_context()
        pod = api.CLIENT.get_service(name, ns=context.namespace)
        fmt = self.get_argument('format', 'json')
        if fmt and fmt not in ['json', 'yaml']:
            raise exceptions.InvalidRequest(f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.Pod.from_object(pod).__dict__
        elif fmt == 'yaml':
            result = objects.Service.to_yaml(pod)
        return {'service': result}


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
        items = api.CLIENT.list_job(ns=context.namespace)
        return {'jobs': [item.__dict__ for item in items]}


@registry_route(r'/configmap')
class ConfigMaps(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_configmap(ns=context.namespace)
        return {'configmaps': [item.__dict__ for item in items]}


@registry_route(r'/configmap/(.+)')
class ConfigMap(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self, name):
        context = self.get_context()

        fmt = self.get_argument('format', 'json')
        configmap = api.CLIENT.get_configmap(name, ns=context.namespace)
        if fmt and fmt not in ['json', 'yaml']:
            raise exceptions.InvalidRequest(f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.ConfigMap.from_object(configmap,
                                                   detail=True).__dict__
        elif fmt == 'yaml':
            result = objects.ConfigMap.to_yaml(configmap)
        return {'configmap': result}


@registry_route(r'/secret')
class Secrets(wsgi.RequestContext, ObjectMixin):

    @utils.response
    def get(self):
        context = self.get_context()
        items = api.CLIENT.list_secret(ns=context.namespace)
        return {'secrets': [item.__dict__ for item in items]}


@registry_route(r'/secret/(.+)')
class Secret(wsgi.RequestContext, ObjectMixin):
 
    @utils.response
    def get(self, name):
        context = self.get_context()
        result = self._get_obj(
            api.CLIENT.get_secret(name, ns=context.namespace),
            objects.Secret,
            fmt=self.get_argument('format', 'json'),
            detail=True
        )
        return {'secret': result}


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
            raise exceptions.InvalidRequest('pod and command must set')
        result = api.CLIENT.exec_on_pod(data.get('pod'), data.get('command'),
                                        ns=context.namespace,
                                        container=data.get('container'))
        return {'exec': result}

    @utils.register_action('addExecHistory')
    def _action_add_exec_history(self, context, data):
        global EXEC_HOSTORY

        exec = data.get('exec', '').strip()
        if not exec:
            raise exceptions.InvalidRequest('exec is empty')
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

    @utils.register_action('createWorkload')
    def _action_create_workload(self, context, data):
        # sourcery skip: raise-from-previous-error
        workload_doc = data.get('workload')
        if not workload_doc:
            raise exceptions.InvalidYaml()

        with fs.make_temp_file(workload_doc) as file:
            LOG.debug('template file: %s', file)
            try:
                api.CLIENT.create_workload(file)
            except AttributeError:
                raise exceptions.InvalidYaml()
            except exceptions.KindNotFound as e:
                raise exceptions.InvalidRequest(str(e))


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
