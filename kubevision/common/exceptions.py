from tornado import web

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


class NodeLabelExists(exs.BaseException):
    _msg = 'Label {label} exists in {node}'


class KindNotFound(exs.BaseException):
    _msg = 'Kind not found'


class NotSupportKind(exs.BaseException):
    _msg = 'Not support kind: {kind}'


class ApiException(web.HTTPError):

    def __init__(self, status, msg, reason=None):
        super().__init__(status, msg, reason=reason)


class InvalidYaml(ApiException):

    def __init__(self):
        super().__init__(400, 'Invalid yaml')


class InvalidRequest(ApiException):

    def __init__(self, reason):
        super().__init__(400, f'Invalid request, {reason}')
