import pathlib


NAME = 'KubeVision'

AUTH = 'fjboy'
REPO = 'kube-vision'
RELEASES_API = f'https://api.github.com/repos/{AUTH}/{REPO}/releases'

IMAGE_NAMESPACE = 'fjboy'
IMAGE_TAGS_API = f'https://hub.docker.com/v2/namespaces/{IMAGE_NAMESPACE}' \
                 f'/repositories/{NAME}/tags'

DEFAULT_NAMESPACE = 'default'

DEFAULT_CONF_FILES = [pathlib.Path('/etc/kubevision/kubevision.conf'),
                      pathlib.Path('etc', 'kubevision.conf')]
DEFAULT_KUBE_CONFIG = pathlib.Path.home().joinpath('.kube', 'config')
