import struct
import hashlib
import time

def swap_hash_endian(data):
    return struct.pack("<4L", *struct.unpack(">4L", data))


class Data(object):
    def get_data(self):
        raise NotImplementedError()

    def is_encrypted(self):
        raise NotImplementedError()

class FileData(Data):
    def __init__(self, filename, offset=0, size=-1):
        self.filename = filename
        self.offset = offset
        self.size = size

    def get_data(self):
        f = open(self.filename, "rb")
        f.seek(self.offset)
        data = f.read(self.size)
        return data

class EncryptedFileData(FileData):
    def is_encrypted(self):
        return True

class RawFileData(FileData):
    def is_encrypted(self):
        return False


class RSDKv5File(object):
    def __init__(self, filename, data, is_encrypted, filename_hash=None):
        self.filename = filename
        if filename_hash is None:
            filename_hash = hashlib.md5(filename.lower()).digest()
        self.filename_hash = filename_hash
        self.data = data
        self.is_encrypted = is_encrypted
        self.key1 = None

    def encrypt_decrypt(self, data, is_decrypt=False):
        if self.key1 is None:
            assert self.filename is not None
            key1 = map(ord, swap_hash_endian(hashlib.md5(self.filename.upper()).digest()))
        else:
            key1 = self.key1
        key2 = map(ord, swap_hash_endian(hashlib.md5(str(len(data))).digest()))
        key1_index = 0
        key2_index = 8
        swap_nibbles = 0
        xor_value = (len(data) >> 2) & 0x7f

        ndata = []
        for c in map(ord, data):
            if is_decrypt:
                c ^= xor_value ^ key2[key2_index]
            else:
                c ^= key1[key1_index]
            if swap_nibbles:
                c = (c >> 4) | ((c & 0xf) << 4)
            if is_decrypt:
                c ^= key1[key1_index]
            else:
                c ^= xor_value ^ key2[key2_index]
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

    def guess_unknown_encrypted_key(self):
        # Assume most of the bytes are zero
        data = self.get_encrypted_data()
        key1_options = [[] for i in xrange(16)]
        key2 = map(ord, swap_hash_endian(hashlib.md5(str(len(data))).digest()))
        key1_index = 0
        key2_index = 8
        swap_nibbles = 0
        xor_value = (len(data) >> 2) & 0x7f

        for c in map(ord, data):
            c ^= xor_value ^ key2[key2_index]
            if swap_nibbles:
                c = (c >> 4) | ((c & 0xf) << 4)
            key1_options[key1_index].append(c)

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
        self.key1 = []
        for i in xrange(0x10):
            max_occurrence = 0
            b = 0
            for j in xrange(0x100):
                cc = key1_options[i].count(j)
                if cc > max_occurrence:
                    max_occurrence = cc
                    b = j
            self.key1.append(b)

    def encrypt(self, data):
        return self.encrypt_decrypt(data, False)

    def decrypt(self, data):
        return self.encrypt_decrypt(data, True)

    def get_raw_data(self):
        return self.data.get_data()

    def get_encrypted_data(self):
        data = self.get_raw_data()
        if self.is_encrypted and not self.data.is_encrypted():
            data = self.encrypt(data)
        return data

    def get_data(self):
        data = self.get_raw_data()
        if self.is_encrypted and self.data.is_encrypted():
            data = self.decrypt(data)
        return data


class RSDKv5(object):
    def __init__(self, path = None):
        self.files = []
        self.hash_to_file = {}
        if path is not None:
            f = open(path, "rb")
            assert f.read(4) == "RSDK", "Invalid magic (expected RSDK)"
            assert f.read(2) == "v5", "Invalid RSDK magic (expected v5)"
            files_count = struct.unpack("<H", f.read(2))[0]
            for i in xrange(files_count):
                hash = swap_hash_endian(f.read(0x10))
                offset, size = struct.unpack("<LL", f.read(0x8))
                is_encrypted = (size >> 31) == 1
                size &= 0x7fffffff
                self.files.append(RSDKv5File(None, EncryptedFileData(path, offset, size), is_encrypted, hash))
                self.hash_to_file[hash] = self.files[-1]

    def get_file(self, name):
        hash = hashlib.md5(name.lower()).digest()
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

    def add_file(self, name, data, is_encrypted, filename_hash=None):
        self.files.append(RSDKv5File(name, data, is_encrypted, filename_hash))
        self.hash_to_file[self.files[-1].filename_hash] = self.files[-1]

    def dump(self, output_file):
        output_file.write("RSDKv5")
        output_file.write(struct.pack("<H", len(self.files)))
        offset = 8 + len(self.files) * 0x18
        for f in self.files:
            file_length = len(f.get_raw_data())
            output_file.write(swap_hash_endian(f.filename_hash))
            output_file.write(struct.pack("<LL", offset, file_length | (int(f.is_encrypted) << 31)))
            offset += file_length
        for f in self.files:
            output_file.write(f.get_encrypted_data())


