import parse_scene
from PIL import Image, ImageOps
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

    for layer in scene.Layers:
        layer_image = Image.new("RGB", (layer.Width * 16, layer.Height * 16), (255, 0, 255))
        for x in xrange(layer.Width):
            for y in xrange(layer.Height):
                tile = layer.Tiles[y * layer.Width + x]
                if tile != 0xffff:
                    tile_image = tiles[tile & 0x3ff]
                    if (tile >> 10) & 1:
                        tile_image = ImageOps.mirror(tile_image)
                    if (tile >> 10) & 2:
                        tile_image = ImageOps.flip(tile_image)
                    layer_image.paste(tile_image, (x * 16, y * 16, x * 16 + 16, y * 16 + 16))
        layer_image.save(os.path.join(os.path.dirname(sys.argv[1]), os.path.basename(sys.argv[1]) + "-" + layer.Name.strip('\0') + ".png"))
