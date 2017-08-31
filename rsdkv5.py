from struct import pack, unpack
from hashlib import md5

def swap_hash_endian(data):
    return pack("<4L", *unpack(">4L", data))


class Data(object):
    def get_data(self):
        return None

    def is_encoded(self):
        return True


class EncodedFileData(Data):
    def __init__(self, filename, offset=0, size=-1):
        self.filename = filename
        self.offset = offset
        self.size = size

    def get_data(self):
        with open(self.filename, "rb") as f:
            f.seek(self.offset)
            data = f.read(self.size)
        return data


class RawFileData(EncodedFileData):
    def is_encoded(self):
        return False


class RSDKv5File(object):
    def __init__(self, filename, data, is_encoded, filename_hash=None):
        self.filename = filename
        if filename_hash is None:
            filename_hash = md5(filename.lower()).digest()
        self.filename_hash = filename_hash
        self.data = data
        self.is_encoded = is_encoded

    def encode(self, data):
        assert self.filename is not None
        key1 = map(ord, swap_hash_endian(md5(self.filename.upper()).digest()))
        key2 = map(ord, swap_hash_endian(md5(str(len(data))).digest()))
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
        return "".join(map(chr, ndata))

    def get_raw_data(self):
        return self.data.get_data()

    def get_encoded_data(self):
        data = self.get_raw_data()
        if self.is_encoded and not self.data.is_encoded():
            data = self.encode(data)
        return data

    def get_data(self):
        data = self.get_raw_data()
        if self.is_encoded and self.data.is_encoded():
            data = self.encode(data)
        return data


class RSDKv5(object):
    def __init__(self, path = None):
        self.files = []
        self.hash_to_file = {}
        if path is not None:
            with open(path, "rb") as f:
                assert f.read(4) == "RSDK", "Invalid magic (expected RSDK)"
                assert f.read(2) == "v5", "Invalid RSDK magic (expected v5)"
                file_count = unpack("<H", f.read(2))[0]
                for i in range(file_count):
                    hash = swap_hash_endian(f.read(16))
                    offset, size = unpack("<LL", f.read(8))
                    is_encoded = (size >> 31) == 1
                    size &= 0x7FFFFFFF
                    self.files.append(RSDKv5File(None, EncodedFileData(path, offset, size), is_encoded, hash))
                    self.hash_to_file[hash] = self.files[-1]

    def get_file(self, name):
        hash = md5(name.lower()).digest()
        f = self.hash_to_file.get(hash)
        if f is not None:
            f.filename = name
        return f

    @staticmethod
    def get_static_object_path(name):
        hash = swap_hash_endian(hashlib.md5(name).digest())

        filename = ""
        filename += hash[0:4].encode("hex").upper()[::-1]
        filename += hash[4:8].encode("hex").upper()[::-1]
        filename += hash[8:12].encode("hex").upper()[::-1]
        filename += hash[12:16].encode("hex").upper()[::-1]

        return "Data/Objects/Static/%s.bin" % filename

    def add_file(self, name, data, is_encoded, filename_hash=None):
        self.files.append(RSDKv5File(name, data, is_encoded, filename_hash))
        self.hash_to_file[self.files[-1].filename_hash] = self.files[-1]

    def dump(self, output_file):
        output_file.write("RSDKv5")
        output_file.write(pack("<H", len(self.files)))
        offset = 8 + len(self.files) * 0x18
        for f in self.files:
            file_length = len(f.get_raw_data())
            output_file.write(swap_hash_endian(f.filename_hash))
            output_file.write(pack("<LL", offset, file_length | (int(f.is_encoded) << 31)))
            offset += file_length
        for f in self.files:
            output_file.write(f.get_encoded_data())
