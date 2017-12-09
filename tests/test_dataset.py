import unittest
import sys
import numpy as np
import os
from shutil import rmtree

import sys
try:
    import n5reader
except ImportError:
    sys.path.append('..')
    import n5reader


class TestDataset(unittest.TestCase):

    def setUp(self):
        self.shape = (100, 100, 100)
        self.ff_n5 = n5reader.File('array.n5')
        self.ff_n5.create_dataset(
            'test', dtype='float32', shape=self.shape, chunks=(10, 10, 10)
        )

    def tearDown(self):
        if(os.path.exists('array.n5')):
            rmtree('array.n5')


    def test_ds_open_empty_n5(self):
        print("open empty n5 array")
        ds = self.ff_n5['test']
        out = ds[:]
        self.assertEqual(out.shape, self.shape)
        self.assertTrue((out == 0).all())

    def test_ds_n5(self):
        dtypes = ('int8', 'int16', 'int32', 'int64',
                  'uint8', 'uint16', 'uint32', 'uint64',
                  'float32', 'float64')
        dtypes = ('int32',)

        for dtype in dtypes:
            print("Running N5-Test for %s" % dtype)
            ds = self.ff_n5.create_dataset(
                'data_%s' % dtype, dtype=dtype, shape=self.shape, chunks=(10, 10, 10)
            )
            in_array = 42 * np.ones(self.shape, dtype=dtype)
            print("Writing ds...")
            ds[:] = in_array
            print("...done")
            print("Reading ds...")
            out_array = ds[:]
            print("...done")
            self.assertEqual(out_array.shape, in_array.shape)
            self.assertTrue(np.allclose(out_array, in_array))

    def test_ds_n5_array_to_format(self):
        dtypes = ('int8', 'int16', 'int32', 'int64',
                  'uint8', 'uint16', 'uint32', 'uint64',
                  'float32', 'float64')

        for dtype in dtypes:
            print("Running N5 Array to format-Test for %s" % dtype)
            ds = self.ff_n5.create_dataset(
                'data_%s' % dtype, dtype=dtype, shape=self.shape, chunks=(10, 10, 10)
            )
            in_array = 42 * np.ones((10, 10, 10), dtype=dtype)
            print("Writing ds...")
            ds[:10,:10,:10] = in_array
            print("...done")

            
            print("Reading chunk...")
            path = os.path.join(os.path.dirname(ds.attrs.path), '0', '0', '0')
            read_from_file = open(path, 'rb').read()
            
            converted_data = ds.array_to_format(in_array)

            print("...done")
            self.assertEqual(len(read_from_file), len(converted_data))
            self.assertEqual(read_from_file, converted_data)


if __name__ == '__main__':
    unittest.main()
