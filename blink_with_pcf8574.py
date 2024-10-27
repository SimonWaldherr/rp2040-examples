from machine import Pin, I2C
import utime

# Parameterize I2C settings
i2c_bus = 0
scl_pin = 17
sda_pin = 16
freq = 100000
address = 0x20
toggle_delay = 1  # delay in seconds

# Initialize I2C
i2c = I2C(i2c_bus, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)

def toggle_pins(address, delay=1):
    try:
        for i in range(8):
            pin_state = 1 << i
            i2c.writeto(address, bytearray([pin_state]))
            utime.sleep(delay)
            
            # Verify the written state
            read_back = i2c.readfrom(address, 1)
            print("Written State:", bin(pin_state), "Read State:", bin(read_back[0]))
            
            # Reset pins after each toggle
            i2c.writeto(address, bytearray([0x00]))
    except OSError as e:
        print("Error accessing I2C device:", e)

# Run toggle function in a controlled manner
try:
    while True:
        toggle_pins(address, toggle_delay)
except KeyboardInterrupt:
    print("Program stopped by user")
