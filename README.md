# Sonic Main Tools

## [Download (.exe in .zip)](https://ci.appveyor.com/project/koolkdev/rsdkv5-extract/build/artifacts)

## Data.rsdk status
Named files:  1664/1677 (99.22%)  
Decrypted files: 1674/1677 (99.82%)

## File formats
**RSDK (.rsdk)** - Retro SDK Archive -  Archive of all the files, can be extracted with rsdkv5_extract.py and repacked with rsdkv5_pack.py

**MDL (.bin)** - 3D Models,  Data/Meshes/\*/\*.bin. can be convetered to stl with mdl2stl.py

**SPR (.bin)** - Sprites info, Data/Sprites/\*/\*.bin

**SCN (.bin)** - Scenario info, Data/Stages/\*/Scene\*.bin

**TIL (.bin)** - Tile configuration for stage, Data/Stages/\*/TileConfig.bin

**CFG (.bin)** - Configuration file, Data/Game/GameConfig.bin and for stages at Data/Stages/\*/StageConfig.bin

**OBJ (.bin)** - Static object files Data/Objects/Static/\*.bin. The name of the file is the hash of the name of the object.
