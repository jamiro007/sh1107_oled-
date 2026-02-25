#!/usr/bin/env python3
"""
SH1107G OLED Display Driver using Luma.OLED Library

Hardware:
- 1.12" OLED Display with 128x128 resolution
- SH1107G Driver IC
- I2C Interface (default address: 0x3C)

Connection (Raspberry Pi 4):
- I2C SCL -> GPIO 3 (Pin 5)
- I2C SDA -> GPIO 2 (Pin 3)
- I2C Address: 0x3C (or 0x3D depending on hardware)

Uses luma.oled library for communication.

Installation:
    sudo apt-get update
    sudo apt-get install python3-pip python3-pil libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 -y
    sudo pip3 install luma.oled

Usage:
    python oled_luma.py           # Use default address 0x3C
    python oled_luma.py 0x3D      # Use address 0x3D
"""

import time
import sys
from luma.core.interface.serial import i2c
from luma.oled.device import sh1107
from luma.core.render import canvas
from PIL import ImageFont


class SH1107Luma:
    """SH1107G OLED Display Driver using Luma.OLED library"""
    
    def __init__(self, i2c_addr=0x3C, i2c_port=1, rotate=0):
        """Initialize display instance"""
        self.i2c_addr = i2c_addr
        self.i2c_port = i2c_port
        self.rotate = rotate
        self.serial = None
        self.device = None
        self.initialized = False
        
        # Initialize I2C interface
        try:
            self.serial = i2c(port=self.i2c_port, address=self.i2c_addr)
            self.device = sh1107(self.serial, width=128, height=128, rotate=self.rotate)
            self.initialized = True
            print("Display initialized successfully")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize display: {e}")
    
    def display_text(self, x, y, text, font_size=12, fill="white"):
        """Display text at specified position"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
        
        # Try to load system font or use default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        with canvas(self.device) as draw:
            draw.text((x, y), text, font=font, fill=fill)
    
    def display_multiline_text(self, lines, font_size=10, fill="white"):
        """Display multiple lines of text"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
            
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        with canvas(self.device) as draw:
            y_offset = 0
            for line in lines:
                draw.text((10, 10 + y_offset), line, font=font, fill=fill)
                y_offset += font_size + 2
                
    def draw_rectangle(self, x1, y1, x2, y2, fill=None, outline="white"):
        """Draw a rectangle - accepts coordinates in any order"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
            
        # Normalize coordinates
        x_min = min(x1, x2)
        x_max = max(x1, x2)
        y_min = min(y1, y2)
        y_max = max(y1, y2)
        
        # Ensure coordinates are within display bounds
        x_min = max(0, x_min)
        x_max = min(127, x_max)
        y_min = max(0, y_min)
        y_max = min(127, y_max)
        
        with canvas(self.device) as draw:
            draw.rectangle([x_min, y_min, x_max, y_max], outline=outline, fill=fill)
            
    def draw_ellipse(self, x1, y1, x2, y2, fill=None, outline="white"):
        """Draw an ellipse - accepts coordinates in any order"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
            
        # Normalize coordinates
        x_min = min(x1, x2)
        x_max = max(x1, x2)
        y_min = min(y1, y2)
        y_max = max(y1, y2)
        
        # Ensure coordinates are within display bounds
        x_min = max(0, x_min)
        x_max = min(127, x_max)
        y_min = max(0, y_min)
        y_max = min(127, y_max)
        
        with canvas(self.device) as draw:
            draw.ellipse([x_min, y_min, x_max, y_max], outline=outline, fill=fill)
            
    def clear(self):
        """Clear the display"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
            
        self.device.clear()
        
    def set_contrast(self, level):
        """Set display contrast (0-255)"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
            
        self.device.contrast(level)
        
    def invert_display(self, invert=True):
        """Invert display colors"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
            
        self.device.invert(invert)
        
    def display_on(self):
        """Turn display on"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
            
        self.device.show()
        
    def display_off(self):
        """Turn display off"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
            
        self.device.hide()


def demo_basic(oled):
    """Basic demonstration"""
    print("Running basic demo...")
    
    # Clear display
    oled.clear()
    time.sleep(0.5)
    
    # Display text
    print("Showing text...")
    lines = [
        "Raspi 4 Online",
        "Grove OLED",
        "SH1107G Driver",
        "Luma.OLED Lib"
    ]
    oled.display_multiline_text(lines, font_size=11)
    time.sleep(2)
    
    # Show rectangle
    print("Showing rectangle...")
    oled.clear()
    oled.draw_rectangle(10, 10, 118, 118, outline="white", fill=None)
    oled.draw_rectangle(20, 20, 108, 108, outline="white", fill=None)
    time.sleep(2)
    
    # Show ellipse
    print("Showing ellipse...")
    oled.clear()
    oled.draw_ellipse(30, 30, 98, 98, outline="white", fill="white")
    time.sleep(2)
    
    # Display system info
    print("Showing system info...")
    oled.clear()
    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
        mem_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        info_lines = [
            f"CPU: {cpu_percent:.1f}%",
            f"RAM: {mem_percent:.1f}%",
            f"Disk: {disk_percent:.1f}%"
        ]
        oled.display_multiline_text(info_lines, font_size=12)
        time.sleep(3)
        
    except ImportError:
        print("psutil library not installed. Skipping system info.")
        oled.display_text(10, 40, "Install psutil", font_size=10)
        time.sleep(2)


def demo_advanced(oled):
    """Advanced demonstration with animations"""
    print("Running advanced demo...")
    
    # Animation effect (ensure valid coordinates)
    max_steps = min(64, 128 // 2)  # Ensure we don't go beyond center
    for i in range(0, max_steps, 2):
        oled.clear()
        x1 = i
        y1 = i
        x2 = 127 - i
        y2 = 127 - i
        
        if x1 <= x2 and y1 <= y2:
            oled.draw_rectangle(x1, y1, x2, y2, outline="white", fill=None)
            
        time.sleep(0.05)
        
    time.sleep(1)


def main():
    """Main entry point"""
    # Parse command line arguments
    i2c_addr = 0x3C
    if len(sys.argv) > 1:
        try:
            addr = sys.argv[1]
            if addr.startswith('0x'):
                i2c_addr = int(addr, 16)
            else:
                i2c_addr = int(addr)
            print(f"Using I2C address: 0x{i2c_addr:02X}")
        except ValueError:
            print(f"Invalid address: {sys.argv[1]}")
            sys.exit(1)
    
    print("=" * 50)
    print("SH1107G OLED Display Test (Luma.OLED)")
    print("=" * 50)
    
    try:
        # Initialize display
        oled = SH1107Luma(i2c_addr=i2c_addr, i2c_port=1, rotate=0)
        
        print("\n1. Running basic demo...")
        demo_basic(oled)
        
        print("\n2. Running advanced demo...")
        demo_advanced(oled)
        
        print("\n3. Displaying final message...")
        oled.clear()
        oled.display_multiline_text(["Demo Complete!", "Press Ctrl+C to exit"], font_size=12)
        
        print("\nPress Ctrl+C to exit...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
