"""Unittests for bilwaj_lib.py"""
import os
import sys

from testutil import unittest

from lib import bilwaj_lib


CANAL_160_WEIGHTS_FILE = os.path.join(unittest.PROJECT_PATH, 'bin/models/canal/UNet160.hdf5')
CANAL_256_WEIGHTS_FILE = os.path.join(unittest.PROJECT_PATH, 'bin/models/canal/UNet256.hdf5')
DISK_WEIGHTS_FILE = os.path.join(unittest.PROJECT_PATH, 'bin/models/disk/UNet.hdf5')
FORAMEN_WEIGHTS_FILE = os.path.join(unittest.PROJECT_PATH, 'bin/models/foramen/UNet.hdf5')

class BilwajUNetTest(unittest.TestCase):

    def test_bilwaj_canal_weights(self):
        model_160 = bilwaj_lib.get_canal_model({
            'img_shape': (160, 160, 1)})
        model_160.load_weights(CANAL_160_WEIGHTS_FILE)

        model_256 = bilwaj_lib.get_canal_model({
            'img_shape': (256, 256, 1),
            'start_ch': 16,
            'residual': False,
        })
        model_256.load_weights(CANAL_256_WEIGHTS_FILE)


    def test_bilwaj_disk_weights(self):
        model = bilwaj_lib.get_disk_model()
        model.load_weights(DISK_WEIGHTS_FILE)

    def test_bilwaj_foramen_weights(self):
        model = bilwaj_lib.get_foramen_model()
        model.load_weights(FORAMEN_WEIGHTS_FILE)


if __name__ == '__main__':
    unittest.main()
