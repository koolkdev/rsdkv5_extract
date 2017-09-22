from construct import *
import sys
import hashlib
import ConfigParser

LString = PascalString(Byte)
Word = Int16ul
Dword = Int32ul

def CompressedZlib(subcon):
    # Compressed zlib, prefixed with a dword for the size of the compressed data (including the big endian dword with the size of the uncompressed data)
    return Prefixed(Dword, FocusedSeq(1,
        "uncompressed_length" / Int32ub,
        "compressed_data" / Compressed(subcon, "zlib"),
    ))

def inc(ctx, var):
    res = ctx[var]
    ctx[var] += 1
    return res

hashes_to_objects = {}
hashes_to_attributes = {}

Color = Struct("B" / Byte, "G" / Byte, "R" / Byte, "A" / Byte)

SCN = Struct(
    "Magic" / Const("SCN\0"),

    # Ignored
    "EditorHeader" / Struct(
        "Unknown1" / Byte,  # 2/3/4 not sure
        "BackgroundColor1" / Color,
        "BackgroundColor2" / Color,
        "Unknown2" / Bytes(7),  # Const: 01010400010400

        # Name of some bin file
        "skipped_bin_name" / LString,
        "skipped_byte" / Byte,
    ),

    "Layers" / PrefixedArray(Byte, Struct(
        # This is read as part as the length of next string, and ignored
        "ignored_byte" / Byte,
        "Name" / LString,

        "IsScrollingVertical" / Byte,
        "unknown_byte_2" / Byte,  # Related to background switch?

        "Width" / Word,
        "Height" / Word,

        "unknown_word_5" / Word,
        "unknown_word_6" / Word,

        "ScrollArray" / PrefixedArray(Word, Struct(
            "unknown_word_1" / Word,
            "unknown_word_2" / Word,
            "unknown_byte_1" / Byte,
            "unknown_byte_2" / Byte,
        )),

        "ScrollingInfo" / CompressedZlib(Bytes(lambda this: (this.IsScrollingVertical and this.Width or this.Height) * 0x10)),

        "Tiles" / CompressedZlib(Array(this.Width * this.Height, Word))
    )),

    "ObjectsInstances" / PrefixedArray(Byte, Struct(
        "ObjectNameHash" / Bytes(16),
        "ObjectName" / Computed(lambda this: hashes_to_objects.get(this.ObjectNameHash)),

        "AttributesCount" / Byte,
        "AttributesInfo" / Array(this.AttributesCount-1, Struct(
            "AttributeNameHash" / Bytes(16),
            "AttributeName" / Computed(lambda this: hashes_to_attributes.get(this.AttributeNameHash)),
            "AttributeType" / Enum(Byte,
                UINT8=0,
                UINT16=1,
                UINT32=2,
                INT8=3,
                INT16=4,
                INT32=5,
                VAR=6,
                BOOL=7,
                STRING=8,
                VECTOR2D=9,
                COLOR=11,
            )
        )),

        "InstancesAttributes" / PrefixedArray(Word, Struct(
            "ObjectID" / Word,
            "X" / Dword,
            "Y" / Dword,
            "i" / Computed(0),
            "Attributes" / Array(this._.AttributesCount-1,
                Switch(lambda this: this._.AttributesInfo[inc(this, "i")].AttributeType,
                    {
                        "UINT8": Byte,
                        "UINT16": Word,
                        "UINT32": Dword,
                        "INT8": Int8sl,
                        "INT16": Int16sl,
                        "INT32": Int32sl,
                        "VAR": Dword,
                        "BOOL": Dword,
                        "STRING": FocusedSeq(1, "length" / Word, "value" / String(this.length * 2, "utf16", "\xff")),
                        "VECTOR2D": Struct("X" / Dword, "Y" / Dword),
                        "COLOR": Color,
                    }
                )
            )
        ))
    ))
)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: parse_scene.py SceneX.bin")
        sys.exit(-1)

    if not sys.argv[1].endswith(".bin"):
        print("Expected .bin file")
        sys.exit(-1)

    try:
        objects_attributes = ConfigParser.ConfigParser()
        objects_attributes.optionxform=str
        objects_attributes.readfp(open('objects_attributes.ini'))

        for obj in objects_attributes.sections():
            hashes_to_objects[hashlib.md5(obj).digest()] = obj
            for attr in objects_attributes.options(obj):
                hashes_to_attributes[hashlib.md5(attr).digest()] = attr
    except:
        pass

    scene = SCN.parse(open(sys.argv[1], "rb").read())
    print(scene)
