#!/usr/bin/env python3
"""Convert modern Minecraft skin (64x64) to Allumeria skin format.

Allumeria uses smaller body parts than Minecraft, so the output is upscaled
to preserve detail from the input skin. Default output is 256x256 (4x scale).

Usage:
    python mc2allumeria.py input.png [output.png] [--scale 4] [--slim]
"""
import argparse
import sys
from pathlib import Path
from PIL import Image

# ============================================================================
# Minecraft UV Layout (64x64 modern format)
# Each face: (u, v, width, height)
# ============================================================================
MC_LAYOUT = {
    'head': {
        'top':    (8, 0, 8, 8),
        'bottom': (16, 0, 8, 8),
        'right':  (0, 8, 8, 8),
        'front':  (8, 8, 8, 8),
        'left':   (16, 8, 8, 8),
        'back':   (24, 8, 8, 8),
    },
    'head_overlay': {
        'top':    (40, 0, 8, 8),
        'bottom': (48, 0, 8, 8),
        'right':  (32, 8, 8, 8),
        'front':  (40, 8, 8, 8),
        'left':   (48, 8, 8, 8),
        'back':   (56, 8, 8, 8),
    },
    'body': {
        'top':    (20, 16, 8, 4),
        'bottom': (28, 16, 8, 4),
        'right':  (16, 20, 4, 12),
        'front':  (20, 20, 8, 12),
        'left':   (28, 20, 4, 12),
        'back':   (32, 20, 8, 12),
    },
    'body_overlay': {
        'top':    (20, 32, 8, 4),
        'bottom': (28, 32, 8, 4),
        'right':  (16, 36, 4, 12),
        'front':  (20, 36, 8, 12),
        'left':   (28, 36, 4, 12),
        'back':   (32, 36, 8, 12),
    },
    'arm_r': {
        'top':    (44, 16, 4, 4),
        'bottom': (48, 16, 4, 4),
        'left':  (40, 20, 4, 12),
        'front':  (44, 20, 4, 12),
        'right':   (48, 20, 4, 12),
        'back':   (52, 20, 4, 12),
    },
    'arm_r_overlay': {
        'top':    (44, 32, 4, 4),
        'bottom': (48, 32, 4, 4),
        'left':  (40, 36, 4, 12),
        'front':  (44, 36, 4, 12),
        'right':   (48, 36, 4, 12),
        'back':   (52, 36, 4, 12),
    },
    'arm_l': {
        'top':    (36, 48, 4, 4),
        'bottom': (40, 48, 4, 4),
        'left':  (32, 52, 4, 12),
        'front':  (36, 52, 4, 12),
        'right':   (40, 52, 4, 12),
        'back':   (44, 52, 4, 12),
    },
    'arm_l_overlay': {
        'top':    (52, 48, 4, 4),
        'bottom': (56, 48, 4, 4),
        'left':  (48, 52, 4, 12),
        'front':  (52, 52, 4, 12),
        'right':   (56, 52, 4, 12),
        'back':   (60, 52, 4, 12),
    },
    'leg_r': {
        'top':    (4, 16, 4, 4),
        'bottom': (8, 16, 4, 4),
        'left':  (0, 20, 4, 12),
        'front':  (4, 20, 4, 12),
        'right':   (8, 20, 4, 12),
        'back':   (12, 20, 4, 12),
    },
    'leg_r_overlay': {
        'top':    (4, 32, 4, 4),
        'bottom': (8, 32, 4, 4),
        'left':  (0, 36, 4, 12),
        'front':  (4, 36, 4, 12),
        'right':   (8, 36, 4, 12),
        'back':   (12, 36, 4, 12),
    },
    'leg_l': {
        'top':    (20, 48, 4, 4),
        'bottom': (24, 48, 4, 4),
        'left':  (16, 52, 4, 12),
        'front':  (20, 52, 4, 12),
        'right':   (24, 52, 4, 12),
        'back':   (28, 52, 4, 12),
    },
    'leg_l_overlay': {
        'top':    (4, 48, 4, 4),
        'bottom': (8, 48, 4, 4),
        'left':  (0, 52, 4, 12),
        'front':  (4, 52, 4, 12),
        'right':   (8, 52, 4, 12),
        'back':   (12, 52, 4, 12),
    },
}

# Alex (Slim) Arm UV Layouts (3px wide instead of 4px)
ALEX_LAYOUT = {
    'arm_r': {
        'top':    (44, 16, 3, 4),
        'bottom': (47, 16, 3, 4),
        'left':  (40, 20, 4, 12),
        'front':  (44, 20, 3, 12),
        'right':   (47, 20, 4, 12),
        'back':   (51, 20, 3, 12),
    },
    'arm_r_overlay': {
        'top':    (44, 32, 3, 4),
        'bottom': (47, 32, 3, 4),
        'left':  (40, 36, 4, 12),
        'front':  (44, 36, 3, 12),
        'right':   (47, 36, 4, 12),
        'back':   (51, 36, 3, 12),
    },
    'arm_l': {
        'top':    (36, 48, 3, 4),
        'bottom': (39, 48, 3, 4),
        'left':  (32, 52, 4, 12),
        'front':  (36, 52, 3, 12),
        'right':   (39, 52, 4, 12),
        'back':   (43, 52, 3, 12),
    },
    'arm_l_overlay': {
        'top':    (52, 48, 3, 4),
        'bottom': (55, 48, 3, 4),
        'left':  (48, 52, 4, 12),
        'front':  (52, 52, 3, 12),
        'right':   (55, 52, 4, 12),
        'back':   (59, 52, 3, 12),
    },
}

# ============================================================================
# Allumeria UV Layout (base 64x64)
# For cubes: (u, v, w, h, d) -> faces computed by cube_faces()
# ============================================================================
ALLUMERIA_LAYOUT = {
    'head':        {'type': 'cube', 'uv': (0, 0),    'size': (6, 6, 6)},
    'hat':         {'type': 'cube', 'uv': (0, 30),   'size': (7, 7, 7)},
    'neck':        {'type': 'cube', 'uv': (0, 26),   'size': (4, 1, 3)},
    'torso':       {'type': 'cube', 'uv': (0, 12),   'size': (6, 11, 3)},
    'arm_l':       {'type': 'cube', 'uv': (52, 49),  'size': (3, 12, 3)},
    'arm_r':       {'type': 'cube', 'uv': (40, 49),  'size': (3, 12, 3)},
    'leg_l':       {'type': 'cube', 'uv': (12, 49),  'size': (3, 12, 3)},
    'leg_r':       {'type': 'cube', 'uv': (0, 49),   'size': (3, 12, 3)},
    # Decorative planes are intentionally left empty/transparent
}

# ============================================================================
# Mapping: Allumeria part -> (Minecraft part, face_mapping)
# Note: Left and Right faces are swapped for limbs to correct mirroring.
# ============================================================================
PART_MAPPING = {
    'head':  ('head', {
        'top': 'top', 'bottom': 'bottom',
        'right': 'right', 'front': 'front',
        'left': 'left', 'back': 'back'
    }),
    'hat':   ('head_overlay', {
        'top': 'top', 'bottom': 'bottom',
        'right': 'right', 'front': 'front',
        'left': 'left', 'back': 'back'
    }),
    'torso': ('body', {
        'top': 'top', 'bottom': 'bottom',
        'right': 'right', 'front': 'front',
        'left': 'left', 'back': 'back'
    }),
    'arm_r': ('arm_r', {
        'top': 'top', 'bottom': 'bottom',
        'right': 'left', 'front': 'front',
        'left': 'right', 'back': 'back'
    }),
    'arm_l': ('arm_l', {
        'top': 'top', 'bottom': 'bottom',
        'right': 'left', 'front': 'front',
        'left': 'right', 'back': 'back'
    }),
    'leg_r': ('leg_r', {
        'top': 'top', 'bottom': 'bottom',
        'right': 'left', 'front': 'front',
        'left': 'right', 'back': 'back'
    }),
    'leg_l': ('leg_l', {
        'top': 'top', 'bottom': 'bottom',
        'right': 'left', 'front': 'front',
        'left': 'right', 'back': 'back'
    }),
}


def cube_faces(u, v, w, h, d):
    """Compute face regions for an Allumeria cube in base 64x64 coords."""
    return {
        'top':    (u + d, v, w, d),
        'bottom': (u + d + w, v, w, d),
        'right':  (u, v + d, d, h),
        'front':  (u + d, v + d, w, h),
        'left':   (u + d + w, v + d, d, h),
        'back':   (u + 2 * d + w, v + d, w, h),
    }


def convert_skin(input_path, output_path, scale=4, is_slim=False):
    """Convert Minecraft skin to Allumeria format."""
    # Load input skin
    mc_skin = Image.open(input_path).convert('RGBA')
    if mc_skin.size != (64, 64):
        print(f"Warning: Input skin is {mc_skin.size}, expected (64, 64). Resizing...")
        mc_skin = mc_skin.resize((64, 64), Image.Resampling.NEAREST)
    
    # Apply Slim (Alex) arm UVs if requested
    if is_slim:
        for part in ['arm_l', 'arm_l_overlay', 'arm_r', 'arm_r_overlay']:
            MC_LAYOUT[part] = ALEX_LAYOUT[part]
        print("Using Slim (Alex) arm UV layout.")
    
    # Create output image (transparent background)
    out_size = 64 * scale
    out_img = Image.new('RGBA', (out_size, out_size), (0, 0, 0, 0))
    
    # 1. Process Neck (Special case: uses top 1px of MC body)
    neck_info = ALLUMERIA_LAYOUT['neck']
    u, v = neck_info['uv']
    w, h, d = neck_info['size']
    neck_faces = cube_faces(u, v, w, h, d)
    
    # Extract top 1px layer from MC body side faces
    paste_face(mc_skin, out_img, (20, 20, 8, 1), neck_faces['front'], scale)
    paste_face(mc_skin, out_img, (32, 20, 8, 1), neck_faces['back'], scale)
    paste_face(mc_skin, out_img, (16, 20, 4, 1), neck_faces['right'], scale)
    paste_face(mc_skin, out_img, (28, 20, 4, 1), neck_faces['left'], scale)
    # Use top 1px layer of MC body top face for neck top
    paste_face(mc_skin, out_img, (20, 16, 8, 1), neck_faces['top'], scale)
    
    # 2. Process Cube parts
    for part_name, part_info in ALLUMERIA_LAYOUT.items():
        if part_info['type'] != 'cube' or part_name == 'neck':
            continue
        
        if part_name not in PART_MAPPING:
            continue
        
        u, v = part_info['uv']
        w, h, d = part_info['size']
        faces = cube_faces(u, v, w, h, d)
        
        mc_part, face_map = PART_MAPPING[part_name]
        
        for allum_face, mc_face in face_map.items():
            allum_region = faces[allum_face]
            mc_region = MC_LAYOUT[mc_part][mc_face]
            
            # Rotate the top face for both arms
            is_arm_top = part_name in ['arm_r', 'arm_l'] and allum_face == 'top'
            
            paste_face(mc_skin, out_img, mc_region, allum_region, scale, rotate=is_arm_top)
    
    # Save output
    out_img.save(output_path)
    print(f"Saved Allumeria skin to {output_path} ({out_size}x{out_size})")


def paste_face(mc_skin, out_img, mc_region, allum_region, scale, rotate=False):
    """Extract a face from MC skin and paste it into the output."""
    mc_u, mc_v, mc_w, mc_h = mc_region
    allum_u, allum_v, allum_w, allum_h = allum_region
    
    # Scale Allumeria region to output coords
    out_u = allum_u * scale
    out_v = allum_v * scale
    out_w = allum_w * scale
    out_h = allum_h * scale

    mc_face = mc_skin.crop((mc_u, mc_v, mc_u + mc_w, mc_v + mc_h))
    
    # Extract MC face and rotate 180 degrees counter-clockwise if requested
    if rotate:
        mc_face = mc_face.rotate(180, expand=True, resample=Image.Resampling.NEAREST)
    
    # Resize to fit Allumeria region in output (NEAREST preserves pixel art)
    mc_face = mc_face.resize((out_w, out_h), Image.Resampling.NEAREST)
    
    # Paste into output
    out_img.paste(mc_face, (out_u, out_v))


def main():
    parser = argparse.ArgumentParser(
        description='Convert Minecraft skin to Allumeria format',
        epilog='Example: python mc2allumeria.py steve.png steve_allumeria.png --scale 4 --slim'
    )
    parser.add_argument('input', help='Input Minecraft skin PNG (64x64)')
    parser.add_argument('output', nargs='?', help='Output Allumeria skin PNG')
    parser.add_argument('--scale', type=int, default=4,
                       help='Output scale factor (default: 4, output will be 64*scale x 64*scale)')
    parser.add_argument('--slim', action='store_true',
                       help='Use Slim (Alex) arm UV layout (3px wide arms)')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_name(input_path.stem + '_allumeria.png')
    
    convert_skin(input_path, output_path, args.scale, args.slim)


if __name__ == '__main__':
    main()