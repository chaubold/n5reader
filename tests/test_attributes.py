from __future__ import print_function

import unittest
import os
from shutil import rmtree

import sys
try:
    import n5reader
except ImportError:
    sys.path.append('..')
    import n5reader


class TestAttributes(unittest.TestCase):

    def attrs_test(self, attrs):
        attrs["a"] = 1
        attrs["b"] = [1, 2, 3]
        attrs["c"] = "whooosa"
        self.assertEqual(attrs["a"], 1)
        self.assertEqual(attrs["b"], [1, 2, 3])
        self.assertEqual(attrs["c"], "whooosa")

    def setUp(self):
        self.shape = (100, 100, 100)
        
        self.ff_n5 = n5reader.File('array.n5')
        self.ff_n5.create_dataset(
            'ds', dtype='float32', shape=self.shape, chunks=(10, 10, 10)
        )
        self.ff_n5.create_group('group')

    def tearDown(self):
        if(os.path.exists('array.n5')):
            rmtree('array.n5')

    def test_attrs_n5(self):

        # test file attributes
        print("N5: File Attribute Test")
        f_attrs = self.ff_n5.attrs
        self.attrs_test(f_attrs)

        # test group attributes
        print("N5: Group Attribute Test")
        f_group = self.ff_n5["group"].attrs
        self.attrs_test(f_group)

        # test ds attributes
        print("N5: Dataset Attribute Test")
        f_ds = self.ff_n5["ds"].attrs
        self.attrs_test(f_ds)


if __name__ == '__main__':
    unittest.main()
