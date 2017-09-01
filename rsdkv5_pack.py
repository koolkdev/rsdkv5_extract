import sys
import os
import rsdkv5

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: rsdkv5_extract.py Data.rsdk input_folder"
        sys.exit(-1)

    input_path = sys.argv[2]
    if not input_path.endswith("/") and not input_path.endswith("\\"):
        input_path += os.path.sep

    # Load known files
    filenames = [x.strip() for x in open("sonic_mania_files_list.txt", "r").readlines()]

    rsdk = rsdkv5.RSDKv5()
    for root, dirnames, filenames in os.walk(input_path):
        nroot = root.replace("\\", "/")
        assert nroot.startswith(input_path.replace("\\", "/"))
        nroot = nroot[len(input_path):]
        if not nroot.startswith("."):
            for filename in filenames:
                # Don't encrypt any file, it takes time
                rsdk.add_file(nroot + "/" + filename, rsdkv5.RawFileData(os.path.join(root, filename)), False)
                print "Add %s" % (nroot + "/" + filename)

    # Now add unknowns
    for root, dirnames, filenames in os.walk(input_path):
        nroot = root.replace("\\", "/")
        assert nroot.startswith(input_path.replace("\\", "/"))
        nroot = nroot[len(input_path):]
        if nroot == ".unknown_encrypted":
            for filename in filenames:
                if filename.decode("hex") not in rsdk.hash_to_file:
                    rsdk.add_file(None, rsdkv5.EncryptedFileData(os.path.join(root, filename)), True, filename.decode("hex"))
                    print "Add %s" % filename
        elif nroot == ".unknown":
            for filename in filenames:
                if filename.decode("hex") not in rsdk.hash_to_file:
                    rsdk.add_file(None, rsdkv5.EncryptedFileData(os.path.join(root, filename)), False, filename.decode("hex"))
                    print "Add %s" % filename

    print "Writing %s" % sys.argv[1]
    rsdk.dump(open(sys.argv[1], "wb"))
