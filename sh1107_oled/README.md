# SH1107G OLED Display Driver

Python drivers for 1.12" 128x128 OLED display with SH1107G driver IC.

## Two Implementation Options

### 1. Luma.OLED Library (for Raspberry Pi)
Uses the Luma.OLED library with Raspberry Pi's built-in I2C interface.

### 2. FT4222 USB-I2C Adapter (for other systems)
Uses pyusb with FT4222 USB-I2C bridge (original implementation).


## Option 1: Luma.OLED Library (Raspberry Pi)

### Hardware
- **Display**: 1.12" OLED, 128x128 pixels
- **Driver IC**: SH1107G
- **Interface**: I2C
- **Default I2C Address**: 0x3C (may also be 0x3D)

### Connection (Raspberry Pi 4)
| OLED Display | Raspberry Pi |
|--------------|--------------|
| VCC | 3.3V (Pin 1) or 5V (Pin 2) |
| GND | GND (Pin 6) |
| SCL | GPIO 3 (Pin 5) |
| SDA | GPIO 2 (Pin 3) |

### Installation

#### For Debian Trixie/Raspberry Pi OS Bookworm:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-pil libjpeg-dev zlib1g-dev libfreetype-dev liblcms2-dev libopenjp2-7 libtiff-dev -y
pip3 install luma.oled psutil --break-system-packages
```

#### For older Debian versions (Bullseye or earlier):
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-pil libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5 -y
sudo pip3 install luma.oled psutil
```

### Usage
```python
from oled_luma import SH1107Luma
import time

# Create display instance
oled = SH1107Luma(i2c_addr=0x3C, i2c_port=1, rotate=0)

try:
    # Display some text
    lines = [
        "Raspi 4 Online",
        "Grove OLED",
        "SH1107G Driver",
        "Luma.OLED Lib"
    ]
    oled.display_multiline_text(lines, font_size=11)
    time.sleep(2)
    
    # Clear display
    oled.clear()
    
except Exception as e:
    print(f"Error: {e}")
```

### API

#### SH1107Luma(i2c_addr=0x3C, i2c_port=1, rotate=0)

Create a new display instance.

- `i2c_addr`: I2C address (default 0x3C)
- `i2c_port`: I2C port (default 1)
- `rotate`: Display rotation (0-3, default 0)

#### Methods

- `display_text(x, y, text, font_size=12, fill="white")` - Display text at position
- `display_multiline_text(lines, font_size=10, fill="white")` - Display multiple lines
- `draw_rectangle(x1, y1, x2, y2, fill=None, outline="white")` - Draw rectangle
- `draw_ellipse(x1, y1, x2, y2, fill=None, outline="white")` - Draw ellipse
- `clear()` - Clear the display
- `set_contrast(level)` - Set contrast (0-255)
- `invert_display(invert=True)` - Invert colors
- `display_on()` / `display_off()` - Turn display on/off

### Running Tests

```bash
python oled_luma.py          # Use default address 0x3C
python oled_luma.py 0x3D    # Use address 0x3D
```


## Option 2: FT4222 USB-I2C Adapter (Original Implementation)

### Hardware
Same display specifications.

### Connection
| OLED Display | FT4222 |
|--------------|--------|
| VCC | 3.3V |
| GND | GND |
| SCL | SCK (Port A) |
| SDA | MOSI (Port A) |

### Installation
```bash
pip install ft4222
```

### Usage
```python
from sh1107 import SH1107G, I2C_ADDR
import time

# Create display instance
oled = SH1107G(i2c_addr=I2C_ADDR)

try:
    # Connect and initialize
    oled.connect()
    oled.initialize()
    
    # Draw some graphics
    oled.clear()
    oled.set_pixel(10, 10, 1)
    oled.draw_rect(20, 20, 50, 50)
    oled.show()
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    oled.disconnect()
```

### Running Tests

```bash
python sh1107.py
```

Python driver for 1.12" 128x128 OLED display with SH1107G driver IC via FT4222 USB-I2C adapter.

## Hardware

- **Display**: 1.12" OLED, 128x128 pixels
- **Driver IC**: SH1107G
- **Interface**: I2C
- **Default I2C Address**: 0x3C (may also be 0x3D)

## Connection

| OLED Display | FT4222 |
|--------------|--------|
| VCC | 3.3V |
| GND | GND |
| SCL | SCK (Port A) |
| SDA | MOSI (Port A) |

## Installation

```bash
pip install ft4222
```

## Usage

```python
from sh1107 import SH1107G, I2C_ADDR
import time

# Create display instance
oled = SH1107G(i2c_addr=I2C_ADDR)

try:
    # Connect and initialize
    oled.connect()
    oled.initialize()
    
    # Draw some graphics
    oled.clear()
    oled.set_pixel(10, 10, 1)
    oled.draw_rect(20, 20, 50, 50)
    oled.show()
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    oled.disconnect()
```

## API

### SH1107G(i2c_addr=I2C_ADDR, clk_speed=400)

Create a new display instance.

- `i2c_addr`: I2C address (default 0x3C)
- `clk_speed`: I2C clock speed in kHz (default 400)

### Methods

- `connect()` - Connect to FT4222 and initialize I2C
- `disconnect()` - Close FT4222 connection
- `initialize()` - Initialize SH1107G display
- `clear()` - Clear display buffer
- `show()` - Send buffer to display
- `set_pixel(x, y, value)` - Set pixel (1=on, 0=off)
- `draw_rect(x1, y1, x2, y2, fill=False)` - Draw rectangle
- `display_on()` / `display_off()` - Turn display on/off
- `invert_display(invert=True)` - Invert colors
- `set_contrast(level)` - Set contrast (0-255)

## Running Tests

```bash
python sh1107.py
```

This will run a demo showing various patterns on the display.

