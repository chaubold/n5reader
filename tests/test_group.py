import unittest
import numpy as np
import os
from shutil import rmtree

import sys
try:
    import n5reader
except ImportError:
    sys.path.append('..')
    import n5reader


class TestGroup(unittest.TestCase):

    def setUp(self):
        self.shape = (100, 100, 100)
        if(os.path.exists('array.n5')):
            rmtree('array.n5')
        self.ff_n5 = n5reader.File('array.n5')
        g5 = self.ff_n5.create_group('test')
        g5.create_dataset(
            'test', dtype='float32', shape=self.shape, chunks=(10, 10, 10)
        )

    def tearDown(self):
        if(os.path.exists('array.n5')):
            rmtree('array.n5')


    def test_open_empty_group_n5(self):
        g = self.ff_n5['test']
        ds = g['test']
        print(type(ds))
        print(ds.shape)
        out = ds[:]
        self.assertEqual(out.shape, self.shape)
        self.assertTrue((out == 0).all())

    def test_open_empty_dataset_n5(self):
        ds = self.ff_n5['test/test']
        out = ds[:]
        self.assertEqual(out.shape, self.shape)
        self.assertTrue((out == 0).all())

    def test_group_n5(self):
        g = self.ff_n5.create_group('group')
        ds = g.create_dataset(
            'data', dtype='float32', shape=self.shape, chunks=(10, 10, 10)
        )
        in_array = 42 * np.ones(self.shape, dtype='float32')
        ds[:] = in_array
        out_array = ds[:]
        self.assertEqual(out_array.shape, in_array.shape)
        self.assertTrue(np.allclose(out_array, in_array))


if __name__ == '__main__':
    unittest.main()
