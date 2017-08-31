import struct
import hashlib
import sys
import os

def swap_hash_endian(data):
    return struct.pack("<4L", *struct.unpack(">4L", data))

class RSDKv5File(object):
    def __init__(self, container, filename_hash, offset, size, is_encoded):
        self.container = container
        self.filename_hash = filename_hash
        self.offset = offset
        self.size = size
        self.is_encoded = is_encoded
        self.filename = None

    def get_raw_data(self):
        f = self.container.get_raw_file()
        f.seek(self.offset)
        data = f.read(self.size)
        return data

    def get_data(self):
        data = self.get_raw_data()
        if self.is_encoded:
            assert self.filename is not None
            key1 = map(ord, swap_hash_endian(hashlib.md5(self.filename.upper()).digest()))
            key2 = map(ord, swap_hash_endian(hashlib.md5(str(self.size)).digest()))
            key1_index = 0
            key2_index = 8
            swap_nibbles = 0
            xor_value = (self.size >> 2) & 0x7f

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
            self.files.append(RSDKv5File(self, hash, offset, size, is_encoded))
            self.hash_to_file[hash] = self.files[-1]

    def get_raw_file(self):
        return self.f

    def get_file(self, name):
        hash = hashlib.md5(name.lower()).digest()
        f = self.hash_to_file.get(hash)
        if f is not None:
            f.filename = name
        return f

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: rsdkv5_extract.py Data.rsdk"
        sys.exit(-1)

    # Load known files
    filenames = [x.strip() for x in open("sonic_mania_files_list.txt", "r").readlines()]

    rsdk = RSDKv5(sys.argv[1])
    for filename in filenames:
        f = rsdk.get_file(filename)
        if f is not None:
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            print "Extracting %s" % filename
            open(filename, "wb").write(f.get_data())

    for f in rsdk.files:
        if f.filename is None:
            if f.is_encoded:
                filename = ".unknown_encrypted/%s" % f.filename_hash.encode("hex")
            else:
                filename = ".unknown/%s" % f.filename_hash.encode("hex")
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            print "Extracting %s" % filename
            open(filename, "wb").write(f.get_raw_data())
