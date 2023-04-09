from pbr import version
import functools
import logging
import requests

from kubernetes.client import exceptions

from easy2use.common import pkg

from kubevision.common import constants
from kubevision.common import exceptions as comm_exc
from kubevision.common.i18n import _


LOG = logging.getLogger(__name__)


def get_version():
    info = version.VersionInfo(constants.NAME)
    return info.release_string()


def check_last_version():
    try:
        releases = requests.get(constants.RELEASES_API).json()
    except Exception as e:
        LOG.error('Check releases failed, %s', e)
        return

    if not releases:
        LOG.info('No release found.')
        return
    current_version = get_version()
    LOG.debug(_('Current version is: %s'), current_version)
    latest = releases[0]
    LOG.debug(_('Latest release version: %s'), latest.get('tag_name'))

    v1 = pkg.PackageVersion(current_version)
    v2 = pkg.PackageVersion(latest.get('tag_name'))
    if v1 >= v2:
        return
    asset = latest.get('assets')[0] if latest.get('assets') else None
    if not asset:
        LOG.error('assets not found')
        return
    download_url = asset.get("browser_download_url")
    return {'version': '.'.join(v2.version), 'download_url': download_url}


def check_last_image_version():
    try:
        tags = requests.get(constants.IMAGE_TAGS_API).json().get('results')
    except Exception as e:
        LOG.error('get tags failed, %s', e)
        return

    if not tags:
        LOG.info('no repository tags found.')
        return
    current_version = get_version()
    LOG.debug(_('Current version is: %s'), current_version)

    v1 = pkg.PackageVersion(current_version)

    latest_version = v1
    for tag in tags:
        if tag.get('name') == 'latest':
            continue
        v2 = pkg.PackageVersion(tag.get('name'))
        if v2 > latest_version:
            latest_version = v2

    if latest_version > v1:
        version_string = '.'.join(latest_version.version)
        return {
            'version': version_string,
            'pull_url': f'fjboy/{constants.NAME}:${version_string}'
        }


def response(func):

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            resp = func(self, *args, **kwargs)
        except exceptions.ApiException as e:
            LOG.exception(e)
            resp = e.status, e.body or e.reason
        except comm_exc.ApiException as ex:
            resp = ex.status_code, {'message': ex.log_message}
        except Exception as e:
            LOG.exception(e)
            resp = 500, f'Internal Server error: {str(e)}'
        if isinstance(resp, tuple):
            status, body = resp
        else:
            status = 200
            body = resp
        self.set_status(status)
        self.finish(body)

    return wrapper


# TODO: move is to easy2use
def with_response(return_code=200):

    def _response(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                resp = func(self, *args, **kwargs)
            except Exception as e:
                LOG.exception(e)
                resp = 500, f'Internal Server error: {str(e)}'
            if isinstance(resp, tuple):
                status, body = resp
            else:
                status = return_code
                body = resp
            self.set_status(status)
            self.finish(body)

        return wrapper

    return _response


def parse_datetime(date_obj, str_format='%Y-%m-%d %H:%M:%S'):
    return date_obj and date_obj.strftime(str_format) or None


def format_time(obj, key, str_format='%Y-%m-%d %H:%M:%S'):
    if not hasattr(obj, key):
        return
    if not getattr(obj, key):
        return
    setattr(obj, key, parse_datetime(getattr(obj, key)))


def get_version():
    info = version.VersionInfo(constants.NAME)
    return info.release_string()
