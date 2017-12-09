import os
import logging
from .base import Base
from .dataset import Dataset

logger = logging.getLogger(__name__)

class Group(Base):

    def __init__(self, path):
        super(Group, self).__init__(path)

    @classmethod
    def make_group(cls, path):
        create_group(path)
        return cls(path)

    @classmethod
    def open_group(cls, path):
        return cls(path)

    def create_group(self, key):
        assert key not in self.keys(), "Group is already existing"
        path = os.path.join(self.path, key)
        return Group.make_group(path)

    def __getitem__(self, key):
        assert key in self, "n5reader.File.__getitem__: key does not exxist"
        path = os.path.join(self.path, key)
        if self.is_group(key):
            return Group.open_group(path)
        else:
            return Dataset.open_dataset(path)
