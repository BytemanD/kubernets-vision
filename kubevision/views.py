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
    def options(self):
        LOG.debug('options request')


class ObjectMixin(object):

    @classmethod
    def to_yaml(cls, obj):
        obj_dict = obj.to_dict()
        metadata = obj_dict.get('metadata')

        if 'creation_timestamp' in metadata:
            metadata['creation_timestamp'] = metadata.get('creation_timestamp').strftime('%Y-%m-%d %H:%M:%S')
        if 'managed_fields' in metadata:
            metadata['managed_fields'] = None

        status = obj_dict.get('status')
        if 'conditions' in status:
            for condition in status.get('conditions') or []:
                condition['last_heartbeat_time'] = condition.get('last_heartbeat_time').strftime('%Y-%m-%d %H:%M:%S')
                condition['last_transition_time'] = condition.get('last_transition_time').strftime('%Y-%m-%d %H:%M:%S')

        return yaml.dump(obj_dict)


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
class Namespace(BaseReqHandler):

    @utils.response
    def get(self):
        namespaces = api.CLIENT.list_namespace()
        return {'namespaces': [item.__dict__ for item in namespaces]}


@registry_route(r'/deployment')
class Deployment(BaseReqHandler):

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


@registry_route(r'/daemonset/(.+)')
class Daemonset(BaseReqHandler, ObjectMixin):

    @utils.response
    def get(self, name):
        daemonset = api.CLIENT.get_daemonset(name)
        fmt = self.get_argument('format', 'json')
        if not fmt or fmt == 'json':
            result = objects.DaemonSet.from_object(daemonset).__dict__
        elif fmt == 'yaml':
            result = self.to_yaml(daemonset)
        else:
            raise exceptions.ApiException(400, f'format {fmt} is invalid')

        return {'daemonset': result}


@registry_route(r'/pod')
class Pod(BaseReqHandler):

    @utils.response
    def get(self):
        items = api.CLIENT.list_pod(ns=self._get_namespace())
        return {'pods': [item.__dict__ for item in items]}


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
