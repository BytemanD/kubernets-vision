import logging
from dataclasses import dataclass

from kubernetes.client.models import v1_daemon_set

LOG = logging.getLogger(__name__)


def get_images(obj):
    try:
        return [cnt.image for cnt in obj.spec.template.spec.containers]
    except AttributeError as e:
        LOG.warn(e)
        return {}


def get_containers(obj):
    try:
        return [
            {'name': cnt.name,
             'command': cnt.command,
             'args': cnt.args,
             'image': cnt.image} for cnt in obj.spec.template.spec.containers
        ]
    except AttributeError as e:
        LOG.warn(e)
        return []


def get_container_state(container_state):
    return {
        'running': container_state.running != None,
        'terminated': container_state.terminated != None,
        'waiting': container_state.waiting.to_dict() if  container_state.waiting else None,
    }
    

def get_container_statuses(obj):
    container_statuses = []

    for status in obj.status.container_statuses or []:
        container_statuses.append({
            'name': status.name,
            'last_state': get_container_state(status.last_state),
            'ready': status.ready,
            'state': get_container_state(status.state)
        })
    # import pdb; pdb.set_trace()
    return container_statuses


@dataclass
class Node:
    name: str
    ready: str
    labels: list
    internal_ip: str
    kernel_version: str
    os_image: str
    container_runtime_version: str

    @classmethod
    def get_container_runtime_version(cls, node_info):
        return node_info.container_runtime_version

    @classmethod
    def get_node_ready_status(cls, node):
        for condition in node.status.conditions or []:
            if condition.type == 'Ready':
                return condition.status

    @classmethod
    def get_node_internal_ip(cls, node):
        return next(
            (
                address.address
                for address in node.status.addresses or []
                if address.type == 'InternalIP'
            ),
            None,
        )

    @classmethod
    def get_containers(cls, obj):
        try:
            return [cnt.name for cnt in obj.spec.template.spec.containers]
        except AttributeError as e:
            LOG.warn(e)
            return []

    @classmethod
    def from_object(cls, obj):
        return cls(
            name=obj.metadata.name,
            ready=cls.get_node_ready_status(obj),
            labels=obj.metadata.labels or [],
            internal_ip=cls.get_node_internal_ip(obj),
            kernel_version=obj.status.node_info.kernel_version,
            os_image=obj.status.node_info.os_image,
            container_runtime_version=cls.get_container_runtime_version(
                obj.status.node_info)
        )


@dataclass
class Namespace:
    name: str
    status: str
    labels: list

    @classmethod
    def from_object(cls, obj):
        return cls(name=obj.metadata.name, status=obj.status.phase,
                   labels=obj.metadata.labels or [])


@dataclass
class Deployment:
    name: str
    replicas: int
    ready_replicas: int
    available_replicas: int
    labels: list
    images: list
    containers: list

    @classmethod
    def from_object(cls, obj):
        return cls(
            name=obj.metadata.name,
            replicas=obj.status.replicas or 0,
            ready_replicas=obj.status.ready_replicas or 0,
            available_replicas=obj.status.available_replicas or 0,
            labels=obj.metadata.labels or [],
            images=get_images(obj),
            containers=get_containers(obj),
        )


@dataclass
class DaemonSet:
    name: str
    number_ready: int
    number_available: int
    current_number_scheduled: int
    desired_number_scheduled: int
    labels: list
    node_selector: dict
    selector: dict
    images: list
    containers: list

    @classmethod
    def get_node_selector(cls, daemonset: v1_daemon_set.V1DaemonSet):
        try:
            return daemonset.spec.template.spec.node_selector
        except AttributeError as e:
            LOG.warn(e)
            return {}

    @classmethod
    def get_selector(cls, daemonset: v1_daemon_set.V1DaemonSet):
        try:
            return daemonset.spec.selector.match_labels
        except AttributeError as e:
            LOG.warn(e)
            return {}

    @classmethod
    def from_object(cls, obj):
        return cls(
            name=obj.metadata.name,
            number_ready=obj.status.number_ready,
            number_available=obj.status.number_available,
            current_number_scheduled=obj.status.current_number_scheduled,
            desired_number_scheduled=obj.status.desired_number_scheduled,
            labels=obj.metadata.labels or [],
            node_selector=cls.get_node_selector(obj),
            selector=cls.get_selector(obj),
            images=get_images(obj),
            containers=get_containers(obj),
        )


@dataclass
class Pod:
    name: str
    labels: list
    node_name: str
    node_selector: dict
    host_ip: str
    pod_ip: str
    containers: list
    container_statuses: list

    @classmethod
    def from_object(cls, obj):
        name = obj.metadata.name
        labels = obj.metadata.labels
        host_ip = obj.status.host_ip
        pod_ip = obj.status.pod_ip
        node_name = obj.spec.node_name
        node_selector = obj.spec.node_selector
        containers = [
            {'name': container.name, 'image': container.image,
             'command': container.command}
            for container in obj.spec.containers
        ]
        container_statuses = get_container_statuses(obj)
        return Pod(name=name, labels=labels, node_name=node_name,
                   node_selector=node_selector, host_ip=host_ip,
                   pod_ip=pod_ip, containers=containers,
                   container_statuses=container_statuses)
