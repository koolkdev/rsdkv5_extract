from construct import *
import sys

MDL = Struct(
    "Magic" / Const("MDL\0"),
    # Flags
    Embedded(FlagsEnum(Int8ul,
        HasNormals=1,
        MaybeHasTextureCoordinates=2,
        HasColors=4)),
    "FaceEdges" / Int8ul,  # 3 or 4
    "VerticiesCount" / Int16ul,
    "MeshesCount" / Int16ul,

    If(lambda ctx: ctx.MaybeHasTextureCoordinates,
        "MaybeTextureCoordinates" / Array(this.VerticiesCount,
            Struct(
                "x" / Float32l,
                "y" / Float32l,
            )
        )
    ),

    If(lambda ctx: ctx.HasColors,
        "Colors" / Array(this.VerticiesCount,
            Struct(
                "r" / Int8ul,
                "g" / Int8ul,
                "b" / Int8ul,
                "a" / Int8ul,
            )
        )
    ),

    "FacesEdgesCount" / Int16ul,
    "Faces" / Array(this.FacesEdgesCount / this.FaceEdges,
        Struct(
            "Verticies" / Array(this._.FaceEdges, Int16ul)
        )
    ),

    "Meshes" / Array(this.MeshesCount,
        Struct(
            "Verticies" / Array(this._.VerticiesCount,
                Struct(
                    "x" / Float32l,
                    "y" / Float32l,
                    "z" / Float32l,
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
    if not 3 <= mdl.FaceEdges <= 4:
        print "Unsupported model"
        sys.exit(-1)
    # TODO: Colors (need to be binary stl)
    base_name = sys.argv[1][:-4]

    file_index = 0
    for mesh in mdl.Meshes:
        if len(mdl.Meshes) > 1:
            output = open(base_name + "_%d.stl" % file_index, "w")
            file_index += 1
        else:
            output = open(base_name + ".stl", "w")
        output.write("solid obj\n")
        for face in mdl.Faces:
            # TODO: normal per vertex (need other file format?)
            output.write("  facet normal 0 0 0\n")
            output.write("    outer loop\n")
            write_vertex(mesh.Verticies[face.Verticies[0]])
            write_vertex(mesh.Verticies[face.Verticies[1]])
            write_vertex(mesh.Verticies[face.Verticies[2]])
            output.write("    endloop\n")
            output.write("  endfacet\n")
            if mdl.FaceEdges == 4:
                output.write("  facet normal 0 0 0\n")
                output.write("    outer loop\n")
                write_vertex(mesh.Verticies[face.Verticies[0]])
                write_vertex(mesh.Verticies[face.Verticies[2]])
                write_vertex(mesh.Verticies[face.Verticies[3]])
                output.write("    endloop\n")
                output.write("  endfacet\n")
        output.write("endsolid\n")
        output.close()
