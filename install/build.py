import argparse
import logging
import os
import shutil
import sys
import inspect
import functools
import json

from easy2use.command import shell

LOG_FORMAT = '%(asctime)s %(process)d %(levelname)-7s %(name)s:%(lineno)s ' \
             '%(message)s'
FILE_PATH = os.path.abspath(__file__)
INSTALL_DIR = os.path.dirname(FILE_PATH)

DOCKER, PODMAN = 'docker', 'podman'
CONTAINER_CMD = None

LOG = logging.getLogger(__name__)

step_num = 0

def log_step(func):
    func_doc = inspect.getdoc(func)
    step_title = func_doc and func_doc.split('\n')[0] or func.__name__

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global step_num

        step_num += 1
        LOG.info('[STEP-%s] %s', '{:0>2}'.format(step_num), step_title)
        return func(*args, **kwargs)

    return wrapper


class PyWebDockerBuilder(object):

    def __init__(self, backend, frontend, workspace=os.path.join('install'),
                 frontend_name=None, config_json=None, favicon=None,
                 no_cache=False, push_registry=None, push_as_latest=False):
        self.bacckend = backend
        self.frontend = frontend
        self.worspace = workspace
        self.bacckend_file = os.path.basename(self.bacckend)
        self.frontend_name = frontend_name or os.path.basename(self.frontend)
        self.config_json = config_json
        self.favicon = favicon
        self.no_cache = no_cache
        self.push_registry = push_registry or []
        self.push_as_latest = push_as_latest

    def get_build_resources(self):
        join_workspace_path = functools.partial(os.path.join, self.worspace)
        requirements = 'requirements.txt'
        return [
            (self.bacckend, join_workspace_path(self.bacckend_file)),
            (self.frontend, join_workspace_path(self.frontend_name)),
            (requirements, join_workspace_path(requirements)),
        ]

    @log_step
    def check_whl_file_and_version(self):
        '''检查 whl 文件和版本
        '''
        LOG.debug('----> whl file path: %s', self.bacckend)
        if not os.path.exists(self.bacckend):
            raise RuntimeError(f'whl file {self.bacckend} is not exists')
        if not os.path.isfile(self.bacckend):
            raise RuntimeError('invalid path %s, it must be a file')

        whl_name = os.path.basename(self.bacckend)
        whl_version = whl_name.split('-')[1]
        try:
            LOG.debug('----> whl version is %s', whl_version)
        except Exception as e:
            LOG.error(e)
            raise
        return whl_name, whl_version

    @log_step
    def check_frontend(self):
        '''检查前端项目目录
        '''
        if not os.path.exists(self.frontend):
            raise RuntimeError(f'frontend project {self.frontend} is not exists')

    @log_step
    def prepare_build_resources(self, resources):
        '''准备构建资源
        '''
        for resource in resources:
            src_path, dst_path = resource[0], resource[1]
            if os.path.exists(dst_path):
                LOG.debug('----> copy %s to %s', src_path, dst_path)
                if os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)
                else:
                    os.remove(dst_path)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy(src_path, dst_path)

    @log_step
    def update_config_json(self):
        """更新文件: config.json
        """
        if not self.config_json:
            LOG.warning('----> config.json file is None, skip')
            return
        config_json = os.path.join(self.worspace, self.frontend_name,
                                   self.config_json)
        if not os.path.exists(config_json):
            raise RuntimeError(f'file {config_json} not exists')
        LOG.warning('----> config.json file is %s', config_json)
        with open(config_json) as f:
            content = json.load(f)
            f.close()
        if 'backend_url' in content:
            content['backend_url'] = ''
        with open(config_json, 'w') as f:
            json.dump(content, f, indent=4)

    @property
    def favicon_file(self):
        return os.path.join(self.worspace, self.frontend_name, self.favicon)

    @log_step
    def update_favicon(self):
        """准备文件: favicon.ico
        """
        if not self.favicon:
            LOG.warning('----> favicon is None, skip')
            return
        favicon_file = self.favicon_file

        if not os.path.exists(favicon_file):
            raise RuntimeError(f'favicon file {favicon_file} not exists')
        shutil.move(favicon_file,
                    os.path.join(self.worspace, self.frontend_name,
                                 'static', 'favicon.ico'))

    @log_step
    def build_docker_image(self, name, version, backend, frontend):
        """构建 docker 镜像
        """
        os.chdir(self.worspace)
        LOG.debug('----> changed dir to %s', os.getcwd())

        for f in [backend, frontend]:
            if not os.path.exists(f):
                raise FileNotFoundError(f)

        target = f'{name}:{version}'
        LOG.debug('----> 目标镜像 %s', target)
        CONTAINER_CMD.build(
            './', network='host', target=target,
            no_cache=self.no_cache,
            build_args=[f'PACKAGE_NAME={backend}',
                        f'FORWARD_PACKAGE_NANME={frontend}'])
        return target

    @log_step
    def cleanup(self, resources):
        """清理构建所需的临时文件
        """
        for resource in resources:
            if not os.path.exists(resource):
                LOG.warning('----> file %s not exists', resource)
                continue
            LOG.info('----> remove file %s', resource)
            if os.path.isdir(resource):
                shutil.rmtree(resource)
            else:
                os.remove(resource)

    @log_step
    def push_image(self, name, version):
        """推送 docker 镜像
        """
        # sourcery skip: raise-from-previous-error
        image = f"{name}:{version}"
        target_latest = f"{name}:latest"
        try:
            for registry in self.push_registry:
                CONTAINER_CMD.tag_and_push(image, f'{registry}/{image}')
                if self.push_as_latest:
                    CONTAINER_CMD.tag_and_push(image,
                                               f'{registry}/{target_latest}')
        except Exception as e:
            raise RuntimeError(f'tag/push failed! {e}')

    @property
    def image_name(self):
        return self.bacckend_file.split('-')[0]

    def build(self):
        whl_name, whl_version = self.check_whl_file_and_version()
        self.check_frontend()

        build_resources = self.get_build_resources()
        self.prepare_build_resources(build_resources)
        
        self.update_config_json()
        self.update_favicon()

        try:
            self.build_docker_image(self.image_name, whl_version,
                                    self.bacckend_file, self.frontend_name)
            LOG.info('镜像构建成功')
        except Exception:
            LOG.exception('镜像构建失败')
            return
        finally:
            # TODO
            self.cleanup([
                os.path.basename(dst_path) for _, dst_path in build_resources]
            )

        try:
            self.push_image(self.image_name, whl_version)
        except Exception as e:
            LOG.error('tag/push failed! %s', e)
            return 1

        LOG.info('kubevision 构建成功.')


def main():
    global CONTAINER_CMD

    parser = argparse.ArgumentParser(description='kubevision build tool')
    parser.add_argument('whl_file', help='The file of whl package')
    parser.add_argument('-w', '--webapp',
                        default=os.path.join('webapp', 'dist'),
                        help='The path of webapp')
    parser.add_argument('-r', '--push-registry', nargs='+',
                        help='The registry to push, e.g. docker.io, '
                             'registry1:5100, 125.0.0.1')
    parser.add_argument('-l', '--push-as-latest', action='store_true',
                        help='Push image to registry as latest version')
    parser.add_argument('-n', '--no-cache', action='store_true',
                        help='Force to build')
    parser.add_argument('-c', '--container-cmd', default=shell.DOCKER,
                        choices=[shell.DOCKER, shell.PODMAN],
                        help='Force to build')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Show debug message')

    args = parser.parse_args()
    logging.basicConfig(level=args.debug and logging.DEBUG or logging.INFO,
                        format=LOG_FORMAT)

    CONTAINER_CMD = shell.get_container_impl(impl=args.container_cmd)

    builder = PyWebDockerBuilder(
        args.whl_file, args.webapp,
        config_json='config.json',
        favicon='favicon.ico',
        frontend_name='kubevision',
        push_registry=args.push_registry,
        push_as_latest=args.push_as_latest,
    )
    builder.build()


if __name__ == '__main__':
    sys.exit(main())
