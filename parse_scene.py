from construct import *
import sys

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

SCN = Struct(
    "magic" / Const("SCN\0"),

    # Ignored
    "skipped_header" / Bytes(16),
    # Name of some bin file
    "skipped_bin_name" / LString,
    "skipped_byte" / Byte,

    "Views" / PrefixedArray(Byte, Struct(
        # This is read as part as the length of next string, and ignored
        "ignored_byte" / Byte,
        "Name" / LString,

        "unknown_byte_1" / Byte,
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

        "ScrollingInfo" / CompressedZlib(Bytes(this.Height * 0x10)),

        "Tiles" / CompressedZlib(Array(this.Width * this.Height, Word))
    )),

    "ObjectsInstances" / PrefixedArray(Byte, Struct(
        "ObjectNameHash" / Bytes(16),

        "AttributesCount" / Byte,
        "AttributesInfo" / Array(this.AttributesCount-1, Struct(
            "AttributeNameHash" / Bytes(16),
            "AttributeType" / Enum(Byte,
                UINT8=0,
                UINT16=1,
                UINT32=2,
                INT8=3,
                INT16=4,
                INT32=5,
                DWORD=6,
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
                        "DWORD": Dword,
                        "BOOL": Dword,
                        "STRING": FocusedSeq(1, "length" / Word, "value" / String(this.length * 2, "utf16", "\xff")),
                        "VECTOR2D": Struct("X" / Dword, "Y" / Dword),
                        "COLOR": Struct("R" / Byte, "G" / Byte, "B" / Byte, "A" / Byte),
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

    scene = SCN.parse(open(sys.argv[1], "rb").read())
    print(scene)
