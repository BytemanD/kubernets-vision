import logging
import pathlib

from kubernetes import client, config
from kubernetes.client.models import v1_daemon_set

from kubevision.common import conf
from kubevision.k8s import objects
from kubevision.common import constants
from kubevision.common import exceptions

CONF = conf.CONF
LOG = logging.getLogger(__name__)

CLIENT = None


class ClientWrapper(object):

    def __init__(self):
        self.api = client.CoreV1Api()
        self.apps_api = client.AppsV1Api()

    def list_namespace(self):
        return [
            objects.Namespace.from_object(obj)
            for obj in self.api.list_namespace().items
        ]

    def list_node(self, node=None):
        nodes = [self.get_node(node)] if node else self.api.list_node().items
        return [objects.Node.from_object(node)for node in nodes]

    def get_node(self, name):
        return self.api.read_node(name)

    def delete_node_label(self, name, label):
        node = self.get_node(name)
        if not node:
            raise exceptions.NodeNotFound(node=name)
        if label not in node.metadata.labels:
            raise exceptions.NodeLabelNotFound(node=name, label=label)
        del node.metadata.labels[label]
        self.api.replace_node(name, node)

    def add_node_label(self, name, labels):
        node = self.get_node(name)
        if not node:
            raise exceptions.NodeNotFound(node=name)
        for key, value in labels.items():
            if key in node.metadata.labels:
                raise exceptions.NodeLabelExists(node=name, label=key)
            node.metadata.labels[key] = value or ''

        self.api.replace_node(name, node)

    def _get_container_runtime_version(self, node_info):
        return node_info.container_runtime_version

    def _get_node_ready_status(self, node):
        for condition in node.status.conditions or []:
            if condition.type == 'Ready':
                return condition.status

    def _get_node_internal_ip(self, node):
        return next(
            (
                address.address
                for address in node.status.addresses or []
                if address.type == 'InternalIP'
            ),
            None,
        )

    def list_deploy(self, ns=constants.DEFAULT_NAMESPACE):
        return [
            objects.Deployment.from_object(obj)
            for obj in self.apps_api.list_namespaced_deployment(ns).items
        ]

    def _get_node_selector(self, daemonset: v1_daemon_set.V1DaemonSet):
        try:
            return daemonset.spec.template.spec.node_selector
        except AttributeError as e:
            LOG.warn(e)
            return {}

    def _get_selector(self, daemonset: v1_daemon_set.V1DaemonSet):
        try:
            return daemonset.spec.selector.match_labels
        except AttributeError as e:
            LOG.warn(e)
            return {}

    def list_daemonset(self, ns=constants.DEFAULT_NAMESPACE):
        return [
            objects.DaemonSet.from_object(obj)
            for obj in self.apps_api.list_namespaced_daemon_set(ns).items
        ]

    def get_daemonset(self, name, ns=constants.DEFAULT_NAMESPACE):
        return self.apps_api.read_namespaced_daemon_set(name, ns)

    def list_pod(self, ns=constants.DEFAULT_NAMESPACE):
        items = []
        for obj in self.api.list_namespaced_pod(ns).items:
            LOG.info(obj)
            items.append(objects.Pod.from_object(obj))
        return items


def init(kube_config: pathlib.Path):
    global CLIENT

    if isinstance(kube_config, str):
        kube_config = pathlib.Path(kube_config)

    if not kube_config.exists():
        raise exceptions.KubeConfigNotExists(file=str(kube_config))

    config.kube_config.load_kube_config(config_file=str(kube_config))

    CLIENT = ClientWrapper()
