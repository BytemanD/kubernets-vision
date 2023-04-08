import shutil
import os

from easy2use import fs
from easy2use.common import msgfmt

kubevision = 'kubevision'
I18N_DIR = 'i18n'


def setup_hook(config):
    # Tell distutils not to put the data_files in platform-specific
    # installation locations.
    # Refer to the instructions in the openstack/horizon project
    # for scheme in install.INSTALL_SCHEMES.values():
    #     scheme['data'] = scheme['purelib']

    msgfmt.make_i18n(kubevision, I18N_DIR)
