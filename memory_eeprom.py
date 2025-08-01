from machine import Pin, SoftI2C
import time
import struct

class EEPROM_24LC256:
    """24LC256 EEPROM driver (32KB)"""
    
    def __init__(self, i2c, address=0x50):
        self.i2c = i2c
        self.address = address
        self.page_size = 64  # 64 bytes per page
        self.max_address = 32767  # 32KB - 1
        
    def write_byte(self, addr, data):
        """Write a single byte to EEPROM"""
        if addr > self.max_address:
            raise ValueError("Address out of range")
        
        addr_bytes = struct.pack('>H', addr)  # Big endian 16-bit address
        self.i2c.writeto(self.address, addr_bytes + bytes([data]))
        time.sleep_ms(5)  # Write cycle time
        
    def read_byte(self, addr):
        """Read a single byte from EEPROM"""
        if addr > self.max_address:
            raise ValueError("Address out of range")
            
        addr_bytes = struct.pack('>H', addr)
        self.i2c.writeto(self.address, addr_bytes)
        return self.i2c.readfrom(self.address, 1)[0]
        
    def write_bytes(self, addr, data):
        """Write multiple bytes to EEPROM"""
        for i, byte in enumerate(data):
            self.write_byte(addr + i, byte)
            
    def read_bytes(self, addr, length):
        """Read multiple bytes from EEPROM"""
        if addr + length > self.max_address:
            raise ValueError("Read would exceed EEPROM size")
            
        addr_bytes = struct.pack('>H', addr)
        self.i2c.writeto(self.address, addr_bytes)
        return self.i2c.readfrom(self.address, length)
        
    def write_string(self, addr, text):
        """Write a string to EEPROM"""
        text_bytes = text.encode('utf-8')
        # Write length first, then string
        self.write_byte(addr, len(text_bytes))
        self.write_bytes(addr + 1, text_bytes)
        
    def read_string(self, addr):
        """Read a string from EEPROM"""
        length = self.read_byte(addr)
        if length == 0:
            return ""
        text_bytes = self.read_bytes(addr + 1, length)
        return text_bytes.decode('utf-8')

def eeprom_test():
    """Test EEPROM functionality"""
    print("EEPROM 24LC256 Test")
    print("=" * 20)
    
    # Initialize I2C
    i2c = SoftI2C(scl=Pin(17), sda=Pin(16), freq=100000)
    
    # Check for EEPROM
    devices = i2c.scan()
    if 0x50 not in devices:
        print("EEPROM not found at address 0x50")
        return
        
    eeprom = EEPROM_24LC256(i2c)
    
    print("EEPROM found, running tests...")
    
    # Test 1: Write and read single bytes
    print("\nTest 1: Single byte operations")
    test_addr = 0x100
    test_value = 0xAA
    
    print(f"Writing 0x{test_value:02X} to address 0x{test_addr:04X}")
    eeprom.write_byte(test_addr, test_value)
    
    read_value = eeprom.read_byte(test_addr)
    print(f"Read back: 0x{read_value:02X}")
    
    if read_value == test_value:
        print("✓ Single byte test passed")
    else:
        print("✗ Single byte test failed")
    
    # Test 2: Write and read multiple bytes
    print("\nTest 2: Multiple byte operations")
    test_data = b"Hello, EEPROM!"
    test_addr = 0x200
    
    print(f"Writing: {test_data}")
    eeprom.write_bytes(test_addr, test_data)
    
    read_data = eeprom.read_bytes(test_addr, len(test_data))
    print(f"Read back: {read_data}")
    
    if read_data == test_data:
        print("✓ Multiple byte test passed")
    else:
        print("✗ Multiple byte test failed")
    
    # Test 3: String operations
    print("\nTest 3: String operations")
    test_string = "RP2040 EEPROM Example"
    test_addr = 0x300
    
    print(f"Writing string: '{test_string}'")
    eeprom.write_string(test_addr, test_string)
    
    read_string = eeprom.read_string(test_addr)
    print(f"Read back: '{read_string}'")
    
    if read_string == test_string:
        print("✓ String test passed")
    else:
        print("✗ String test failed")
    
    print("\nAll tests completed!")

def simple_datalogger():
    """Simple data logger using EEPROM"""
    print("Simple EEPROM Data Logger")
    print("=" * 25)
    
    # Initialize I2C and EEPROM
    i2c = SoftI2C(scl=Pin(17), sda=Pin(16), freq=100000)
    
    if 0x50 not in i2c.scan():
        print("EEPROM not found!")
        return
        
    eeprom = EEPROM_24LC256(i2c)
    
    # Data logging parameters
    log_start_addr = 0x1000
    entry_size = 8  # 4 bytes timestamp + 4 bytes value
    max_entries = 100
    
    print("Data logger ready")
    print("Press Ctrl+C to stop and read back data")
    
    entry_count = 0
    
    try:
        while entry_count < max_entries:
            # Simulate sensor reading
            sensor_value = int(time.ticks_ms() % 1000)
            timestamp = time.ticks_ms()
            
            # Pack data: timestamp (4 bytes) + value (4 bytes)
            data = struct.pack('<II', timestamp, sensor_value)
            
            # Write to EEPROM
            addr = log_start_addr + (entry_count * entry_size)
            eeprom.write_bytes(addr, data)
            
            print(f"Entry {entry_count}: Time={timestamp}, Value={sensor_value}")
            
            entry_count += 1
            time.sleep(2)
            
    except KeyboardInterrupt:
        print(f"\nLogging stopped. Recorded {entry_count} entries")
        
    # Read back and display data
    print("\nReading back logged data:")
    for i in range(entry_count):
        addr = log_start_addr + (i * entry_size)
        data = eeprom.read_bytes(addr, entry_size)
        timestamp, value = struct.unpack('<II', data)
        print(f"Entry {i}: Time={timestamp}, Value={value}")

def main():
    """Main function"""
    print("EEPROM Examples")
    print("=" * 15)
    
    # Run EEPROM test
    eeprom_test()
    
    time.sleep(2)
    
    # Uncomment to run data logger:
    # simple_datalogger()

if __name__ == "__main__":
    main()
