import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_logo():
    print("Generating premium application icon assets...")
    
    # 1. Ensure target directory exists
    assets_dir = Path("app/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    ico_path = assets_dir / "app.ico"
    
    # 2. Base Size for High-Res Icon
    base_size = 256
    img = Image.new("RGBA", (base_size, base_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 3. Draw a premium rounded gradient background
    # We will simulate a linear gradient from top-left to bottom-right
    for y in range(base_size):
        for x in range(base_size):
            # Calculate distance/gradient factor
            factor = (x + y) / (2 * base_size)
            # Interpolate between primary blue (#1F6AA5) and deep navy (#0A2239)
            r = int(0x1F + (0x0A - 0x1F) * factor)
            g = int(0x6A + (0x22 - 0x6A) * factor)
            b = int(0xA5 + (0x39 - 0xA5) * factor)
            
            # Draw only inside a rounded box boundaries
            # Rounded corner check: padding of 12px
            pad = 12
            r_corner = 48
            
            # Bounding box check
            if pad <= x < (base_size - pad) and pad <= y < (base_size - pad):
                # Calculate if inside rounded corners
                in_corner = False
                # Top-Left Corner
                if x < pad + r_corner and y < pad + r_corner:
                    if (x - (pad + r_corner))**2 + (y - (pad + r_corner))**2 > r_corner**2:
                        in_corner = True
                # Top-Right Corner
                elif x >= base_size - pad - r_corner and y < pad + r_corner:
                    if (x - (base_size - pad - r_corner))**2 + (y - (pad + r_corner))**2 > r_corner**2:
                        in_corner = True
                # Bottom-Left Corner
                elif x < pad + r_corner and y >= base_size - pad - r_corner:
                    if (x - (pad + r_corner))**2 + (y - (base_size - pad - r_corner))**2 > r_corner**2:
                        in_corner = True
                # Bottom-Right Corner
                elif x >= base_size - pad - r_corner and y >= base_size - pad - r_corner:
                    if (x - (base_size - pad - r_corner))**2 + (y - (base_size - pad - r_corner))**2 > r_corner**2:
                        in_corner = True
                
                if not in_corner:
                    draw.point((x, y), fill=(r, g, b, 255))

    # 4. Draw Inner Accent border ring
    # A sleek thin cyan glowing border
    draw.rounded_rectangle(
        [15, 15, base_size - 15, base_size - 15],
        radius=44,
        outline=(0x3A, 0x9A, 0xD9, 120),
        width=4
    )

    # 5. Draw stylized keyboard key icon inside
    # Keyboard cap border
    key_x1, key_y1 = 68, 68
    key_x2, key_y2 = 188, 188
    
    # Shadow/3D offset
    draw.rounded_rectangle(
        [key_x1, key_y1 + 8, key_x2, key_y2 + 8],
        radius=20,
        fill=(0x0D, 0x1B, 0x2A, 180)
    )
    # Key face
    draw.rounded_rectangle(
        [key_x1, key_y1, key_x2, key_y2],
        radius=20,
        fill=(0xFC, 0xFC, 0xFF, 255),
        outline=(0xD0, 0xD0, 0xD8, 255),
        width=3
    )
    # Inner key inset depth
    draw.rounded_rectangle(
        [key_x1 + 8, key_y1 + 8, key_x2 - 8, key_y2 - 8],
        radius=14,
        outline=(0xE5, 0xE5, 0xEA, 255),
        width=2
    )

    # 6. Draw clean stylized keyboard character symbol "A" in the center of the key cap
    # We use a built-in default font or draw manually to ensure no OS font mismatches
    # Let's draw a nice clean geometric letter 'A' using lines for 100% platform independence
    # Center is (128, 128)
    # Let's draw an A of height ~50px, width ~36px
    cx, cy = 128, 124
    w, h = 18, 26
    
    # Draw thicker geometric strokes for high visibility
    # Left leg: (cx - w, cy + h) to (cx, cy - h)
    # Right leg: (cx + w, cy + h) to (cx, cy - h)
    # Crossbar: (cx - w/2, cy + h/3) to (cx + w/2, cy + h/3)
    line_color = (0x1F, 0x6A, 0xA5, 255)
    draw.line([(cx - w, cy + h), (cx, cy - h)], fill=line_color, width=8)
    draw.line([(cx + w, cy + h), (cx, cy - h)], fill=line_color, width=8)
    draw.line([(cx - int(w*0.6), cy + int(h*0.15)), (cx + int(w*0.6), cy + int(h*0.15))], fill=line_color, width=7)

    # 7. Save as multi-size Windows .ico file
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=sizes)
    print(f"[SUCCESS] Multi-resolution icon saved to: {ico_path.resolve()}")

if __name__ == "__main__":
    generate_logo()
