from machine import Pin, I2C, SPI
import time

def scan_i2c_devices():
    """Scan for I2C devices on the bus"""
    print("I2C Device Scanner")
    print("=" * 20)
    
    # Initialize I2C with common pin configurations
    i2c_configs = [
        (0, 16, 17),  # I2C0, SDA=16, SCL=17
        (0, 4, 5),    # I2C0, SDA=4, SCL=5
        (1, 2, 3),    # I2C1, SDA=2, SCL=3
        (1, 6, 7),    # I2C1, SDA=6, SCL=7
    ]
    
    for bus_id, sda_pin, scl_pin in i2c_configs:
        try:
            print(f"\nScanning I2C{bus_id} (SDA={sda_pin}, SCL={scl_pin})...")
            i2c = I2C(bus_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=100000)
            
            devices = i2c.scan()
            if devices:
                print(f"Found {len(devices)} device(s):")
                for device in devices:
                    print(f"  Address: 0x{device:02X} ({device})")
            else:
                print("No devices found")
        except Exception as e:
            print(f"Error on I2C{bus_id}: {e}")

def i2c_communication_example():
    """Example of I2C communication with a generic device"""
    print("I2C Communication Example")
    print("=" * 25)
    
    # Initialize I2C
    i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)
    
    # Example device address (change as needed)
    device_address = 0x48  # Common for temperature sensors
    
    print(f"Attempting communication with device at 0x{device_address:02X}")
    
    try:
        # Try to read from device
        data = i2c.readfrom(device_address, 2)
        print(f"Read data: {[hex(b) for b in data]}")
        
        # Try to write to device
        i2c.writeto(device_address, b'\x00')  # Write register address 0
        print("Write successful")
        
        # Read from specific register
        register_data = i2c.readfrom_mem(device_address, 0x00, 2)
        print(f"Register 0x00 data: {[hex(b) for b in register_data]}")
        
    except OSError as e:
        print(f"Communication error: {e}")
        print("Make sure device is connected and address is correct")

def spi_communication_example():
    """Example of SPI communication"""
    print("SPI Communication Example")
    print("=" * 25)
    
    # Initialize SPI
    spi_configs = [
        (0, 18, 19, 16),  # SPI0, SCK=18, MOSI=19, MISO=16
        (1, 10, 11, 12),  # SPI1, SCK=10, MOSI=11, MISO=12
    ]
    
    for spi_id, sck_pin, mosi_pin, miso_pin in spi_configs:
        try:
            print(f"\nTesting SPI{spi_id} (SCK={sck_pin}, MOSI={mosi_pin}, MISO={miso_pin})")
            
            spi = SPI(spi_id, 
                     baudrate=1000000,  # 1 MHz
                     polarity=0,        # Clock idle state
                     phase=0,           # Clock edge for data sampling
                     sck=Pin(sck_pin),
                     mosi=Pin(mosi_pin),
                     miso=Pin(miso_pin))
            
            # CS (Chip Select) pin
            cs = Pin(17, Pin.OUT)
            cs.value(1)  # Deselect device
            
            # Example SPI transaction
            test_data = b'\x01\x02\x03\x04'
            
            print("Sending test data:", [hex(b) for b in test_data])
            
            # Select device
            cs.value(0)
            
            # Send and receive data
            received = spi.read(len(test_data))
            spi.write(test_data)
            
            # Deselect device
            cs.value(1)
            
            print("Received data:", [hex(b) for b in received])
            
        except Exception as e:
            print(f"SPI{spi_id} error: {e}")

def digital_io_example():
    """Digital I/O example with multiple pins"""
    print("Digital I/O Example")
    print("=" * 20)
    
    # Output pins (LEDs)
    output_pins = [Pin(i, Pin.OUT) for i in range(10, 14)]
    
    # Input pins (buttons/switches)
    input_pins = [Pin(i, Pin.IN, Pin.PULL_UP) for i in range(14, 18)]
    
    print("Output pins: GPIO 10-13 (connect LEDs)")
    print("Input pins: GPIO 14-17 (connect buttons)")
    print("Press Ctrl+C to stop")
    
    counter = 0
    
    try:
        while True:
            # Binary counter on output pins
            for i, pin in enumerate(output_pins):
                pin.value((counter >> i) & 1)
            
            # Read input pins
            input_states = [not pin.value() for pin in input_pins]  # Inverted due to pull-up
            
            if any(input_states):
                print(f"Inputs: {input_states}, Counter: {counter:04b}")
            
            counter = (counter + 1) % 16
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nDigital I/O example stopped")
        # Turn off all outputs
        for pin in output_pins:
            pin.value(0)

def pwm_example():
    """PWM example with multiple channels"""
    print("PWM Example")
    print("=" * 12)
    
    # Initialize PWM on multiple pins
    pwm_pins = [Pin(i) for i in range(20, 24)]
    pwm_channels = [PWM(pin) for pin in pwm_pins]
    
    # Set frequency
    freq = 1000  # 1 kHz
    for pwm in pwm_channels:
        pwm.freq(freq)
    
    print(f"PWM on GPIO 20-23 at {freq} Hz")
    print("Duty cycle will sweep from 0% to 100%")
    
    try:
        while True:
            for duty_percent in range(0, 101, 5):
                duty_value = int((duty_percent / 100) * 65535)
                
                # Different phase for each channel
                for i, pwm in enumerate(pwm_channels):
                    phase_offset = (duty_percent + i * 25) % 100
                    phase_duty = int((phase_offset / 100) * 65535)
                    pwm.duty_u16(phase_duty)
                
                print(f"Duty cycle: {duty_percent}%")
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nPWM example stopped")
        # Turn off all PWM
        for pwm in pwm_channels:
            pwm.duty_u16(0)

def main():
    """Main function to run all examples"""
    print("RP2040 Communication and I/O Examples")
    print("=" * 40)
    
    # Run all examples
    scan_i2c_devices()
    time.sleep(2)
    
    i2c_communication_example()
    time.sleep(2)
    
    spi_communication_example()
    time.sleep(2)
    
    # Uncomment to run interactive examples:
    # digital_io_example()
    # pwm_example()

if __name__ == "__main__":
    main()
