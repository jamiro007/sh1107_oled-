#!/usr/bin/env python3
"""
Example usage of SH1107G OLED display with Luma.OLED library

This script demonstrates basic text display, graphics drawing,
and system information monitoring.
"""

import time
from oled_luma import SH1107Luma


def main():
    """Main example function"""
    print("SH1107G OLED Display Example")
    print("=" * 40)
    
    try:
        # Initialize display
        oled = SH1107Luma(i2c_addr=0x3C, i2c_port=1, rotate=0)
        
        print("1. Displaying welcome message...")
        oled.clear()
        lines = [
            "SH1107 OLED Demo",
            "128x128 Pixels",
            "Luma.OLED Library",
            "Raspberry Pi 4"
        ]
        oled.display_multiline_text(lines, font_size=10)
        time.sleep(3)
        
        print("2. Drawing graphics...")
        oled.clear()
        
        # Draw borders
        oled.draw_rectangle(0, 0, 127, 127, outline="white")
        oled.draw_rectangle(10, 10, 117, 117, outline="white")
        
        # Draw centered ellipse
        oled.draw_ellipse(30, 40, 97, 87, outline="white", fill="white")
        
        time.sleep(3)
        
        print("3. Displaying system info...")
        oled.clear()
        
        # Try to get system information
        try:
            import psutil
            
            cpu_usage = psutil.cpu_percent()
            mem_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            info_text = [
                f"CPU: {cpu_usage:.1f}%",
                f"RAM: {mem_usage:.1f}%",
                f"Disk: {disk_usage:.1f}%"
            ]
            oled.display_multiline_text(info_text, font_size=12)
            
            time.sleep(5)
            
        except ImportError:
            print("psutil library not installed")
            oled.display_text(10, 40, "Install psutil", font_size=10)
            oled.display_text(10, 55, "for system info", font_size=10)
            time.sleep(3)
            
        print("4. Displaying dynamic text...")
        oled.clear()
        
        # Show a simple scrolling effect
        for i in range(0, 100, 2):
            oled.clear()
            oled.display_text(i, 50, "Scrolling Text", font_size=12)
            time.sleep(0.05)
            
        time.sleep(2)
        
        print("5. Final message...")
        oled.clear()
        oled.display_multiline_text(["Demo Complete!", "Thanks for watching!"], font_size=11)
        time.sleep(3)
        
        print("6. Clearing display...")
        oled.clear()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Cleaning up...")


if __name__ == "__main__":
    main()
