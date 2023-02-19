import logging

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
        items = []
        for obj in self.api.list_namespace().items:
            items.append(objects.Namespace(
                name=obj.metadata.name,
                status=obj.status.phase,
                labels=obj.metadata.labels or [],
            ))
        return items

    def list_node(self, ns=constants.DEFAULT_NAMESPACE):
        items = []
        for obj in self.api.list_node().items:
            # import pdb; pdb.set_trace()
            items.append(objects.Node(
                name=obj.metadata.name,
                ready=self._get_node_ready_status(obj),
                labels=obj.metadata.labels or [],
                internal_ip=self._get_node_internal_ip(obj),
                kernel_version=obj.status.node_info.kernel_version,
                os_image=obj.status.node_info.os_image,
                container_runtime_version=self._get_container_runtime_version(
                    obj.status.node_info)
            ))
        return items

    def get_node(self, name):
        for obj in self.api.list_node().items:
            if obj.metadata.name == name:
                return obj

    def replace_node(self, name, node):
        self.api.replace_node(name, body=node)

    def delete_node_label(self, name, label):
        node = self.get_node(name)
        if not node:
            raise exceptions.NodeNotFound(node=name)
        if label not in node.metadata.labels:
            raise exceptions.NodeLabelNotFound(node=name, label=label)
        del node.metadata.labels[label]
        self.api.replace_node(name, node)

    def _get_container_runtime_version(self, node_info):
        return node_info.container_runtime_version

    def _get_node_ready_status(self, node):
        for condition in node.status.conditions or []:
            if condition.type == 'Ready':
                return condition.status

    def _get_node_internal_ip(self, node):
        for address in node.status.addresses or []:
            if address.type == 'InternalIP':
                return address.address
        return None

    def list_deploy(self, ns=constants.DEFAULT_NAMESPACE):
        items = []
        for obj in self.apps_api.list_namespaced_deployment(ns).items:
            # import pdb;  pdb.set_trace()
            items.append(objects.Deployment(
                name=obj.metadata.name,
                replicas=obj.status.replicas,
                ready_replicas=obj.status.ready_replicas,
                available_replicas=obj.status.available_replicas,
                labels=obj.metadata.labels or [],
                images=self._get_images(obj),
                containers=self._get_containers(obj),
            ))
        return items

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

    def _get_images(self, deploy):
        try:
            return [cnt.image for cnt in deploy.spec.template.spec.containers]
        except AttributeError as e:
            LOG.warn(e)
            return {}

    def _get_containers(self, obj):
        try:
            return [cnt.name for cnt in obj.spec.template.spec.containers]
        except AttributeError as e:
            LOG.warn(e)
            return []

    def list_daemonset(self, ns=constants.DEFAULT_NAMESPACE):
        items = []
        for obj in self.apps_api.list_namespaced_daemon_set(ns).items:
            items.append(objects.DaemonSet(
                name=obj.metadata.name,
                number_ready=obj.status.number_ready,
                number_available=obj.status.number_available,
                current_number_scheduled=obj.status.current_number_scheduled,
                desired_number_scheduled=obj.status.desired_number_scheduled,
                labels=obj.metadata.labels or [],
                node_selector=self._get_node_selector(obj),
                selector=self._get_selector(obj),
                images=self._get_images(obj),
                containers=self._get_containers(obj),
            ))
        return items

    def list_pod(self, ns=constants.DEFAULT_NAMESPACE):
        items = []
        for obj in self.api.list_namespaced_pod(ns).items:
            # import pdb;  pdb.set_trace()
            items.append(objects.Pod(
                name=obj.metadata.name,
            ))
        return items

    def delete_label(self):
        self.api.delete


def init(config_file=None):
    global CLIENT

    config.kube_config.load_kube_config(
        config_file=config_file or '/root/.kube/config')

    CLIENT = ClientWrapper()
