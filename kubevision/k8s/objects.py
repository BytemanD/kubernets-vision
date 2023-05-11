from dataclasses import dataclass
import logging
import yaml

from kubernetes.client.models import v1_daemon_set
from kubernetes.client.models import v1_cron_job

from kubevision.common import utils

LOG = logging.getLogger(__name__)


def get_images(obj):
    try:
        return [cnt.image for cnt in obj.spec.template.spec.containers]
    except AttributeError as e:
        LOG.warn(e)
        return {}


def get_containers(obj):
    if isinstance(obj, v1_cron_job.V1CronJob):
        template = obj.spec.job_template.spec.template
    else:
        template = obj.spec.template
    try:
        return [
            {'name': cnt.name, 'command': cnt.command, 'args': cnt.args,
             'image': cnt.image} for cnt in template.spec.containers
        ]
    except AttributeError as e:
        LOG.warn(e)
        return []


def get_init_containers(obj):
    try:
        return [
            {'name': cnt.name, 'command': cnt.command,  'args': cnt.args,
             'image': cnt.image
             } for cnt in obj.spec.template.spec.init_containers or []]
    except AttributeError as e:
        LOG.warn(e)
        return []


def get_container_state(container_state):
    waiting = container_state.waiting
    return {
        'running': container_state.running is not None,
        'terminated': container_state.terminated is not None,
        'waiting': waiting and waiting.to_dict() or None,
    }


def get_container_statuses(obj):
    return [
        {
            'name': status.name,
            'last_state': get_container_state(status.last_state),
            'ready': status.ready,
            'state': get_container_state(status.state),
        }
        for status in obj.status.container_statuses or []
    ]


def get_deletion(obj):
    return {
        'grace_period_seconds': obj.metadata.deletion_grace_period_seconds,
        'timestamp': utils.parse_datetime(obj.metadata.deletion_timestamp),
    }


def get_creation(obj):
    return {
        'timestamp': utils.parse_datetime(obj.metadata.creation_timestamp),
    }


def get_node_selector(obj):
    try:
        return obj.spec.template.spec.node_selector
    except AttributeError as e:
        LOG.warn(e)
        return {}


def get_selector(obj):
    try:
        return obj.spec.selector.match_labels
    except AttributeError as e:
        LOG.warn(e)
        return {}


def get_phase(obj):
    return obj.status.phase


@dataclass
class Context:
    namespace: str

    def __str__(self):
        return f'<namepace: {self.namespace} >'


@dataclass
class BaseDataObject:
    name: str
    creation: str

    @staticmethod
    def to_yaml(obj):
        obj_dict = obj.to_dict()
        metadata = obj_dict.get('metadata')

        utils.format_time(metadata, 'creation_timestamp')
        if 'managed_fields' in metadata:
            metadata['managed_fields'] = None

        status = obj_dict.get('status')
        if status and 'conditions' in status:
            for condition in status.get('conditions') or []:
                utils.format_time(condition, 'last_heartbeat_time')
                utils.format_time(condition, 'last_transition_time')

        return yaml.dump(obj_dict)


@dataclass
class Node(BaseDataObject):
    ready: str
    labels: list
    internal_ip: str
    kernel_version: str
    os_image: str
    container_runtime_version: str
    capacity: dict
    allocatable: dict

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
            name=obj.metadata.name, creation=get_creation(obj),
            ready=cls.get_node_ready_status(obj),
            labels=obj.metadata.labels or [],
            internal_ip=cls.get_node_internal_ip(obj),
            kernel_version=obj.status.node_info.kernel_version,
            os_image=obj.status.node_info.os_image,
            container_runtime_version=cls.get_container_runtime_version(
                obj.status.node_info),
            capacity=obj.status.capacity,
            allocatable=obj.status.allocatable,
        )


@dataclass
class Namespace(BaseDataObject):
    status: str
    labels: list

    @classmethod
    def from_object(cls, obj):
        return cls(name=obj.metadata.name, creation=get_creation(obj),
                   status=obj.status.phase,
                   labels=obj.metadata.labels or [])


@dataclass
class Deployment(BaseDataObject):
    name: str
    replicas: int
    ready_replicas: int
    available_replicas: int
    labels: list
    images: list
    containers: list
    init_containers: list

    @classmethod
    def from_object(cls, obj):
        return cls(
            name=obj.metadata.name, creation=get_creation(obj),
            replicas=obj.status.replicas or 0,
            ready_replicas=obj.status.ready_replicas or 0,
            available_replicas=obj.status.available_replicas or 0,
            labels=obj.metadata.labels or [],
            images=get_images(obj),
            containers=get_containers(obj),
            init_containers=get_init_containers(obj),
        )


@dataclass
class DaemonSet(BaseDataObject):
    number_ready: int
    number_available: int
    current_number_scheduled: int
    desired_number_scheduled: int
    labels: list
    node_selector: dict
    selector: dict
    images: list
    containers: list
    init_containers: list

    @classmethod
    def from_object(cls, obj):
        return cls(
            name=obj.metadata.name, creation=get_creation(obj),
            number_ready=obj.status.number_ready,
            number_available=obj.status.number_available,
            current_number_scheduled=obj.status.current_number_scheduled,
            desired_number_scheduled=obj.status.desired_number_scheduled,
            labels=obj.metadata.labels or [],
            node_selector=get_node_selector(obj),
            selector=get_selector(obj),
            images=get_images(obj),
            containers=get_containers(obj),
            init_containers=get_init_containers(obj),
        )


@dataclass
class StatusfulSet(BaseDataObject):
    labels: list
    node_selector: dict
    selector: dict
    images: list
    containers: list
    init_containers: list

    @classmethod
    def from_object(cls, obj):
        pod_ip = obj.status.pod_ip
        node_name = obj.spec.node_name
        node_selector = obj.spec.node_selector
        containers = [
            {'name': container.name, 'image': container.image,
             'command': container.command}
            for container in obj.spec.containers
        ]
        container_statuses = get_container_statuses(obj)
        return cls(
            name=obj.metadata.name,
            creation=get_creation(obj),
            labels=obj.metadata.labels,
            node_name=node_name,
            node_selector=node_selector,
            pod_ip=pod_ip,
            containers=containers,
            container_statuses=container_statuses,
            deletion=get_deletion(obj),
        )


@dataclass
class CronJob(BaseDataObject):
    labels: list
    node_selector: dict
    selector: dict
    containers: list

    @classmethod
    def from_object(cls, obj):
        return cls(
            name=obj.metadata.name,
            creation=get_creation(obj),
            labels=obj.metadata.labels or [],
            node_selector=get_node_selector(obj),
            selector=get_selector(obj),
            containers=get_containers(obj),
        )


@dataclass
class Job(BaseDataObject):
    labels: list
    node_selector: dict
    selector: dict
    containers: list

    @classmethod
    def from_object(cls, obj):
        return Job(
            name=obj.metadata.name,
            creation=get_creation(obj),
            labels=obj.metadata.labels or [],
            node_selector=get_node_selector(obj),
            selector=get_selector(obj),
            containers=get_containers(obj),
        )


@dataclass
class Service(BaseDataObject):
    type: str
    cluster_ip: str
    cluster_i_ps: list
    internal_traffic_policy: str
    ip_families: list
    ports: list

    @classmethod
    def from_object(cls, obj):
        return cls(
            name=obj.metadata.name,
            creation=get_creation(obj),
            type=obj.spec.type,
            cluster_ip=obj.spec.cluster_ip,
            cluster_i_ps=obj.spec.cluster_i_ps,
            internal_traffic_policy=obj.spec.internal_traffic_policy,
            ip_families=obj.spec.ip_families,
            ports=[port.to_dict() for port in obj.spec.ports],
        )


@dataclass
class Pod(BaseDataObject):
    labels: list
    node_name: str
    node_selector: dict
    host_ip: str
    pod_ip: str
    containers: list
    container_statuses: list
    deletion: dict
    phase: str

    @classmethod
    def from_object(cls, obj):
        name = obj.metadata.name
        labels = obj.metadata.labels
        host_ip = obj.status.host_ip
        pod_ip = obj.status.pod_ip
        node_name = obj.spec.node_name
        node_selector = obj.spec.node_selector
        containers = [{
            'name': container.name, 'image': container.image,
            'command': container.command,
            'image_pull_policy': container.image_pull_policy,
            'ports': [
                {'protocol': port.protocol, 'host_port': port.host_port,
                 'container_port': port.container_port}
                for port in container.ports or []
            ]
            } for container in obj.spec.containers
        ]
        container_statuses = get_container_statuses(obj)
        return Pod(
            name=name, creation=get_creation(obj),
            labels=labels, node_name=node_name,
            node_selector=node_selector, host_ip=host_ip,
            pod_ip=pod_ip, containers=containers,
            container_statuses=container_statuses,
            deletion=get_deletion(obj),
            phase=get_phase(obj),
        )


@dataclass
class ConfigMap(BaseDataObject):
    data_list: list
    data: dict

    @classmethod
    def from_object(cls, obj, detail=False):
        return cls(
            name=obj.metadata.name,
            creation=get_creation(obj),
            data_list=list(obj.data.keys()),
            data=detail and obj.data or {}
        )


@dataclass
class Secret(BaseDataObject):
    data_list: list
    data: dict

    @classmethod
    def from_object(cls, obj, detail=False):
        return cls(
            name=obj.metadata.name,
            creation=get_creation(obj),
            data_list=list(obj.data.keys()),
            data=detail and obj.data or {},
        )
