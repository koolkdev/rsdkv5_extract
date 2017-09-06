from construct import *
import sys

MDL = Struct(
    "Magic" / Const("MDL\0"),
    # Flags
    Embedded(FlagsEnum(Int8ul,
        HasNormals=1,
        HasUnknown=2,
        HasColors=4)),
    # How many vertices in face. 3 or 4
    "FaceVerticesCount" / Int8ul,
    "VerticesCount" / Int16ul,
    "FramesCount" / Int16ul,

    If(lambda ctx: ctx.HasUnknown,
        "UnknownList" / Array(this.VerticesCount,
            Struct(
                "x" / Float32l,
                "y" / Float32l,
            )
        )
    ),

    If(lambda ctx: ctx.HasColors,
        "Colors" / Array(this.VerticesCount,
            Struct(
                "r" / Int8ul,
                "g" / Int8ul,
                "b" / Int8ul,
                "a" / Int8ul,
            )
        )
    ),

    # Should be in multiply of FaceVerticesCount
    # It has FaceVerticesCount vertices for each face
    "FacesVertices" / PrefixedArray(Int16ul, Int16ul),

    "Frames" / Array(this.FramesCount,
        Struct(
            "Vertices" / Array(this._.VerticesCount,
                Struct(
                    "x" / Float32l,
                    "y" / Float32l,
                    "z" / Float32l,
                    # I am not sure if it is normals
                    If(this._._.HasNormals,
                        "Normal" / Struct(
                            "x" / Float32l,
                            "y" / Float32l,
                            "z" / Float32l,
                        )
                    )
                )
            )
        )
    )
)

def write_vertex(vertex):
    output.write("      vertex %f %f %f\n" % (vertex.x, vertex.z, vertex.y))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: mdl2stl.py mesh.bin"
        sys.exit(-1)

    if not sys.argv[1].endswith(".bin"):
        print "Expected .bin file"
        sys.exit(-1)

    mdl = MDL.parse(open(sys.argv[1], "rb").read())
    if not 3 <= mdl.FaceVerticesCount <= 4:
        print "Unsupported model"
        sys.exit(-1)
    # TODO: Colors (need to be binary stl)
    base_name = sys.argv[1][:-4]

    file_index = 0
    for mesh in mdl.Frames:
        if len(mdl.Frames) > 1:
            output = open(base_name + "_%d.stl" % file_index, "w")
            file_index += 1
        else:
            output = open(base_name + ".stl", "w")
        output.write("solid obj\n")
        for i in xrange(0, len(mdl.FacesVertices), mdl.FaceVerticesCount):
            face_vertices = [mesh.Vertices[x] for x in mdl.FacesVertices[i:i+mdl.FaceVerticesCount]]
            # TODO: normal per vertex (need other file format?)
            output.write("  facet normal 0 0 0\n")
            output.write("    outer loop\n")
            write_vertex(face_vertices[0])
            write_vertex(face_vertices[1])
            write_vertex(face_vertices[2])
            output.write("    endloop\n")
            output.write("  endfacet\n")
            if mdl.FaceVerticesCount == 4:
                # If it is quad-face, split it to two triangle faces
                output.write("  facet normal 0 0 0\n")
                output.write("    outer loop\n")
                write_vertex(face_vertices[0])
                write_vertex(face_vertices[2])
                write_vertex(face_vertices[3])
                output.write("    endloop\n")
                output.write("  endfacet\n")
        output.write("endsolid\n")
        output.close()
