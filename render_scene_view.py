import parse_scene
from PIL import Image
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: render_scene_view.py SceneX.bin")
        sys.exit(-1)

    if not sys.argv[1].endswith(".bin"):
        print("Expected .bin file")
        sys.exit(-1)

    scene = parse_scene.SCN.parse(open(sys.argv[1], "rb").read())
    try:
        tiles_image = Image.open(os.path.join(os.path.dirname(sys.argv[1]), "16x16Tiles.gif"))
    except:
        print("Failed to open 16x16Tiles.gif")
        sys.exit(-1)

    tiles = []
    for i in xrange(0x400):
        tiles.append(tiles_image.crop((0, i * 16, 16, i * 16 + 16)))

    for view in scene.Views:
        view_image = Image.new("RGB", (view.Width * 16, view.Height * 16), (255, 0, 255))
        for x in xrange(view.Width):
            for y in xrange(view.Height):
                tile = view.Tiles[y * view.Width + x]
                if tile != 0xffff:
                    view_image.paste(tiles[tile & 0x3ff], (x * 16, y * 16, x * 16 + 16, y * 16 + 16))
        view_image.save(os.path.join(os.path.dirname(sys.argv[1]), os.path.basename(sys.argv[1]) + "-" + view.Name.strip('\0') + ".png"))
