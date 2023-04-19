import json
import logging
import inspect
from tornado import web

from kubevision.common import conf
from kubevision.common import constants
from kubevision.common import exceptions
from kubevision.common import utils
from kubevision.k8s import objects

LOG = logging.getLogger(__name__)
CONF = conf.CONF


class BaseReqHandler(web.RequestHandler):

    def set_default_headers(self):
        super().set_default_headers()
        if CONF.enable_cross_domain:
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Access-Control-Allow-Headers', '*')
            self.set_header('Access-Control-Allow-Max-Age', 1000)
            self.set_header('Access-Control-Allow-Methods',
                            'GET, POST, PUT, DELETE, PATCH, OPTIONS')

    def return_resp(self, status, data):
        self.set_status(status)
        self.finish(data)

    def _get_body(self):
        return json.loads(self.request.body)

    @utils.with_response(return_code=204)
    def options(self, *args, **kwargs):
        LOG.debug('options request')


class RequestContext(BaseReqHandler):
    NAMESPACE = 'X-Namespace'

    def _get_header(self, header):
        return self.request.headers.get(header, constants.DEFAULT_NAMESPACE)

    def get_context(self):
        ctx = objects.Context(
            namespace=self._get_header(self.NAMESPACE),
        )
        LOG.debug('request context is %s', ctx)
        return ctx


class BaseAction(RequestContext):

    def _get_function(self, body):
        found_func = None
        for name, func in inspect.getmembers(self, inspect.ismethod):
            if not hasattr(func, 'wsgi_action') or \
               not name.startswith('_action_') or \
               func.wsgi_action not in body.keys():
                continue
            found_func = func
            break
        if not found_func:
            raise exceptions.ApiException(400, 'not such action')
        LOG.info('found bound method %s', found_func)
        return found_func

    @utils.response
    def post(self):
        body = self._get_body()
        found_func = self._get_function(body)
        return found_func(self.get_context(), body.get(found_func.wsgi_action))
