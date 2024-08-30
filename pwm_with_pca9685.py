import ustruct
import time
import math
from machine import I2C, Pin

class PCA9685:
    """
    A class for controlling the PCA9685 PWM/Servo driver, which allows control
    of up to 16 servos via the I2C interface.
    """
    def __init__(self, i2c, address=0x40):
        """
        Initializes a new instance of the PCA9685 class.

        Args:
            i2c (I2C): The I2C object for communication.
            address (int): The I2C address of the PCA9685 module.
        """
        self.i2c = i2c
        self.address = address
        self.reset()

    def _write(self, reg, value):
        """ Writes a byte value to a specific PCA9685 register. """
        self.i2c.writeto_mem(self.address, reg, bytearray([value]))

    def _read(self, reg):
        """ Reads a byte value from a specific PCA9685 register. """
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def reset(self):
        """ Resets the PCA9685 device. """
        self._write(0x00, 0x00)  # Command to reset in the Mode1 register

    def set_pwm_frequency(self, freq):
        """ Sets the PWM frequency for the PCA9685. """
        prescale_val = int(25000000.0 / 4096.0 / freq - 1 + 0.5)
        old_mode = self._read(0x00)
        self._write(0x00, old_mode | 0x10)  # Sleep mode
        self._write(0xFE, prescale_val)
        self._write(0x00, old_mode)
        time.sleep_us(5)
        self._write(0x00, old_mode | 0xa1)  # Restart

    def set_pwm(self, channel, on, off):
        """ Sets the start (on) and end (off) of the pulse for a single PWM channel. """
        data = ustruct.pack('<HH', on, off)
        self.i2c.writeto_mem(self.address, 0x06 + 4 * channel, data)

    def read_pwm(self, channel):
        """ Reads the PWM values from the PCA9685. """
        data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * channel, 4)
        return ustruct.unpack('<HH', data)

    def set_duty_cycle(self, channel, duty_cycle, invert=False):
        """ Sets the duty cycle for a PWM channel. """
        if not 0 <= duty_cycle <= 4095:
            raise ValueError("Duty cycle out of range.")
        if invert:
            duty_cycle = 4095 - duty_cycle
        if duty_cycle == 0:
            self.set_pwm(channel, 0, 4096)
        elif duty_cycle == 4095:
            self.set_pwm(channel, 4096, 0)
        else:
            self.set_pwm(channel, 0, duty_cycle)

class Servo:
    def __init__(self, i2c, address=0x40, freq=50, min_us=600, max_us=2400, degrees=180):
        """
        Initializes a new instance of the Servo class.

        Args:
            i2c (I2C): The I2C object for communication.
            address (int): The I2C address of the PCA9685 module.
            freq (int): The frequency in Hz for PWM control.
            min_us (int): The minimum pulse width in microseconds.
            max_us (int): The maximum pulse width in microseconds.
            degrees (int): The range of motion for the servos in degrees.
        """
        self.pca9685 = PCA9685(i2c, address)
        self.pca9685.set_pwm_frequency(freq)
        self.period = 1000000 / freq
        self.min_duty = self._us_to_duty_cycle(min_us)
        self.max_duty = self._us_to_duty_cycle(max_us)
        self.degrees = degrees

    def _us_to_duty_cycle(self, us):
        """ Converts microseconds to duty cycle based on the current frequency. """
        return int(4095 * us / self.period)

    def set_position(self, channel, degrees=None, radians=None, us=None):
        """ Sets the position of the servo. """
        if degrees is not None:
            duty_cycle = self.min_duty + (self.max_duty - self.min_duty) * degrees / self.degrees
        elif radians is not None:
            duty_cycle = self.min_duty + (self.max_duty - self.min_duty) * radians / math.radians(self.degrees)
        elif us is not None:
            duty_cycle = self._us_to_duty_cycle(us)
        else:
            return self.pca9685.read_pwm(channel)

        duty_cycle = max(self.min_duty, min(self.max_duty, int(duty_cycle)))
        self.pca9685.set_duty_cycle(channel, duty_cycle)

    def release(self, channel):
        """ Releases a servo by stopping its motion. """
        self.pca9685.set_duty_cycle(channel, 0)

# Setup of I2C and PCA9685
sda = Pin(0)
scl = Pin(1)
i2c = I2C(id=0, sda=sda, scl=scl)
servo_controller = Servo(i2c=i2c)

# Example application: Setting different positions for the servos
for channel in range(16):
    # Set the servo to 0 degrees
    servo_controller.set_position(channel, degrees=0)
    time.sleep(0.5)
    # Set the servo to 90 degrees
    servo_controller.set_position(channel, degrees=90)
    time.sleep(0.5)
    # Set the servo to 180 degrees
    servo_controller.set_position(channel, degrees=180)
    time.sleep(0.5)
    # Release the servo
    servo_controller.release(channel)
    time.sleep(0.1)
