from machine import Pin, SPI
import time

class SSD1306_SPI:
    """Simple SSD1306 OLED display driver for SPI interface"""
    
    def __init__(self, width, height, spi, dc, res, cs):
        self.width = width
        self.height = height
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.init_display()
        
    def write_cmd(self, cmd):
        """Write command to display"""
        self.cs.value(1)
        self.dc.value(0)  # Command mode
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)
        
    def write_data(self, buf):
        """Write data to display"""
        self.cs.value(1)
        self.dc.value(1)  # Data mode
        self.cs.value(0)
        self.spi.write(buf)
        self.cs.value(1)
        
    def init_display(self):
        """Initialize the OLED display"""
        self.res.value(0)
        time.sleep_ms(10)
        self.res.value(1)
        time.sleep_ms(10)
        
        # Initialization sequence
        init_cmds = [
            0xAE,  # Display off
            0xD5, 0x80,  # Set display clock divide ratio
            0xA8, 0x3F,  # Set multiplex ratio (63)
            0xD3, 0x00,  # Set display offset
            0x40,  # Set start line address
            0x8D, 0x14,  # Charge pump setting
            0x20, 0x00,  # Memory addressing mode
            0xA1,  # Set segment re-map
            0xC8,  # Set COM output scan direction
            0xDA, 0x12,  # Set COM pins hardware configuration
            0x81, 0xCF,  # Set contrast control
            0xD9, 0xF1,  # Set pre-charge period
            0xDB, 0x40,  # Set VCOMH deselect level
            0xA4,  # Entire display on
            0xA6,  # Set normal display
            0xAF   # Display on
        ]
        
        for cmd in init_cmds:
            self.write_cmd(cmd)
            
    def show(self):
        """Update the display with buffer contents"""
        self.write_cmd(0x21)  # Set column address
        self.write_cmd(0x00)  # Start column
        self.write_cmd(0x7F)  # End column
        
        self.write_cmd(0x22)  # Set page address  
        self.write_cmd(0x00)  # Start page
        self.write_cmd(0x07)  # End page
        
        self.write_data(self.buffer)
        
    def fill(self, color):
        """Fill entire display with color (0=black, 1=white)"""
        fill_value = 0xFF if color else 0x00
        for i in range(len(self.buffer)):
            self.buffer[i] = fill_value
            
    def pixel(self, x, y, color):
        """Set individual pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            page = y // 8
            bit = y % 8
            index = page * self.width + x
            if color:
                self.buffer[index] |= 1 << bit
            else:
                self.buffer[index] &= ~(1 << bit)
                
    def text(self, text, x, y):
        """Simple text rendering (5x8 font)"""
        font = {
            'A': [0x7E, 0x11, 0x11, 0x11, 0x7E],
            'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
            'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
            'D': [0x7F, 0x41, 0x41, 0x22, 0x1C],
            'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
            '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],
            '1': [0x00, 0x42, 0x7F, 0x40, 0x00],
            '2': [0x42, 0x61, 0x51, 0x49, 0x46],
            '3': [0x21, 0x41, 0x45, 0x4B, 0x31],
            '4': [0x18, 0x14, 0x12, 0x7F, 0x10],
            '5': [0x27, 0x45, 0x45, 0x45, 0x39],
            '.': [0x00, 0x60, 0x60, 0x00, 0x00],
            'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
            'e': [0x38, 0x54, 0x54, 0x54, 0x18],
            'l': [0x00, 0x41, 0x7F, 0x40, 0x00],
            'o': [0x38, 0x44, 0x44, 0x44, 0x38],
        }
        
        offset_x = 0
        for char in text.upper():
            if char in font:
                char_data = font[char]
                for col, data in enumerate(char_data):
                    for row in range(8):
                        if data & (1 << row):
                            self.pixel(x + offset_x + col, y + row, 1)
                offset_x += 6

def main():
    """Main example function"""
    print("SSD1306 OLED Display Example")
    print("=" * 30)
    
    # Initialize SPI and control pins
    spi = SPI(0, baudrate=8000000, polarity=0, phase=0, 
              sck=Pin(18), mosi=Pin(19), miso=Pin(16))
    dc = Pin(20, Pin.OUT)
    res = Pin(21, Pin.OUT)
    cs = Pin(17, Pin.OUT)
    
    # Initialize display
    display = SSD1306_SPI(128, 64, spi, dc, res, cs)
    
    counter = 0
    while True:
        # Clear display
        display.fill(0)
        
        # Draw some content
        display.text("Hello RP2040", 10, 10)
        display.text(f"Count: {counter}", 10, 25)
        
        # Draw some pixels
        for i in range(10):
            display.pixel(10 + i, 40 + i, 1)
            
        # Update display
        display.show()
        
        counter += 1
        time.sleep(1)

if __name__ == "__main__":
    main()
