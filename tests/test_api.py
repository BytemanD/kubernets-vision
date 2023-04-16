import pathlib
import unittest

from kubernetes import config

from kubevision.k8s import api

CLIENT = None


def init():
    global CLIENT

    kube_config = pathlib.Path('/etc', 'kubevision', 'config')
    api.init(kube_config)
    CLIENT = api.CLIENT


class TestK8sApi(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.contexts, self.current = config.list_kube_config_contexts()

    def test_get_config(self):
        self.assertIsNotNone(self.contexts)
        self.assertIsNotNone(self.current)
        self.assertIsNotNone(api.get_config())

    def test_create_workload(self):
        self.assertIsNone(CLIENT.create_workload('/tmp/test_ds.yaml'))


init()
