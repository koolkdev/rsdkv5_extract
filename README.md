# Sonic Mania Tools

### [Download (Windows binary)](https://github.com/koolkdev/rsdkv5_extract/releases)

## Data.rsdk status
Named files:  1677/1677 (100%)
Decrypted files: 1677/1677 (100%)

## File formats and tools
**RSDK (.rsdk)** - Retro SDK Archive -  Archive of all the files
* rsdkv5_extract.py - extract archive
* rsdkv5_pack.py - pack the archive back

**MDL (.bin)** - 3D Models,  Data/Meshes/\*/\*.bin
* mdl2stl.py - convert the model to stl
* 3d2mdl - convert any 3d model to bin

**SPR (.bin)** - Sprites info, Data/Sprites/\*/\*.bin

**SCN (.bin)** - Scenario info, Data/Stages/\*/Scene\*.bin
* parse_scene_view.py - SceneX.bin parser
* render_scene_view.py - render levels to png

**TIL (.bin)** - Tile configuration for stage, Data/Stages/\*/TileConfig.bin

**CFG (.bin)** - Configuration file, Data/Game/GameConfig.bin and for stages at Data/Stages/\*/StageConfig.bin
* parse_game_config.py GameConfig.bin parser
* parse_stage_config.py StageConfig.bin parser
* palette_editor.py - palette editor for GameConfig.bin and StageConfig.bin

**OBJ (.bin)** - Static object files Data/Objects/Static/\*.bin. The name of the file is the hash of the name of the object.
