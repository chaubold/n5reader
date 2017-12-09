import os
import json
import logging
from .base import Base
from .group import Group
from .dataset import Dataset

logger = logging.getLogger(__name__)

class File(Base):

    def __init__(self, path):
        # check if the file already exists
        # and load it if it does
        if os.path.exists(path):
            logger.debug(f"Found n5 file {path}")
        # otherwise create a new file
        else:
            logger.debug(f"Creating new n5 file {path}")
            os.mkdir(path)

        super(File, self).__init__(path)

    def create_group(self, key):
        assert key not in self.keys(), \
            "n5reader.File.create_group: Group is already existing"
        path = os.path.join(self.path, key)
        return Group.make_group(path)

    def __getitem__(self, key):
        path = os.path.join(self.path, key)
        assert os.path.exists(path), "n5reader.File.__getitem__: key does not exist"
        if self.is_group(key):
            return Group.open_group(path)
        else:
            return Dataset.open_dataset(path)
