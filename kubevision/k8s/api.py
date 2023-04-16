import logging
import pathlib
import re

from kubernetes import client, config
from kubernetes.client.models import v1_daemon_set

from kubevision.common import conf
from kubevision.k8s import objects
from kubevision.common import constants
from kubevision.common import exceptions
from kubernetes.stream import stream

CONF = conf.CONF
LOG = logging.getLogger(__name__)

CLIENT = None
KUBE_CONFIG = None

UPPER_FOLLOWED_BY_LOWER_RE = re.compile('(.)([A-Z][a-z]+)')
LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE = re.compile('([a-z0-9])([A-Z])')


class ClientWrapper(object):

    def __init__(self):
        self.api = client.CoreV1Api()
        self.api_client = client.ApiClient()
        self.apps_api = client.AppsV1Api()
        self.version_api = client.VersionApi()
        self.batch_api = client.BatchV1Api()

    def list_namespace(self):
        return [
            objects.Namespace.from_object(obj)
            for obj in self.api.list_namespace().items
        ]
    def get_namespace(self, name):
        return self.api.read_namespace(name)

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

    def list_deploy(self, ns=None):
        return [
            objects.Deployment.from_object(obj)
            for obj in self.apps_api.list_namespaced_deployment(ns).items
        ]

    def get_deploy(self, name, ns=None):
        return self.apps_api.read_namespaced_deployment(
            name, ns or constants.DEFAULT_NAMESPACE)

    def delete_deploy(self, name, ns=None):
        return self.apps_api.delete_namespaced_deployment(
            name, ns or constants.DEFAULT_NAMESPACE)

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

    def list_daemonset(self, ns=None):
        return [
            objects.DaemonSet.from_object(obj)
            for obj in self.apps_api.list_namespaced_daemon_set(
                ns or constants.DEFAULT_NAMESPACE
            ).items
        ]

    def get_daemonset(self, name, ns=None):
        return self.apps_api.read_namespaced_daemon_set(
            name, ns or constants.DEFAULT_NAMESPACE)

    def delete_daemonset(self, name, ns=None):
        return self.apps_api.delete_namespaced_daemon_set(
            name, ns or constants.DEFAULT_NAMESPACE)

    def replace_daemonset(self, name, body, ns=None, **kwargs):
        LOG.info('replace ds %s', name)
        # self.apps_api.replace_namespaced_daemon_set(name, ns, body, **kwargs)
        return self.apps_api.replace_namespaced_daemon_set(
            name, ns or constants.DEFAULT_NAMESPACE, body,
            **kwargs)

    def patch_daemonset(self, name, body, ns=None, **kwargs):
        LOG.info('patch ds %s', name)
        self.apps_api.patch_namespaced_daemon_set(name, ns, body, field_manager='replace', force=True)
        return self.apps_api.patch_namespaced_daemon_set(
            name, ns or constants.DEFAULT_NAMESPACE, body,
            **kwargs)

    def list_pod(self, ns=None):
        return [
            objects.Pod.from_object(obj)
            for obj in self.api.list_namespaced_pod(
                ns or constants.DEFAULT_NAMESPACE
            ).items
        ]

    def get_pod(self, name, ns=None):
        return self.api.read_namespaced_pod(
            name, ns or constants.DEFAULT_NAMESPACE)

    def delete_pod(self, name, ns=None):
        return self.api.delete_namespaced_pod(
            name, ns or constants.DEFAULT_NAMESPACE)

    def get_pod_logs(self, name, ns=None, tail_lines=None, **kwargs):
        return self.api.read_namespaced_pod_log(
            name, ns or constants.DEFAULT_NAMESPACE,
            tail_lines=tail_lines,
            **kwargs)

    def exec_on_pod(self, name, command, ns=None, container=None, async_req=False, **kwargs):
        result = stream(self.api.connect_post_namespaced_pod_exec,
                        name, ns, command=['/bin/sh', '-c', command],
                        container=container, stdout=True, stderr=True, tty=False,
                        async_req=async_req,
                        **kwargs)
        return async_req and result.get() or result

    def list_service(self, ns=None):
        return [
            objects.Service.from_object(service)
            for service in self.api.list_namespaced_service(
                ns or constants.DEFAULT_NAMESPACE).items
        ] 

    def list_cron_job(self, ns=None):
        return [
            objects.CronJob.from_object(cron_job)
            for cron_job in self.batch_api.list_namespaced_cron_job(
                ns or constants.DEFAULT_NAMESPACE).items
        ]

    def list_job(self, ns=None):
        return [
            objects.Job.from_object(job)
            for job in self.batch_api.list_namespaced_job(
                ns or constants.DEFAULT_NAMESPACE).items
        ]

    def list_configmap(self, ns=None):
        return [
            objects.ConfigMap.from_object(obj)
            for obj in self.api.list_namespaced_config_map(
                ns or constants.DEFAULT_NAMESPACE
            ).items
        ]

    def get_version(self):
        return self.version_api.get_code()

    def get_cluster_info(self):
        config = get_config()
        return  {
            'config': {
                'host': config.host,
                'verify_ssl': config.verify_ssl,
            },
            'version': self.version_api.get_code().to_dict(),
            'current_context': get_current_context(),
        } 

    def create_workload(self, yaml_file):
        import yaml
        with open(yaml_file) as f:
            yaml_doc = yaml.safe_load(f)

        print(yaml_doc)
        kind = yaml_doc.get('kind')
        if not kind:
            raise exceptions.KindNotFound()

        kind = UPPER_FOLLOWED_BY_LOWER_RE.sub(r'\1_\2', kind)
        kind = LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE.sub(r'\1_\2', kind).lower()

        create_func = None
        create_with_namespce = False
        for api_client in [self.apps_api, self.api]:
            if hasattr(api_client, f'create_namespaced_{kind}'):
                create_func = getattr(api_client, f'create_namespaced_{kind}')
                create_with_namespce = True
                break
            elif hasattr(api_client, f'create_{kind}'):
                create_func = getattr(api_client)
                create_with_namespce = False
                break

        if not create_func:
            raise exceptions.NotSupportKind(kind=kind)
        if not create_with_namespce:
            return create_func(yaml_doc)

        namespace =yaml_doc.get(
            'metadata', {}).get('namespace', constants.DEFAULT_NAMESPACE)
        return create_func(namespace, yaml_doc)


def get_config():
    return config.kube_config.Configuration._default


def get_current_context():
    global KUBE_CONFIG

    _, context = config.list_kube_config_contexts(str(KUBE_CONFIG))
    return context


def get_host():
    return config.kube_config.Configuration._default.host


def init(kube_config: pathlib.Path):
    # sourcery skip: instance-method-first-arg-name
    global CLIENT, KUBE_CONFIG

    if isinstance(kube_config, str):
        kube_config = pathlib.Path(kube_config)

    if not kube_config.exists():
        raise exceptions.KubeConfigNotExists(file=str(kube_config))

    config.kube_config.load_kube_config(config_file=str(kube_config))

    KUBE_CONFIG = kube_config
    CLIENT = ClientWrapper()
    LOG.info('current context: %s', get_current_context())
