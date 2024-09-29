import machine
import time

class Nunchuck:
    INIT_COMMANDS = [b'\xf0\x55', b'\xfb\x00']

    def __init__(self, i2c, poll=True, poll_interval=50):
        self.i2c = i2c
        self.address = 0x52
        self.buffer = bytearray(6)
        self.last_poll = time.ticks_ms()
        self.polling_threshold = poll_interval if poll else -1

        self._initialize_nunchuck()

    def _initialize_nunchuck(self):
        for command in self.INIT_COMMANDS:
            self.i2c.writeto(self.address, command)

    def _update(self):
        self.i2c.writeto(self.address, b'\x00')
        self.i2c.readfrom_into(self.address, self.buffer)

    def _poll(self):
        if self.polling_threshold > 0 and time.ticks_diff(time.ticks_ms(), self.last_poll) > self.polling_threshold:
            self._update()
            self.last_poll = time.ticks_ms()

    def buttons(self):
        self._poll()
        return (
            not (self.buffer[5] & 0x02),  # C button
            not (self.buffer[5] & 0x01)   # Z button
        )

    def joystick(self):
        self._poll()
        return self.buffer[0], self.buffer[1]


def main():
    # Initialize the I2C bus
    i2c_devices = [
        machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16), freq=100000),
        machine.I2C(1, scl=machine.Pin(19), sda=machine.Pin(18), freq=100000)
    ]

    nunchuks = [Nunchuck(i2c, poll=True, poll_interval=100) for i2c in i2c_devices]

    # Infinite loop for continuously querying and displaying data
    while True:
        for idx, nunchuk in enumerate(nunchuks, 1):
            print(f"Nunchuk {idx}:")
            print("Joystick:", nunchuk.joystick())
            print("Buttons:", nunchuk.buttons())
            print("-" * 40)
        print("=" * 40)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
