from construct import *
import sys

MDL = Struct("MDL",
    Bytes("Magic", 4),  # MDL\0
    # Flags
    EmbeddedBitStruct(
        BitField("UnusedFlags", 5),
        Flag("HasColors"),
        Flag("MaybeHasTextureCoordinates"),
        Flag("HasNormals"),
    ),
    ULInt8("FaceEdges"),  # 3 or 4
    ULInt16("VerticiesCount"),
    ULInt16("MeshesCount"),

    If(lambda ctx: ctx.MaybeHasTextureCoordinates,
        Array(lambda ctx: ctx.VerticiesCount,
            Struct("MaybeTextureCoordinates",
                LFloat32("x"),
                LFloat32("Y"),
            )
        )
    ),

    If(lambda ctx: ctx.HasColors,
        Array(lambda ctx: ctx.VerticiesCount,
            Struct("Colors",
                ULInt8("r"),
                ULInt8("g"),
                ULInt8("b"),
                ULInt8("a"),
            )
        )
    ),

    ULInt16("FacesEdgesCount"),
    Array(lambda ctx: ctx.FacesEdgesCount / ctx.FaceEdges,
        Struct("Faces",
            Array(lambda ctx: ctx._.FaceEdges, ULInt16("Verticies"))
        )
    ),

    Array(lambda ctx: ctx.MeshesCount,
        Struct("Meshes",
            Array(lambda ctx: ctx._.VerticiesCount,
                Struct("Verticies",
                    LFloat32("x"),
                    LFloat32("y"),
                    LFloat32("z"),
                    If(lambda ctx: ctx._._.HasNormals,
                        Struct("Normal",
                            LFloat32("x"),
                            LFloat32("y"),
                            LFloat32("z"),
                        )
                    )
                )
            )
        )
    )
)

def write_vertex(vertex):
    output.write("      vertex %f %f %f\n" % (vertex.x, vertex.y, vertex.z))

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
