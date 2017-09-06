from mdl2stl import MDL, FlagsContainer, Container
import pyassimp
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: 3d2mdl.py output.bin frame1_model [frame2_model [...]]"
        sys.exit(-1)

    try:
        scene = pyassimp.load(sys.argv[2])
    except:
        print "Failed to load %s" % sys.argv[2]
        sys.exit(-1)

    assert len(scene.meshes) == 1, "Support only one mesh per model"

    faces = scene.meshes[0].faces
    assert 3 <= len(scene.meshes[0].faces[0]) <= 4, "Support only 3 or 4 vertices per face"
    assert all(len(faces[0]) == len(x) for x in faces), "Inconsistency in faces vertices count"

    vertices = scene.meshes[0].vertices
    frames = [vertices]

    for i in xrange(3, len(sys.argv)):
        try:
            scene = pyassimp.load(sys.argv[i])
        except:
            print "Failed to load %s" % sys.argv[2]
            sys.exit(-1)

        assert len(vertices) == len(scene.meshes[0].vertices), "Different number of vertices between the different models"
        frames.append(scene.meshes[0].vertices)

    mdl = MDL.build(Container(Flags=FlagsContainer(HasNormals=False,
                                                   HasUnknown=False,
                                                   HasColors=False),
                              UnknownList=None,
                              Colors=None,
                              FaceVerticesCount=len(faces[0]),
                              VerticesCount=len(vertices),
                              FramesCount=len(frames),
                              FacesVertices=reduce(lambda x, y: x + list(map(int,y)), faces, []),
                              Frames=[Container(Vertices=[Container(x=vertex[0], z=vertex[1], y=vertex[2], Normal=None) for vertex in vertices]) for vertices in frames]
                              ))

    open(sys.argv[1], "wb").write(mdl)
