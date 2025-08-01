from machine import Pin, SoftSPI
import time

class MAX7219:
    """Simple MAX7219 8x8 LED matrix driver"""
    
    def __init__(self, spi, cs_pin):
        self.spi = spi
        self.cs = Pin(cs_pin, Pin.OUT)
        self.cs.value(1)
        self.init_display()
        
    def write_register(self, register, data):
        """Write to MAX7219 register"""
        self.cs.value(0)
        self.spi.write(bytearray([register, data]))
        self.cs.value(1)
        
    def init_display(self):
        """Initialize the MAX7219"""
        self.write_register(0x09, 0x00)  # Decode mode: no decode
        self.write_register(0x0A, 0x03)  # Intensity: medium
        self.write_register(0x0B, 0x07)  # Scan limit: all digits
        self.write_register(0x0C, 0x01)  # Shutdown: normal operation
        self.write_register(0x0F, 0x00)  # Display test: off
        self.clear()
        
    def clear(self):
        """Clear the display"""
        for row in range(1, 9):
            self.write_register(row, 0x00)
            
    def set_row(self, row, data):
        """Set a row (1-8) with 8-bit data"""
        if 1 <= row <= 8:
            self.write_register(row, data)
            
    def draw_pattern(self, pattern):
        """Draw an 8x8 pattern (list of 8 bytes)"""
        for i, row_data in enumerate(pattern):
            self.set_row(i + 1, row_data)

def main():
    """Main LED matrix example"""
    print("MAX7219 8x8 LED Matrix Example")
    print("=" * 30)
    
    # Initialize SPI
    spi = SoftSPI(baudrate=1000000, polarity=0, phase=0,
                  sck=Pin(18), mosi=Pin(19), miso=Pin(16))
    
    # Initialize MAX7219
    matrix = MAX7219(spi, cs_pin=17)
    
    # Define some patterns
    patterns = {
        'smile': [
            0b00111100,
            0b01000010,
            0b10100101,
            0b10000001,
            0b10100101,
            0b10011001,
            0b01000010,
            0b00111100
        ],
        'heart': [
            0b00000000,
            0b01100110,
            0b11111111,
            0b11111111,
            0b01111110,
            0b00111100,
            0b00011000,
            0b00000000
        ],
        'arrow': [
            0b00001000,
            0b00011100,
            0b00111110,
            0b01111111,
            0b00001000,
            0b00001000,
            0b00001000,
            0b00001000
        ],
        'cross': [
            0b00011000,
            0b00011000,
            0b00011000,
            0b11111111,
            0b11111111,
            0b00011000,
            0b00011000,
            0b00011000
        ]
    }
    
    print("Displaying patterns...")
    
    try:
        while True:
            for name, pattern in patterns.items():
                print(f"Showing: {name}")
                matrix.draw_pattern(pattern)
                time.sleep(2)
                
            # Scrolling text effect
            print("Scrolling effect...")
            for shift in range(16):
                shifted_pattern = []
                for row in patterns['smile']:
                    if shift < 8:
                        shifted_pattern.append(row >> shift)
                    else:
                        shifted_pattern.append(row << (shift - 8))
                matrix.draw_pattern(shifted_pattern)
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        matrix.clear()
        print("\nLED matrix example stopped")

if __name__ == "__main__":
    main()
