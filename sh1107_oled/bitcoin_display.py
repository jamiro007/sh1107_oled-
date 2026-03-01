#!/usr/bin/env python3
"""
Simple Bitcoin Logo Display for SH1107G OLED Display

This script displays an embedded Bitcoin logo on the 128x128 SH1107G OLED display.

Usage:
    python bitcoin_display.py           # Run on Raspberry Pi with OLED
    python bitcoin_display.py --test   # Save preview without hardware
"""

import sys
import os
import time
import base64
from io import BytesIO
from PIL import Image

# Only import OLED driver when not in test mode
if len(sys.argv) > 1 and sys.argv[1] == '--test':
    TEST_MODE = True
else:
    TEST_MODE = False
    from oled_luma import SH1107Luma

# Embedded Bitcoin logo image (BTC_124x128_4bpp.png) - base64 encoded
BITCOIN_LOGO_PNG = b'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'


def rotate_image(image, angle):
    """Rotate image by given angle, expanding to fit"""
    # Rotate with expansion to fit entire rotated image
    rotated = image.rotate(angle, resample=Image.BILINEAR, expand=True)
    
    # Create 128x128 canvas and center the rotated image
    canvas = Image.new('1', (128, 128), 1)  # White background
    
    # Calculate position to center
    x_offset = (128 - rotated.width) // 2
    y_offset = (128 - rotated.height) // 2
    
    # Paste centered
    canvas.paste(rotated, (x_offset, y_offset))
    return canvas


def main():
    """Main function - display rotating Bitcoin logo"""
    print("Bitcoin Logo Rotation Display")
    print("=" * 40)
    
    # Decode base64 image
    img_data = base64.b64decode(BITCOIN_LOGO_PNG)
    base_img = Image.open(BytesIO(img_data))
    print(f"Loaded image: {base_img.size}, mode: {base_img.mode}")
    
    # Resize to exactly 128x128 for OLED display
    if base_img.size != (128, 128):
        base_img = base_img.resize((128, 128), Image.Resampling.LANCZOS)
    
    # Convert to 1-bit (black and white) for OLED
    base_img = base_img.convert('1')
    print(f"Base image: {base_img.size}, mode: {base_img.mode}")
    
    # Pre-generate rotation frames (36 frames = 10 degrees per frame for smooth rotation)
    num_frames = 36
    frames = []
    print(f"Generating {num_frames} rotation frames...")
    
    for i in range(num_frames):
        angle = i * (360 / num_frames)
        rotated = rotate_image(base_img, angle)
        frames.append(rotated)
    
    print(f"Generated {len(frames)} frames")
    
    # Test mode: Save first frame as PNG for preview
    if TEST_MODE:
        print("\nTest mode: Saving preview...")
        output_dir = "bitcoin_frames"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save a few frames for preview
        for i in [0, 9, 18, 27]:
            preview_path = f"{output_dir}/bitcoin_rotated_{i:02d}.png"
            frames[i].save(preview_path)
            print(f"Saved frame {i} to {preview_path}")
        return
    
    # Normal mode: Display on OLED
    try:
        # Initialize display
        oled = SH1107Luma(i2c_addr=0x3C, i2c_port=1, rotate=0)
        
        print("Displaying rotating Bitcoin logo...")
        print("Press Ctrl+C to exit")
        
        frame_idx = 0
        while True:
            # Display current frame
            oled.device.display(frames[frame_idx])
            
            # Move to next frame
            frame_idx = (frame_idx + 1) % num_frames
            
            # Control rotation speed (~40 FPS = 0.9 seconds per full rotation, 4x speed)
            time.sleep(0.025)
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clear display before exiting
        try:
            oled.clear()
        except:
            pass
        print("Cleaning up...")


if __name__ == "__main__":
    main()
