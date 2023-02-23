import logging
import mimetypes
import os
import sys
import subprocess

from easy2use.downloader.urllib import driver
from easy2use.globals import cli
from easy2use.globals import log
from easy2use.system import OS
from easy2use import system
from easy2use.web import application

from kubevision.common import conf
from kubevision.common import constants
from kubevision.common import exceptions
from kubevision.common import utils
from kubevision.common.i18n import _
from kubevision.k8s import api
from kubevision import views

LOG = logging.getLogger(__name__)
CONF = conf.CONF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Version(cli.SubCli):
    NAME = 'version'

    def __call__(self, args):
        print(utils.get_version())


class Upgrade(cli.SubCli):
    NAME = 'upgrade'
    ARGUMENTS = [
        cli.Arg('-d', '--debug', action='store_true',
                help=_('Show debug message')),
        cli.Arg('-y', '--yes', action='store_true',
                help=_('answer yes for all questions')),
        cli.Arg('-c', '--cache', action='store_true',
                help=_('use cache if it is downloaded')),
        cli.Arg('--image', action='store_true',
                help=_('Check image version')),
    ]

    def __call__(self, args):
        if args.image:
            last_version = self.upgrade_from_image()
            return
        last_version = utils.check_last_version()
        if not last_version:
            print(_('The current version is the latest.'))
            return

        version = last_version.get('version')
        download_url = last_version.get('download_url')
        msg = f'\nA new {constants.NAME} release is available: ' \
              f'{version}\n' \
              f'Upgrade from:\n    {download_url}\n'
        print(msg)

        if not args.yes:
            while True:
                input_str = input(r'Upgrade now ? [y/n] ')
                if input_str == 'y':
                    break
                elif input_str == 'n':
                    return
                else:
                    print('Error, invalid input, must be y or n.')

        file_path = self.download(download_url, cache=args.cache)
        try:
            self.pip_install(file_path)
        except Exception as e:
            LOG.error('Install failed, error: %s', e)
            return
        print(_('Install success.'))
        print(_('Please execute the command below to restart kubevision:'))
        print('    systemctl restart kubevision')

    def upgrade_from_image(self):
        latest_version = utils.check_last_image_version()
        if not latest_version:
            print(_('The current version is the latest.'))
            return

        msg = f'{_("A new image is available:")} ' \
              f'{latest_version.get("version")}'
        print('\n' + msg + '\n')

    def pip_install(self, file_path, force=False):
        install_cmd = ['pip3', 'install', file_path]
        if force:
            install_cmd.append('--force-reinstall')
        LOG.info(_('start to install %s'), ' '.join(install_cmd))
        status, output = subprocess.getstatusoutput(' '.join(install_cmd))
        if status != 0:
            LOG.error(_('Install Output: %s'), output)
            raise exceptions.PipInstallFailed(package=file_path,
                                              cmd=' '.join(install_cmd))

    def download(self, url, cache=False):
        file_path = os.path.basename(url)
        tmp_dir = OS.is_windows() and os.getenv('TMP') or '/tmp'
        cached_file = os.path.join(tmp_dir, '/tmp')
        if cache and os.path.exists(cached_file):
            LOG.warning('use cache: %s', cached_file)
            return cached_file

        downloader = driver.Urllib3Driver(progress=True,
                                          cached_file=tmp_dir)
        LOG.info(_('download from %s'), url)
        downloader.download(url)
        LOG.info(_('download success'))
        return file_path


class KubeVisionApp(application.TornadoApp):

    def start(self, **kwargs):
        LOG.info('Staring server ...')
        super().start(**kwargs)


class Serve(cli.SubCli):
    NAME = 'serve'
    ARGUMENTS = log.get_args() + [
        cli.Arg('-p', '--port', type=int,
                help=_("Run serve with specified port")),
        cli.Arg('--develop', action='store_true',
                help=_("Run serve with develop mode")),
        cli.Arg('--container', action='store_true',
                help=_("Run serve with docker container")),
        cli.Arg('--kube-config',
                default=constants.DEFAULT_KUBE_CONFIG,
                help=f'{_("Kubernetes config file, default is")}: ' +
                     constants.DEFAULT_KUBE_CONFIG),
    ]

    def __call__(self, args):
        views.RUN_AS_CONTAINER = args.container
        if system.OS.is_windows():
            # NOTE(fjboy) For windows host, MIME type of .js file is
            # 'text/plain', so add this type before start http server.
            mimetypes.add_type('application/javascript', '.js')

        conf.load_configs()
        api.init(args.kube_config)

        template_path = os.path.join(ROOT, 'templates')
        static_path = os.path.join(ROOT, 'static')
        app = KubeVisionApp(views.get_routes(), develop=args.develop,
                            template_path=template_path,
                            static_path=static_path)
        app.start(port=args.port or CONF.port,
                  num_processes=CONF.workers)


def main():
    cli_parser = cli.SubCliParser(_('Kube Vision Command Line'),
                                  title=_('Subcommands'))
    cli_parser.register_clis(Version, Upgrade, Serve)
    cli_parser.call()


if __name__ == '__main__':
    sys.exit(main())
