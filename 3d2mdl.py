from mdl2stl import MDL, FlagsContainer, Container
import pyassimp
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: 3d2mdl.py output.bin frame1_model [frame2_model [...]]"
        sys.exit(-1)

    scenes = []

    for i in xrange(2, len(sys.argv)):
        try:
            scenes.append(pyassimp.load(sys.argv[i]))
        except:
            print "Failed to load %s" % sys.argv[i]
            sys.exit(-1)

        assert all(3 <= len(mesh.faces[0]) <= 4 for mesh in scenes[-1].meshes), "Support only 3 or 4 vertices per face"
        assert all(all(len(mesh.faces[0]) == len(x) for x in mesh.faces) for mesh in scenes[-1].meshes), "Inconsistency in faces vertices count"

        if len(scenes) > 1:
            assert sum(len(mesh.vertices) for mesh in scenes[-1].meshes) == sum(len(mesh.vertices) for mesh in scenes[0].meshes), "Different number of vertices between the different models"

    has_rgb_colors = False
    has_material = False
    if any(len(mesh.colors) > 0 for mesh in scenes[0].meshes):
        has_rgb_colors = True
    elif any(material.properties["name"] != u'DefaultMaterial' for material in scenes[0].materials):
        has_material = True

    faces = []
    if has_rgb_colors or has_material:
        colors = []
    else:
        colors = None

    # Fill colors and faces
    vertices_count = 0
    for mesh in scenes[0].meshes:
        faces.extend([x + vertices_count for x in face] for face in mesh.faces)
        vertices_count += len(mesh.vertices)

        if has_rgb_colors:
            if len(mesh.colors) > 0:
                colors.extend(Container(r=int(color[0] * 255), g=int(color[1] * 255), b=int(color[2] * 255), a=int(color[3] * 255)) for color in mesh.colors)
            else:
                colors.extend(Container(r=200, g=200, b=200, a=255) for color in len(xrange(mesh.vertices)))
        elif has_material:
            rgb = [int(255 * (mesh.material.properties["diffuse"][i] ** (1/2.2))) for i in xrange(3)]
            colors.extend(Container(r=rgb[0], g=rgb[1], b=rgb[2], a=255) for i in xrange(len(mesh.vertices)))

    print "Frames: %d" % (len(sys.argv) - 2)
    print "Faces: %d" % (len(faces))
    print "Vertices: %d" % (vertices_count)
    if has_rgb_colors:
        print "Colors: yes"
    elif has_material:
        print "Colors: yes (from material)"
    else:
        print "Colors: no"

    frames = []
    if has_rgb_colors or has_material or any(any(len(mesh.normals) > 0 for mesh in scene.meshes) for scene in scenes):
        frames_normals = []
        print "Normals: yes"
    else:
        frames_normals = None
        print "Normals: no"

    for scene in scenes:
        vertices = []
        vertices_normals = []

        frames.append([])
        if frames_normals is not None:
            frames_normals.append([])

        for mesh in scene.meshes:
            frames[-1].extend(mesh.vertices)
            if frames_normals is not None:
                if len(mesh.normals) > 0:
                    frames_normals[-1].extend(scene.meshes[0].normals)
                else:
                    frames_normals[-1].extend([0., 0., 0.] for i in xrange(len(scene.vertices)))

    if frames_normals is None:
        frames_vertices = [Container(Vertices=[Container(x=vertex[0], y=vertex[1], z=vertex[2], Normal=None) for vertex in vertices]) for vertices in frames]
    else:
        frames_vertices = [Container(Vertices=[Container(x=vertex[0], y=vertex[1], z=vertex[2],
                                     Normal=Container(x=normal[0], y=normal[1], z=normal[2])) for vertex, normal in zip(vertices, normals)]) for vertices, normals in zip(frames, frames_normals)]

    mdl = MDL.build(Container(Flags=FlagsContainer(HasNormals=frames_vertices is not None,
                                                   HasUnknown=False,
                                                   HasColors=colors is not None),
                              UnknownList=None,
                              Colors=colors,
                              FaceVerticesCount=len(faces[0]),
                              VerticesCount=vertices_count,
                              FramesCount=len(frames),
                              FacesVertices=reduce(lambda x, y: x + list(map(int,y)), faces, []),
                              Frames=frames_vertices
                              ))

    open(sys.argv[1], "wb").write(mdl)
