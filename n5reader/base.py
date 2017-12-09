import os
import json
from .dataset import Dataset
from .attribute_manager import AttributeManager


class Base(object):

    def __init__(self, path):
        self.path = path
        self._attrs = AttributeManager(path)

    @property
    def attrs(self):
        return self._attrs

    # FIXME this is not what we want, because
    # a) we want to have the proper python key syntax
    # b) this will not list nested paths in file properly,
    # like 'volumes/raw'
    def keys(self):
        return os.listdir(self.path)

    def __contains__(self, key):
        return os.path.exists(os.path.join(self.path, key))

    
    # TODO allow creating with data ?!
    def create_dataset(self, key, dtype, shape, chunks,
                       fill_value=0,
                       compressor='gzip', 
                       codec='lz4',
                       level=4,
                       shuffle=1):
        assert key not in self.keys(), "Dataset is already existing"
        path = os.path.join(self.path, key)
        return Dataset.create_dataset(path, dtype, shape,
                                      chunks,
                                      fill_value, compressor,
                                      codec, level, shuffle)

    def is_group(self, key):
        path = os.path.join(self.path, key)
    
        meta_path = os.path.join(path, 'attributes.json')
        if not os.path.exists(meta_path):
            return True
        with open(meta_path, 'r') as f:
            # attributes for n5 file can be empty which cannot be parsed by json
            try:
                attributes = json.load(f)
            except ValueError:
                attributes = {}
        # The dimensions key is only present in a dataset
        return 'dimensions' not in attributes
