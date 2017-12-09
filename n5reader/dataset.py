import numpy as np
import numbers
import logging
import struct
import zlib

# from ._n5reader import DatasetImpl, open_dataset, create_dataset
# from ._n5reader import write_subarray, write_scalar, read_subarray
from .attribute_manager import AttributeManager
logger = logging.getLogger(__name__)

class Dataset(object):

    dtype_dict = {np.dtype('uint8'): 'uint8',
                  np.dtype('uint16'): 'uint16',
                  np.dtype('uint32'): 'uint32',
                  np.dtype('uint64'): 'uint64',
                  np.dtype('int8'): 'int8',
                  np.dtype('int16'): 'int16',
                  np.dtype('int32'): 'int32',
                  np.dtype('int64'): 'int64',
                  np.dtype('float32'): 'float32',
                  np.dtype('float64'): 'float64'}

    compressors_n5 = ['raw', 'gzip', 'bzip2']
    n5_default_compressor = 'gzip'

    def __init__(self, path, dset_impl):
        assert isinstance(dset_impl, DatasetImpl)
        self._impl = dset_impl
        self._attrs = AttributeManager(path)

    @classmethod
    def create_dataset(cls, path, dtype,
                       shape, chunks,
                       fill_value, compressor,
                       codec, level, shuffle):
        if compressor not in cls.compressors_n5:
            if compressor != None:
                logger.warn("Invalid compressor provided, using default...")
            compressor = cls.n5_default_compressor

        # support for numpy datatypes
        if not isinstance(dtype, str):
            assert dtype in cls.dtype_dict, "n5reader.Dataset: invalid data type"
            dtype_ = cls.dtype_dict[dtype]
        else:
            dtype_ = dtype

        return cls(path, create_dataset(path, dtype_,
                                        shape, chunks,
                                        fill_value,
                                        compressor, codec,
                                        level, shuffle))

    @classmethod
    def open_dataset(cls, path):
        return cls(path, open_dataset(path))

    @property
    def attrs(self):
        return self._attrs

    @property
    def shape(self):
        return tuple(self._impl.shape)

    @property
    def ndim(self):
        return self._impl.ndim

    @property
    def size(self):
        return self._impl.size

    @property
    def chunks(self):
        return tuple(self._impl.chunks)

    @property
    def dtype(self):
        return np.dtype(self._impl.dtype)

    @property
    def chunks_per_dimension(self):
        return self._impl.chunks_per_dimension

    @property
    def number_of_chunks(self):
        return self._impl.number_of_chunks

    @property
    def compression_options(self):
        return {'compressor': self._impl.compressor,
                'codec': self._impl.codec,
                'level': self._impl.level,
                'shuffle': self._impl.shuffle}

    def __len__(self):
        return self._impl.len

    # TODO support ellipsis
    def index_to_roi(self, index):

        # check index types of index and normalize the index
        assert isinstance(index, (slice, tuple)), \
            "n5reader.Dataset: index must be slice or tuple of slices"
        index_ = (index,) if isinstance(index, slice) else index

        # check lengths of index
        assert len(index_) <= self.ndim, "n5reader.Dataset: index is longer than dimension"

        # check the individual slices
        assert all(isinstance(ii, slice) for ii in index_), \
            "n5reader.Dataset: index must be slice or tuple of slices"
        assert all(ii.step is None for ii in index_), \
            "n5reader.Dataset: slice with non-trivial step is not supported"
        # get the roi begin and shape from the slicing
        roi_begin = [
            (0 if index_[d].start is None else index_[d].start)
            if d < len(index_) else 0 for d in range(self.ndim)
        ]
        roi_shape = tuple(
            ((self.shape[d] if index_[d].stop is None else index_[d].stop)
             if d < len(index_) else self.shape[d]) - roi_begin[d] for d in range(self.ndim)
        )
        return roi_begin, roi_shape

    # most checks are done in c++
    def __getitem__(self, index):
        roi_begin, shape = self.index_to_roi(index)
        out = np.empty(shape, dtype=self.dtype)
        read_subarray(self._impl, out, roi_begin)
        return out

    # most checks are done in c++
    def __setitem__(self, index, item):
        assert isinstance(item, (numbers.Number, np.ndarray))
        roi_begin, shape = self.index_to_roi(index)

        # n5 input must be transpsed due to different axis convention
        # write the complete array
        if isinstance(item, np.ndarray):
            assert item.ndim == self.ndim, \
                "n5reader.Dataset: complicated broadcasting is not supported"
            write_subarray(self._impl, item, roi_begin)

        # broadcast scalar
        else:
            # FIXME this seems to broken; fails with RuntimeError('WrongRequest Shape')
            write_scalar(self._impl, roi_begin, list(shape), item)

    def find_minimum_coordinates(self, dim):
        return self._impl.findMinimumCoordinates(dim)

    def find_maximum_coordinates(self, dim):
        return self._impl.findMaximumCoordinates(dim)

    # expose the impl write subarray functionality
    def write_subarray(self, start, data):
        write_subarray(self._impl, data, start)

    # expose the impl read subarray functionality
    def read_subarray(self, start, stop):
        shape = tuple(sto - sta for sta, sto in zip(start, stop))
        out = np.empty(shape, dtype=self.dtype)
        read_subarray(self._impl, out, start)
        return out

    def _encode_header(self, shape):
        # FIXME: mode must be 0 now, 1 for variable length needs to be implemented
        buf = struct.pack('>HH' + 'I'*len(shape), 
                    0, # mode
                    len(shape), # num dimensions
                    *shape
                    )
        return buf


    def _decode_header(self, buf):
        # FIXME: mode must be 0 now, 1 for variable length needs to be implemented
        mode, ndims = struct.unpack_from('>HH', buf, offset=0)
        assert mode == 0, "Only supporting mode 0 for now, no varlength yet!"
        offset = struct.calcsize('>HH')
        shape = struct.unpack_from('>'+'I'*ndim, buf, offset=offset)
        offset += struct.calcsize('>'+'I'*ndim)
        data = buf[offset:]
        return shape, data

    def _compress_body(self, data, compressor):
        if compressor == 'raw':
            return data
        if compressor == 'gzip':
            return zlib.compress(data)
        else:
            raise ValueError(f"unknown compressor {compressor}")

    def _data_to_binary_chunk(self, data):
        assert isinstance(data, np.ndarray), "can only convert numpy arrays to chunk"
        assert dtype_dict[data.dtype] == dtype_, "provided array has wrong dtype"
        assert data.shape == self.chunks, f"data must have correct chunk size {self.chunks}, not {data.shape}!"

        header = self._encode_header(data.shape)

