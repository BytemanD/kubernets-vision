import os
import socket
import logging

from easy2use.globals import cfg
from kubevision.common import constants

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
DEFAULT_HOST = socket.gethostname()


default_options = [
    cfg.BooleanOption('debug', default=False),
    cfg.Option('log_file', default=None),
    cfg.IntOption('port', default=8091),
    cfg.IntOption('workers', default=None),
    cfg.Option('data_path', default='/etc/kubevision'),
    cfg.BooleanOption('enable_cross_domain', default=False),
    cfg.Option('index_redirect', default=None),
]

k8s_options = [
    cfg.Option('kube_config', default=constants.DEFAULT_KUBE_CONFIG),
]

web_options = [
    cfg.ListOption(name='stylesheet', default=None),
]

def load_configs():
    for file in constants.DEFAULT_CONF_FILES:
        if not os.path.exists(file):
            continue
        LOG.info('Load config file from %s', file)
        CONF.load(file)
        break
    else:
        LOG.warning('config file not found')


CONF.register_opts(default_options)
CONF.register_opts(k8s_options, group='k8s')
CONF.register_opts(web_options, group='web')
