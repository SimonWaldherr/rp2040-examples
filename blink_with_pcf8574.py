from machine import Pin, I2C
import utime

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=100000)
address = 0x20

def toggle_pins():
    try:
        for i in range(8):
            pin_state = 1 << i
            i2c.writeto(address, bytearray([pin_state]))
            utime.sleep(1)
            
            # Nachprüfen, was tatsächlich geschrieben wurde
            read_back = i2c.readfrom(address, 1)
            print("Geschriebener Zustand:", bin(pin_state), "Gelesener Zustand:", bin(read_back[0]))
            
            i2c.writeto(address, bytearray([0x00]))
    except OSError as e:
        print("Fehler beim Zugriff auf das I2C-Gerät:", e)

while True:
    toggle_pins()
