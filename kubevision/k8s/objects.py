from dataclasses import dataclass


@dataclass
class Node:
    name: str
    ready: str
    labels: list
    internal_ip: str
    kernel_version: str
    os_image: str
    container_runtime_version: str


@dataclass
class Namespace:
    name: str
    status: str
    labels: list


@dataclass
class Deployment:
    name: str
    replicas: int
    ready_replicas: int
    available_replicas: int
    labels: list
    images: list
    containers: list


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


@dataclass
class Pod:
    name: str
    labels: list
    node_name: str
    node_selector: dict
    host_ip: str
    pod_ip: str
    containers: list

    @classmethod
    def from_object(cls, obj):
        name = obj.metadata.name
        labels = obj.metadata.labels
        host_ip = obj.status.host_ip
        pod_ip = obj.status.pod_ip
        node_name = obj.spec.node_name
        node_selector = obj.spec.node_selector
        containers = []
        for container in obj.spec.containers:
            containers.append({
                'name': container.name,
                'image': container.image,
                'command': container.command
            })
        return Pod(name=name, labels=labels, node_name=node_name,
                   node_selector=node_selector, host_ip=host_ip,
                   pod_ip=pod_ip, containers=containers)