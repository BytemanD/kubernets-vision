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
