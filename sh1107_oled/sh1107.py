#!/usr/bin/env python3
"""
SH1107G OLED Display Driver

Hardware:
- 1.12" OLED Display with 128x128 resolution
- SH1107G Driver IC
- I2C Interface (default address: 0x3C)

Connection:
- I2C SCL -> FT4222 Port A SCK
- I2C SDA -> FT4222 Port A MOSI
- I2C Address: 0x3C (or 0x3D depending on hardware)

Uses pyusb for FT4222 communication.

Usage:
    python sh1107.py           # Use default address 0x3C
    python sh1107.py 0x3D    # Use address 0x3D
"""

import time
import sys
import usb.core
import usb.util

# SH1107G I2C Address
I2C_ADDR = 0x3C
CLK_SPEED = 100  # 100kHz I2C clock

# FTDI/FT4222 Vendor Commands
FTDI_VENDOR_CMD = 0x40
FT4222_I2C_MODE = 0x30
FT4222_I2C_MASTER_ENABLE = 0x40

# SH1107G Command Definitions
CMD_SET_COLUMN_ADDR = 0x15
CMD_SET_ROW_ADDR = 0x75
CMD_SET_DISPLAY_START_LINE = 0xA1
CMD_SET_CONTRAST = 0x81
CMD_SEG_REMAP_ON = 0xA0
CMD_DISPLAY_NORMAL = 0xA6
CMD_DISPLAY_INVERSE = 0xA7
CMD_DISPLAY_ON = 0xAF
CMD_DISPLAY_OFF = 0xAE
CMD_PAGE_MODE = 0x20
CMD_HORIZONTAL_MODE = 0x21
CMD_SET_MUX_RATIO = 0xA8
CMD_SET_OFFSET = 0xD3
CMD_SET_PAGE = 0xB0
CMD_COM_SCAN_NORMAL = 0xC0
CMD_COM_SCAN_REMAP = 0xC8
CMD_SET_CLOCK_DIV = 0xD5
CMD_SET_PRECHARGE = 0xD9
CMD_SET_COM_PINS = 0xDA
CMD_SET_VCOMH = 0xDB
CMD_SET_CHARGE_PUMP = 0x8D

# Display dimensions
WIDTH = 128
HEIGHT = 128
PAGES = HEIGHT // 8
BUFFER_SIZE = WIDTH * PAGES


class FT4222USB:
    """FT4222H USB to I2C Bridge using pyusb"""
    
    def __init__(self, vid=0x0403, pid=0x601C):
        self.vid = vid
        self.pid = pid
        self.dev = None
        self.ep_out = 0x02
        self.ep_in = 0x81
        self._connected = False
        
    def connect(self):
        """Connect to FT4222H device"""
        self.dev = usb.core.find(idVendor=self.vid, idProduct=self.pid)
        if self.dev is None:
            raise ConnectionError("FT4222H device not found")
        
        # Print device info
        print(f"Device: {usb.util.get_string(self.dev, self.dev.iProduct)}")
        print(f"Manufacturer: {usb.util.get_string(self.dev, self.dev.iManufacturer)}")
        
        # Set configuration
        try:
            self.dev.set_configuration()
        except Exception as e:
            print(f"Warning: set_configuration: {e}")
        
        # Initialize I2C mode
        self._init_i2c()
        
        self._connected = True
        return True
    
    def _init_i2c(self):
        """Initialize FT4222 in I2C master mode"""
        # Send vendor command to set I2C mode
        # BM_REQUEST_TYPE: 0x40 (Host to Device, Vendor, Device)
        # B_REQUEST: 0x30 (FT4222_I2C_MODE)
        # W_VALUE: 0x0000 (I2C mode)
        # W_INDEX: 0x0000
        try:
            self.dev.ctrl_transfer(
                0x40,  # bmRequestType
                0x30,  # bRequest (FT4222_I2C_MODE)
                0x0000, # wValue
                0x0000, # wIndex
                None    # no data
            )
            print("I2C mode set")
        except Exception as e:
            print(f"Warning: I2C mode set: {e}")
        
        # Enable I2C master
        try:
            self.dev.ctrl_transfer(
                0x40,  # bmRequestType
                0x31,  # bRequest (FT4222_I2C_MASTER_ENABLE)
                0x0000, # wValue
                0x0000, # wIndex
                None    # no data
            )
            print("I2C master enabled")
        except Exception as e:
            print(f"Warning: I2C master enable: {e}")
        
        # Set clock speed (divider)
        # wValue = divider (0x0014 = 400kHz, 0x0064 = 100kHz, 0x00C8 = 50kHz)
        try:
            self.dev.ctrl_transfer(
                0x40,  # bmRequestType
                0x0D,  # bRequest (Set Clock)
                0x0064, # wValue (100kHz)
                0x0000, # wIndex
                None    # no data
            )
            print("Clock speed set to 100kHz")
        except Exception as e:
            print(f"Warning: clock speed: {e}")
    
    def i2c_write(self, addr, data, retry=3):
        """Write data to I2C device"""
        # I2C write command format: 0x10
        # Packet: [CMD(0x10), LEN, I2C_ADDR, DATA...]
        cmd_byte = 0x10
        addr_byte = (addr << 1) & 0xFE  # 7-bit addr, write bit = 0
        
        for attempt in range(retry):
            try:
                # Include length byte like SHT31 test
                packet = bytes([cmd_byte, len(data) + 1, addr_byte]) + data
                
                self.dev.write(self.ep_out, packet, timeout=1000)
                time.sleep(0.002)
                
                # Read status
                try:
                    status = self.dev.read(self.ep_in, 2, timeout=1000)
                    if len(status) >= 1 and status[0] != 0:
                        print(f"  Write status: {list(status)}")
                    return status
                except usb.core.USBTimeoutError:
                    if attempt < retry - 1:
                        time.sleep(0.01)
                        continue
                    raise IOError("I2C write timeout")
                    
            except Exception as e:
                if attempt < retry - 1:
                    time.sleep(0.01)
                    continue
                raise
    
    def i2c_read(self, addr, length, retry=3):
        for attempt in range(retry):
            try:
                # I2C read command format: 0x20 (START | READ | STOP)
                cmd = 0x20
                addr_byte = ((addr << 1) | 0x01) & 0xFF  # 7-bit addr, read bit = 1
                packet = bytes([cmd, addr_byte, length])
                
                self.dev.write(self.ep_out, packet, timeout=1000)
                
                # Read response
                data = self.dev.read(self.ep_in, length + 2, timeout=1000)
                
                # Check status (first 2 bytes)
                if len(data) >= 2:
                    if data[1] & 0x04:  # NACK flag
                        if attempt < retry - 1:
                            time.sleep(0.01)
                            continue
                        raise IOError(f"I2C NACK at address 0x{addr:02X}")
                
                return data[2:]  # Skip status bytes
                
            except Exception as e:
                if attempt < retry - 1:
                    time.sleep(0.01)
                    continue
                raise
    
    def close(self):
        """Close the USB connection"""
        if self.dev:
            try:
                usb.util.release_interface(self.dev, 0)
            except:
                pass
            self.dev = None
        self._connected = False


class SH1107G:
    """SH1107G OLED Display Driver"""
    
    def __init__(self, i2c_addr=I2C_ADDR):
        self.i2c_addr = i2c_addr
        self.ft4222 = None
        self.initialized = False
        self.buffer = [0] * BUFFER_SIZE
        
    def connect(self):
        """Connect to FT4222 and initialize I2C"""
        try:
            self.ft4222 = FT4222USB()
            self.ft4222.connect()
            print("Connected to FT4222")
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")
    
    def disconnect(self):
        """Close connection to FT4222"""
        if self.ft4222:
            self.ft4222.close()
            self.ft4222 = None
            self.initialized = False
    
    def _write_command(self, cmd):
        """Write command byte to display"""
        if not self.ft4222:
            raise ConnectionError("Not connected")
        
        # Control byte 0x00 = Command
        data = bytes([0x00, cmd])
        try:
            self.ft4222.i2c_write(self.i2c_addr, data)
        except Exception as e:
            print(f"Warning: command write error: {e}")
            raise
        time.sleep(0.001)
    
    def _write_data(self, data):
        """Write data bytes to display"""
        if not self.ft4222:
            raise ConnectionError("Not connected")
        
        # Control byte 0x40 = Data
        packet = bytes([0x40]) + bytes(data)
        try:
            self.ft4222.i2c_write(self.i2c_addr, packet)
        except Exception as e:
            print(f"Warning: data write error: {e}")
            raise
    
    def initialize(self):
        """Initialize SH1107G display"""
        if not self.ft4222:
            raise ConnectionError("Not connected to FT4222")
        
        print("Initializing SH1107G display...")
        
        time.sleep(0.1)
        
        # Initialization sequence
        self._write_command(CMD_DISPLAY_OFF)
        time.sleep(0.05)
        
        self._write_command(CMD_SET_CLOCK_DIV)
        self._write_command(0x80)
        
        self._write_command(CMD_SET_MUX_RATIO)
        self._write_command(0x7F)
        
        self._write_command(CMD_SET_OFFSET)
        self._write_command(0x00)
        
        self._write_command(CMD_SET_DISPLAY_START_LINE)
        self._write_command(0x00)
        
        self._write_command(CMD_SET_CHARGE_PUMP)
        self._write_command(0x14)
        
        self._write_command(CMD_SEG_REMAP_ON)
        self._write_command(0x01)
        
        self._write_command(CMD_COM_SCAN_REMAP)
        self._write_command(0x08)
        
        self._write_command(CMD_SET_COM_PINS)
        self._write_command(0x12)
        
        self._write_command(CMD_SET_CONTRAST)
        self._write_command(0xFF)
        
        self._write_command(CMD_SET_PRECHARGE)
        self._write_command(0x25)
        
        self._write_command(CMD_SET_VCOMH)
        self._write_command(0x20)
        
        self._write_command(CMD_DISPLAY_NORMAL)
        self._write_command(CMD_DISPLAY_ON)
        
        time.sleep(0.1)
        
        self.initialized = True
        print("SH1107G initialized successfully!")
        
    def clear(self):
        """Clear the display buffer"""
        self.buffer = [0] * BUFFER_SIZE
    
    def set_pixel(self, x, y, value=1):
        """Set a pixel in the buffer"""
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return
        
        page = y // 8
        bit = y % 8
        
        idx = page * WIDTH + x
        if value:
            self.buffer[idx] |= (1 << bit)
        else:
            self.buffer[idx] &= ~(1 << bit)
    
    def draw_rect(self, x1, y1, x2, y2, fill=False):
        """Draw a rectangle"""
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                if fill or x == x1 or x == x2 or y == y1 or y == y2:
                    self.set_pixel(x, y, 1)
    
    def show(self):
        """Send buffer to display"""
        if not self.initialized:
            raise RuntimeError("Display not initialized")
        
        for page in range(PAGES):
            self._write_command(CMD_SET_PAGE | (page & 0x0F))
            self._write_command(CMD_SET_COLUMN_ADDR)
            self._write_command(0x00)
            self._write_command(WIDTH - 1)
            
            start_idx = page * WIDTH
            end_idx = start_idx + WIDTH
            page_data = self.buffer[start_idx:end_idx]
            
            self._write_data(bytes(page_data))
    
    def display_on(self):
        """Turn display on"""
        self._write_command(CMD_DISPLAY_ON)
    
    def display_off(self):
        """Turn display off"""
        self._write_command(CMD_DISPLAY_OFF)
    
    def set_contrast(self, level):
        """Set display contrast"""
        self._write_command(CMD_SET_CONTRAST)
        self._write_command(level & 0xFF)


def i2c_scan():
    """Scan I2C bus for devices"""
    print("Scanning I2C bus...")
    found = []
    
    ft = FT4222USB()
    try:
        ft.connect()
    except Exception as e:
        print(f"Failed to connect for scan: {e}")
        return found
    
    for addr in range(0x08, 0x78):
        try:
            # Try to read one byte - device should ACK if present
            result = ft.i2c_read(addr, 1, retry=1)
            print(f"Found device at 0x{addr:02X}")
            found.append(hex(addr))
        except Exception as e:
            pass
    
    ft.close()
    
    if found:
        print(f"Found devices: {found}")
    else:
        print("No devices found!")
    
    return found


def demo_pattern(oled):
    """Display demo patterns"""
    print("Running display demo...")
    
    oled.clear()
    oled.show()
    time.sleep(0.5)
    
    print("Pattern 1: Fill screen")
    oled.buffer = [0xFF] * BUFFER_SIZE
    oled.show()
    time.sleep(1)
    
    print("Pattern 2: Clear screen")
    oled.clear()
    oled.show()
    time.sleep(0.5)
    
    print("Pattern 3: Checkerboard")
    oled.clear()
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if (x // 8 + y // 8) % 2 == 0:
                oled.set_pixel(x, y, 1)
    oled.show()
    time.sleep(1)
    
    print("Pattern 4: Horizontal lines")
    oled.clear()
    for y in range(0, HEIGHT, 8):
        for x in range(WIDTH):
            oled.set_pixel(x, y, 1)
    oled.show()
    time.sleep(1)
    
    print("Pattern 5: Vertical lines")
    oled.clear()
    for x in range(0, WIDTH, 8):
        for y in range(HEIGHT):
            oled.set_pixel(x, y, 1)
    oled.show()
    time.sleep(1)
    
    print("Pattern 6: Frame")
    oled.clear()
    oled.draw_rect(0, 0, WIDTH - 1, HEIGHT - 1)
    oled.draw_rect(4, 4, WIDTH - 5, HEIGHT - 5)
    oled.show()
    time.sleep(2)
    
    print("Demo complete!")


def main():
    global I2C_ADDR
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            addr = sys.argv[1]
            if addr.startswith('0x'):
                I2C_ADDR = int(addr, 16)
            else:
                I2C_ADDR = int(addr)
            print(f"Using I2C address: 0x{I2C_ADDR:02X}")
        except ValueError:
            print(f"Invalid address: {sys.argv[1]}")
    
    print("=" * 50)
    print("SH1107G OLED Display Test")
    print("=" * 50)
    
    # Scan I2C bus first
    print("\n0. Scanning I2C bus...")
    try:
        i2c_scan()
    except Exception as e:
        print(f"I2C scan failed: {e}")
    
    # Create display instance
    oled = SH1107G(i2c_addr=I2C_ADDR)
    
    try:
        print("\n1. Connecting to FT4222...")
        oled.connect()
        
        print("\n2. Initializing SH1107G...")
        oled.initialize()
        
        print("\n3. Running demo...")
        demo_pattern(oled)
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        oled.disconnect()
        print("\nDisconnected.")


if __name__ == "__main__":
    main()
