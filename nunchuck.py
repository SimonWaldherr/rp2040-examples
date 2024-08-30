import machine
import time

class Nunchuck:
    """
    A class for handling a Wii Nunchuk controller via I2C.
    Provides functions to retrieve joystick, acceleration, and button values.
    A polling mechanism allows for regular updates of sensor values.
    """

    def __init__(self, i2c, poll=True, poll_interval=50):
        """
        Initializes the Nunchuk controller.
        
        :param i2c: I2C object for communication with the controller.
        :param poll: Enables or disables polling (default: True).
        :param poll_interval: Polling interval in milliseconds (default: 50ms).
        """
        self.i2c = i2c
        self.address = 0x52
        self.buffer = bytearray(6)  # Buffer for storing sensor data

        # Initialization sequence for the Nunchuk
        self.i2c.writeto(self.address, b'\xf0\x55')
        self.i2c.writeto(self.address, b'\xfb\x00')

        # Timestamp of the last polling update
        self.last_poll = time.ticks_ms()
        
        # Polling interval in milliseconds
        self.polling_threshold = poll_interval if poll else -1

    def update(self):
        """
        Requests a sensor readout from the controller and stores the
        data in the internal buffer.
        """
        self.i2c.writeto(self.address, b'\x00')
        self.i2c.readfrom_into(self.address, self.buffer)

    def __poll(self):
        """
        Checks if polling is necessary and performs a
        sensor value update if required.
        """
        if self.polling_threshold > 0 and time.ticks_diff(time.ticks_ms(), self.last_poll) > self.polling_threshold:
            self.update()
            self.last_poll = time.ticks_ms()

    def accelerator(self):
        """
        Returns the current values of the acceleration sensor.
        
        :return: A tuple with the values for the X, Y, and Z axes.
        """
        self.__poll()
        return (
            (self.buffer[2] << 2) + ((self.buffer[5] & 0x0C) >> 2),
            (self.buffer[3] << 2) + ((self.buffer[5] & 0x30) >> 4),
            (self.buffer[4] << 2) + ((self.buffer[5] & 0xC0) >> 6)
        )

    def buttons(self):
        """
        Returns the current state of the C and Z buttons.
        
        :return: A tuple with boolean values for the C and Z buttons (True = pressed).
        """
        self.__poll()
        return (
            not (self.buffer[5] & 0x02),  # C button
            not (self.buffer[5] & 0x01)   # Z button
        )

    def joystick(self):
        """
        Returns the current X and Y values of the joystick.
        
        :return: A tuple with the values for the X and Y axes.
        """
        self.__poll()
        return (self.buffer[0], self.buffer[1])

    def joystick_left(self):
        """
        Returns True if the joystick is tilted to the left.
        """
        self.__poll()
        return self.buffer[0] < 55

    def joystick_right(self):
        """
        Returns True if the joystick is tilted to the right.
        """
        self.__poll()
        return self.buffer[0] > 200

    def joystick_up(self):
        """
        Returns True if the joystick is tilted upwards.
        """
        self.__poll()
        return self.buffer[1] > 200

    def joystick_down(self):
        """
        Returns True if the joystick is tilted downwards.
        """
        self.__poll()
        return self.buffer[1] < 55

    def joystick_center(self):
        """
        Returns True if the joystick is in the center position.
        """
        self.__poll()
        return 100 < self.buffer[0] < 155 and 100 < self.buffer[1] < 155

    def joystick_x(self):
        """
        Returns the normalized X value of the joystick.
        
        :return: X value, normalized to a range of approximately -34 to 222.
        """
        self.__poll()
        return (self.buffer[0] >> 2) - 34

    def joystick_y(self):
        """
        Returns the normalized Y value of the joystick.
        
        :return: Y value, normalized to a range of approximately -34 to 222.
        """
        self.__poll()
        return (self.buffer[1] >> 2) - 34

    def is_shaking(self):
        """
        Checks if the Nunchuk is being shaken vigorously based on acceleration values.
        
        :return: True if the acceleration values exceed a certain threshold.
        """
        x, y, z = self.accelerator()
        return max(x, y, z) > 800  # Threshold for detection

    def button_combination(self):
        """
        Checks if both buttons are pressed simultaneously.
        
        :return: True if both C and Z buttons are pressed.
        """
        c, z = self.buttons()
        return c and z


def main():
    # Initialize the I2C bus
    i2c = machine.I2C(0, scl=machine.Pin(21), sda=machine.Pin(20), freq=100000)
    
    # Create the Nunchuck object
    nunchuk = Nunchuck(i2c, poll=True, poll_interval=100)

    # Infinite loop for continuously querying and displaying data
    while True:
        print("Joystick:", nunchuk.joystick())
        print("Accelerator:", nunchuk.accelerator())
        print("Buttons:", nunchuk.buttons())
        print("Shaking:", nunchuk.is_shaking())
        print("-" * 40)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
