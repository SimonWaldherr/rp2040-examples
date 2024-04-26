import ustruct
import time
import math
from machine import I2C, Pin

class PCA9685:
    """
    Eine Klasse zur Steuerung des PCA9685 PWM/Servo-Treibers, die die Kontrolle
    über bis zu 16 Servos über die I2C-Schnittstelle ermöglicht.
    """
    def __init__(self, i2c, address=0x40):
        """
        Initialisiert eine neue Instanz der PCA9685-Klasse.

        Args:
            i2c (I2C): Das I2C-Objekt für die Kommunikation.
            address (int): Die I2C-Adresse des PCA9685-Moduls.
        """
        self.i2c = i2c
        self.address = address
        self.reset()

    def _write(self, reg, value):
        """ Schreibt einen Byte-Wert in ein spezifisches PCA9685-Register. """
        self.i2c.writeto_mem(self.address, reg, bytearray([value]))

    def _read(self, reg):
        """ Liest einen Byte-Wert aus einem spezifischen PCA9685-Register. """
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def reset(self):
        """ Setzt das PCA9685-Gerät zurück. """
        self._write(0x00, 0x00)  # Befehl zum Zurücksetzen in das Mode1-Register

    def set_pwm_frequency(self, freq):
        """ Stellt die PWM-Frequenz für den PCA9685 ein. """
        prescale_val = int(25000000.0 / 4096.0 / freq - 1 + 0.5)
        old_mode = self._read(0x00)
        self._write(0x00, old_mode | 0x10)  # Schlafmodus
        self._write(0xFE, prescale_val)
        self._write(0x00, old_mode)
        time.sleep_us(5)
        self._write(0x00, old_mode | 0xa1)  # Neustart

    def set_pwm(self, channel, on, off):
        """ Setzt den Start (on) und das Ende (off) des Impulses für einen einzelnen PWM-Kanal. """
        data = ustruct.pack('<HH', on, off)
        self.i2c.writeto_mem(self.address, 0x06 + 4 * channel, data)

    def read_pwm(self, channel):
        """ Liest die PWM-Werte aus dem PCA9685. """
        data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * channel, 4)
        return ustruct.unpack('<HH', data)

    def set_duty_cycle(self, channel, duty_cycle, invert=False):
        """ Stellt den Tastgrad für einen PWM-Kanal ein. """
        if not 0 <= duty_cycle <= 4095:
            raise ValueError("Tastgrad außerhalb des zulässigen Bereichs.")
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
        Initialisiert eine neue Instanz der Servo-Klasse.

        Args:
            i2c (I2C): Das I2C-Objekt für die Kommunikation.
            address (int): Die I2C-Adresse des PCA9685-Moduls.
            freq (int): Die Frequenz in Hz für die PWM-Steuerung.
            min_us (int): Die minimale Impulsdauer in Mikrosekunden.
            max_us (int): Die maximale Impulsdauer in Mikrosekunden.
            degrees (int): Der Bewegungsumfang der Servos in Grad.
        """
        self.pca9685 = PCA9685(i2c, address)
        self.pca9685.set_pwm_frequency(freq)
        self.period = 1000000 / freq
        self.min_duty = self._us_to_duty_cycle(min_us)
        self.max_duty = self._us_to_duty_cycle(max_us)
        self.degrees = degrees

    def _us_to_duty_cycle(self, us):
        """ Konvertiert Mikrosekunden in den Tastgrad basierend auf der aktuellen Frequenz. """
        return int(4095 * us / self.period)

    def set_position(self, channel, degrees=None, radians=None, us=None):
        """ Stellt die Position des Servo ein. """
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
        """ Entlässt einen Servo, indem seine Bewegung gestoppt wird. """
        self.pca9685.set_duty_cycle(channel, 0)

# Einrichtung von I2C und PCA9685
sda = Pin(0)
scl = Pin(1)
i2c = I2C(id=0, sda=sda, scl=scl)
servo_controller = Servo(i2c=i2c)

# Beispielanwendung: Verschiedene Positionen für die Servos setzen
for channel in range(16):
    # Stelle den Servo auf 0 Grad
    servo_controller.set_position(channel, degrees=0)
    time.sleep(0.5)
    # Stelle den Servo auf 90 Grad
    servo_controller.set_position(channel, degrees=90)
    time.sleep(0.5)
    # Stelle den Servo auf 180 Grad
    servo_controller.set_position(channel, degrees=180)
    time.sleep(0.5)
    # Servo freigeben
    servo_controller.release(channel)
    time.sleep(0.1)

