# Sonic Mania Tools

### [Download (Windows binary)](https://github.com/Axanery/rsdkv5_extract_plus/releases)
### [Mod Loader Tutorial](https://www.youtube.com/watch?v=Kl2pKkaqklY)
### [Extraction Tutorial (for this tool)](https://www.youtube.com/watch?v=8oxISJxgBc4)

## Data.rsdk status
Fully extracted.

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

Credits:  
[koolkdev](https://github.com/koolkdev)- Making the original tool  
[Axanery](https://youtube.com/c/Axanery) - Finding Mania Plus/1.07 file names  
[M&M](https://github.com/ActualMandM) - Finding Mania Plus file names  
[RandomTalkingBush](https://twitter.com/RandomTBush) - Finding Mania Plus file names  
[SuperSonic16](https://github.com/thesupersonic16) - Finding Mania Plus file names  
[Rubberduckycooly](https://twitter.com/Rubberduckcooly) - Finding Mania Plus file names  
[Tpot](https://github.com/Tpot-SSL) - Finding Mania Plus file names
