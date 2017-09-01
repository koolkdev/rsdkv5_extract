import sys
import os
import rsdkv5

if __name__ == "__main__":
    if not 2 <= len(sys.argv) <= 3:
        print "Usage: rsdkv5_extract.py Data.rsdk [output_folder]"
        sys.exit(-1)

    output_path = None
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]

    dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Load known files
    filenames = [x.strip() for x in open(os.path.join(dir, "sonic_mania_files_list.txt"), "r").readlines()]

    static_objects_names = [x.strip() for x in open(os.path.join(dir, "static_objects_list.txt"), "r").readlines()]
    filenames += [rsdkv5.RSDKv5.get_static_object_path(name) for name in static_objects_names]

    # Load mapping between unknown filenames lower case hash to higher case hash
    unknown_keys = {x.strip().split("=")[0].decode("hex"):x.strip().split("=")[1].decode("hex") for x in \
                    open(os.path.join(dir, "unknown_keys.txt"), "r").readlines()}

    rsdk = rsdkv5.RSDKv5(sys.argv[1])
    for filename in filenames:
        f = rsdk.get_file(filename)
        path = filename
        if output_path is not None:
            path = os.path.join(output_path, path)
        if f is not None:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            print "Extracting %s" % filename
            open(path, "wb").write(f.get_data())

    for f in rsdk.files:
        if f.filename is None:
            if f.is_encrypted and f.filename_hash not in unknown_keys:
                filename = ".unknown_encrypted/%s" % f.filename_hash.encode("hex")
            else:
                filename = ".unknown/%s" % f.filename_hash.encode("hex")
                if f.is_encrypted:
                    f.key1 = map(ord, unknown_keys[f.filename_hash])
            path = filename
            if output_path is not None:
                path = os.path.join(output_path, path)
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            print "Extracting %s" % filename
            if f.is_encrypted and f.filename_hash not in unknown_keys:
                open(path, "wb").write(f.get_raw_data())
            else:
                open(path, "wb").write(f.get_data())

            if f.is_encrypted:
                filename = ".unknown_encrypted_guess/%s" % f.filename_hash.encode("hex")
                path = filename
                if output_path is not None:
                    path = os.path.join(output_path, path)
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                f.guess_unknown_encrypted_key()
                open(path, "wb").write(f.get_data())
