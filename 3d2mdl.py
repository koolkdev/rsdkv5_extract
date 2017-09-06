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

    if len(scene.meshes[0].colors) > 0:
        colors = [Container(r=color[0], g=color[1], b=color[2], a=color[3]) for color in scene.meshes[0].colors]
    else:
        colors = None

    if len(scene.meshes[0].normals) > 0:
        frames_normals = [scene.meshes[0].normals]
    else:
        frames_normals = None

    for i in xrange(3, len(sys.argv)):
        try:
            scene = pyassimp.load(sys.argv[i])
        except:
            print "Failed to load %s" % sys.argv[2]
            sys.exit(-1)

        assert len(vertices) == len(scene.meshes[0].vertices), "Different number of vertices between the different models"
        frames.append(scene.meshes[0].vertices)
        if frames_normals is not None:
            frames_normals.append(scene.meshes[0].normals)

    has_normals = False
    if frames_normals is None:
        if colors is not None:
            # Create empty normals for the colors
            frames_vertices = [Container(Vertices=[Container(x=vertex[0], z=vertex[1], y=vertex[2], Normal=Container(x=0, z=0, y=0)) for vertex in vertices]) for vertices in frames]
            has_normals = True
        else:
            frames_vertices = [Container(Vertices=[Container(x=vertex[0], z=vertex[1], y=vertex[2], Normal=None) for vertex in vertices]) for vertices in frames]
    else:
        frames_vertices = [Container(Vertices=[Container(x=vertex[0], z=vertex[1], y=vertex[2],
                                     Normal=Container(x=normal[0], z=normal[1], y=normal[2])) for vertex, normal in zip(vertices, normals)]) for vertices, normals in zip(frames, frames_normals)]
        has_normals = True

    mdl = MDL.build(Container(Flags=FlagsContainer(HasNormals=has_normals,
                                                   HasUnknown=False,
                                                   HasColors=colors is not None),
                              UnknownList=None,
                              Colors=colors,
                              FaceVerticesCount=len(faces[0]),
                              VerticesCount=len(vertices),
                              FramesCount=len(frames),
                              FacesVertices=reduce(lambda x, y: x + list(map(int,y)), faces, []),
                              Frames=frames_vertices
                              ))

    open(sys.argv[1], "wb").write(mdl)
