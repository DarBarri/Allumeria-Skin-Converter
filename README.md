# Minecraft to Allumeria Skin Converter

A Python script to convert modern Minecraft skins (64x64) into the Allumeria skin format. Because Allumeria uses smaller body parts than Minecraft, script automatically upscales the output. 

![alt text](https://github.com/DarBarri/Allumeria-skin-converter/blob/main/Screenshot.jpg?raw=true)

## Features
- Converts standard 64x64 Minecraft skins to Allumeria format.
- Upscales output to 256x256 by default to maintain crisp pixel art.
- Supports Slim 3px-wide skins arm models via the `--slim` flag.
- Uses nearest-neighbor resampling to prevent blurry textures.

## Requirements
- Python 3.x
- [Pillow](https://pillow.readthedocs.io/)

## Usage

```bash
python Allumeria-skin-converter.py input.png [output.png] [--scale 4] [--slim]
```

## Arguments

    input: Input Minecraft skin PNG (must be 64x64).
    output: (Optional) Output Allumeria skin PNG. Defaults to <input_name>_allumeria.png.
    --scale: Output scale factor (default: 4).
    --slim: Use the Slim arm UV layout (3px wide arms).

Example: 
    python Allumeria-skin-converter.py alex.png --slim

## Known Bugs

Allumeria >64x64 Texture Bug: Allumeria itself turns any skins higher than 64x64 into a chaotic mess for online players.

![alt text](https://github.com/DarBarri/Allumeria-skin-converter/blob/main/online%20bug.jpg?raw=true)
