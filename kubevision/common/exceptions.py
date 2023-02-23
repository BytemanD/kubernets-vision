

from easy2use.common import exceptions as exs


class KubeConfigNotExists(exs.BaseException):
    _msg = 'Kube config {file} is not exists'


class PipInstallFailed(exs.BaseException):
    _msg = 'Install {package} failed, cmd={}'


class NodeNotFound(exs.BaseException):
    _msg = 'Node {node} not found'


class NodeLabelNotFound(exs.BaseException):
    _msg = 'Label {label} not found in {node}'


class NodeLabelExists(exs.BaseException):
    _msg = 'Label {label} exists in {node}'
