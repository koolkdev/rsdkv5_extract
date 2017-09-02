from construct import *
import sys

String = PascalString(Byte)
Word = Int16ul
Dword = Int32ul

def inc(ctx, var):
    res = ctx[var]
    ctx[var] += 1
    return res

CFG = Struct(
    "Magic" / Const("CFG\0"),

    # Bool - if to use the objects specified in GameObject.bin
    "UseGameObject" / Byte,

    "Objects" / PrefixedArray(Byte, String),

    "Palettes" / Array(8, Struct(
        "Bitmap" / Word,
        "i" / Computed(0),
        "Columns" / Array(16, Struct(
            "Pixels" / If(lambda ctx: (1 << inc(ctx._, "i")) & ctx._.Bitmap,
                Array(16, Struct(
                    "R" / Byte,
                    "G" / Byte,
                    "B" / Byte
                ))
            )
        ))
    )),

    "WavFiles" / PrefixedArray(Byte, Struct(
        "Path" / String,
        "Unknown" / Byte
    )),
)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: parse_stage_config.py StageConfig.bin"
        sys.exit(-1)

    if not sys.argv[1].endswith(".bin"):
        print "Expected .bin file"
        sys.exit(-1)

    cfg = CFG.parse(open(sys.argv[1], "rb").read())
    print(cfg)
