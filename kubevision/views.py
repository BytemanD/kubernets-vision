import json
import logging
import yaml

from tornado import web

from kubevision.common import conf
from kubevision.common import constants
from kubevision.common import exceptions
from kubernetes.client import exceptions as client_exc
from kubevision.common import utils
from kubevision.k8s import api
from kubevision.k8s import objects

LOG = logging.getLogger(__name__)
CONF = conf.CONF

CONF_DB_API = None
RUN_AS_CONTAINER = False
ROUTES = []


def registry_route(url):

    def registry(cls):
        global ROUTES

        ROUTES.append((url, cls))
        return cls
    return registry


class BaseReqHandler(web.RequestHandler):

    def set_default_headers(self):
        super().set_default_headers()
        if CONF.enable_cross_domain:
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Access-Control-Allow-Headers', '*')
            self.set_header('Access-Control-Allow-Max-Age', 1000)
            self.set_header('Access-Control-Allow-Methods',
                            'GET, POST, PUT, DELETE, PATCH, OPTIONS')

    def return_resp(self, status, data):
        self.set_status(status)
        self.finish(data)

    def _get_body(self):
        return json.loads(self.request.body)

    def set_default_headers(self):
        super().set_default_headers()
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Methods',
                        'GET, POST, PUT, DELETE, OPTIONS')

    def _get_namespace(self):
        return self.get_argument('namespace', constants.DEFAULT_NAMESPACE)

    @utils.with_response(return_code=204)
    def options(self, *args, **kwargs):
        LOG.debug('options request')


class ObjectMixin(object):

    @classmethod
    def to_yaml(cls, obj):
        # TODO
        # move this code to objects
        obj_dict = obj.to_dict()
        metadata = obj_dict.get('metadata')

        if 'creation_timestamp' in metadata:
            metadata['creation_timestamp'] = metadata.get('creation_timestamp').strftime('%Y-%m-%d %H:%M:%S')
        if 'managed_fields' in metadata:
            metadata['managed_fields'] = None

        status = obj_dict.get('status')
        if 'conditions' in status:
            for condition in status.get('conditions') or []:
                cls._format_time(condition, 'last_heartbeat_time')
                cls._format_time(condition, 'last_transition_time')

        return yaml.dump(obj_dict)

    @staticmethod
    def _format_time(obj, key, str_format='%Y-%m-%d %H:%M:%S'):
        if not hasattr(obj, key):
            return
        setattr(obj, key, getattr(obj, key).strftime(str_format))


@registry_route(r'/')
class Index(BaseReqHandler):

    def get(self):
        if CONF.index_redirect:
            self.redirect(CONF.index_redirect)
        else:
            self.redirect('index.html')


@registry_route(r'/.+\.html')
class Html(BaseReqHandler):

    def get(self):
        try:
            self.render(self.request.path[1:])
        except FileNotFoundError:
            self.set_status(404)
            self.finish({'error': f'{self.request.path[1:]} not found'})


@registry_route(r'/config.json')
class ConfigJson(BaseReqHandler):

    def get(self):
        try:
            self.render(self.request.path[1:])
        except FileNotFoundError:
            self.set_status(404)
            self.finish({'error': f'{self.request.path[1:]} not found'})


@registry_route(r'/version')
class ConfigJson(BaseReqHandler):

    @utils.with_response()
    def get(self):
        return {'version': {'backend': utils.get_version()}}


@registry_route(r'/node')
class Nodes(BaseReqHandler):

    @utils.response
    def get(self):
        items = api.CLIENT.list_node()
        return {'nodes': [item.__dict__ for item in items]}


@registry_route(r'/node/(.*)')
class Node(BaseReqHandler, ObjectMixin):

    @utils.response
    def get(self, name):
        node = api.CLIENT.get_node(name)
        return {'node': self.to_yaml(node)}


@registry_route(r'/namespace')
class Namespaces(BaseReqHandler):

    @utils.response
    def get(self):
        namespaces = api.CLIENT.list_namespace()
        return {'namespaces': [item.__dict__ for item in namespaces]}


@registry_route(r'/namespace/(.+)')
class Namespace(BaseReqHandler, ObjectMixin):

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
class Deployments(BaseReqHandler):

    @utils.response
    def get(self):
        items = api.CLIENT.list_deploy(ns=self._get_namespace())
        return {'deployments': [item.__dict__ for item in items]}


@registry_route(r'/daemonset')
class Daemonsets(BaseReqHandler):

    @utils.response
    def get(self):
        LOG.info('namespace is %s', self._get_namespace())
        items = api.CLIENT.list_daemonset(ns=self._get_namespace())
        return {'daemonsets': [item.__dict__ for item in items]}


@registry_route(r'/deployment/(.+)')
class Deployment(BaseReqHandler, ObjectMixin):

    @utils.response
    def get(self, name):
        deploy = api.CLIENT.get_deploy(name, ns=self._get_namespace())
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
        api.CLIENT.delete_deploy(name, ns=self._get_namespace())


@registry_route(r'/daemonset/(.+)')
class Daemonset(BaseReqHandler, ObjectMixin):

    @utils.response
    def get(self, name):
        daemonset = api.CLIENT.get_daemonset(name)
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
        api.CLIENT.delete_daemonset(daemonset, ns=self._get_namespace())

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
        data = self._get_body().get('daemonset', {})
        force = data.get('force', False)
        containers = data.get('containers', {})
        ds = api.CLIENT.get_daemonset(daemonset, ns=self._get_namespace())
        if containers:
            for container in ds.spec.template.spec.containers:
                new_image =  containers.get(container.name, {}).get('image')
                if not new_image:
                    continue
                container.image = new_image
                LOG.info('container %s new image: %s', container.name, container.image)

        if force:
            # TODO
            api.CLIENT.replace_daemonset(daemonset, ds, ns=self._get_namespace(), _request_timeout=0)
        else:
            api.CLIENT.replace_daemonset(daemonset, ds, ns=self._get_namespace())
        return {}


@registry_route(r'/pod')
class Pods(BaseReqHandler):

    @utils.response
    def get(self):
        items = api.CLIENT.list_pod(ns=self._get_namespace())
        return {'pods': [item.__dict__ for item in items]}


@registry_route(r'/pod/(.+)')
class Pod(BaseReqHandler, ObjectMixin):

    @utils.response
    def get(self, name):
        pod = api.CLIENT.get_pod(name, ns=self._get_namespace())
        fmt = self.get_argument('format', 'json')
        if fmt and fmt not in ['json', 'yaml']:
            raise exceptions.ApiException(400, f'format {fmt} is invalid')
        if not fmt or fmt == 'json':
            result = objects.Pod.from_object(pod).__dict__
        elif fmt == 'yaml':
            result = self.to_yaml(pod)
        return {'pod': result}

    @utils.with_response(return_code=204)
    def delete(self, daemonset):
        LOG.debug('options request')
        api.CLIENT.delete_daemonset(daemonset, ns=self._get_namespace())


@registry_route(r'/action')
class Action(BaseReqHandler):

    @utils.response
    def post(self):
        body = self._get_body()
        if 'deleteLabel' in body.keys():
            data = body.get('deleteLabel')
            self.delete_label(data.get('kind'), data.get('name'),
                              data.get('label'))
        elif 'addLabel' in body.keys():
            data = body.get('addLabel')
            self.add_label(data.get('kind'), data.get('name'),
                           data.get('labels'))

    def delete_label(self, kind, name, label):
        if kind == 'node':
            api.CLIENT.delete_node_label(name, label)

    def add_label(self, kind, name, labels):
        """Add Lable

        Args:
            kind (string): resource kind
            name (string): resource name
            labels (lables): dict, e.g. {key1: value1}
        """
        if kind == 'node':
            api.CLIENT.add_node_label(name, labels)


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
