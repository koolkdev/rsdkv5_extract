import struct
import hashlib

def swap_hash_endian(data):
    return struct.pack("<4L", *struct.unpack(">4L", data))


class Data(object):
    def get_data(self):
        return None


class FileData(Data):
    def __init__(self, file, offset, size):
        self.file = file
        self.offset = offset
        self.size = size

    def get_data(self):
        self.file.seek(self.offset)
        data = self.file.read(self.size)
        return data


class RSDKv5File(object):
    def __init__(self, filename, data, is_encoded, filename_hash=None):
        self.filename = filename
        if filename_hash is None:
            filename_hash = hashlib.md5(filename.lower()).digest()
        self.filename_hash = filename_hash
        self.data = data
        self.is_encoded = is_encoded

    def get_raw_data(self):
        return self.data.get_data()

    def get_data(self):
        data = self.get_raw_data()
        if self.is_encoded:
            assert self.filename is not None
            key1 = map(ord, swap_hash_endian(hashlib.md5(self.filename.upper()).digest()))
            key2 = map(ord, swap_hash_endian(hashlib.md5(str(len(data))).digest()))
            key1_index = 0
            key2_index = 8
            swap_nibbles = 0
            xor_value = (len(data) >> 2) & 0x7f

            ndata = []
            for c in map(ord, data):
                c ^= xor_value
                c ^= key2[key2_index]
                if swap_nibbles:
                    c = (c >> 4) | ((c & 0xf) << 4)
                c ^= key1[key1_index]
                ndata.append(c)

                # Update things
                key1_index += 1
                key2_index += 1
                if key1_index > 15 and key2_index > 8:
                    xor_value += 2
                    xor_value &= 0x7f
                    if swap_nibbles:
                        key1_index = xor_value % 7
                        key2_index = (xor_value % 12) + 2
                    else:
                        key1_index = (xor_value % 12) + 3
                        key2_index = xor_value % 7
                    swap_nibbles ^= 1
                else:
                    if key1_index > 15:
                        swap_nibbles ^= 1
                        key1_index = 0
                    if key2_index > 12:
                        swap_nibbles ^= 1
                        key2_index = 0
            data = "".join(map(chr, ndata))
        return data


class RSDKv5(object):
    def __init__(self, path):
        self.f = open(path, "rb")
        assert self.f.read(4) == "RSDK", "Invalid magic (expected RSDK)"
        assert self.f.read(2) == "v5", "Invalid RSDK magic (expected v5)"
        files_count = struct.unpack("<H", self.f.read(2))[0]
        self.files = []
        self.hash_to_file = {}
        for i in xrange(files_count):
            hash = swap_hash_endian(self.f.read(0x10))
            offset, size = struct.unpack("<LL", self.f.read(0x8))
            is_encoded = (size >> 31) == 1
            size &= 0x7fffffff
            self.files.append(RSDKv5File(None, FileData(self.f, offset, size), is_encoded, hash))
            self.hash_to_file[hash] = self.files[-1]

    def get_file(self, name):
        hash = hashlib.md5(name.lower()).digest()
        f = self.hash_to_file.get(hash)
        if f is not None:
            f.filename = name
        return f
