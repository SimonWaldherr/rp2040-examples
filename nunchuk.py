import machine
import time

class Nunchuck:
    """
    Eine Klasse zur Handhabung eines Wii Nunchuk Controllers über I2C.
    Bietet Funktionen zum Abrufen von Joystick-, Beschleunigungs- und Tastenwerten.
    Ein Polling-Mechanismus ermöglicht regelmäßige Aktualisierungen der Sensorwerte.
    """

    def __init__(self, i2c, poll=True, poll_interval=50):
        """
        Initialisiert den Nunchuk-Controller.
        
        :param i2c: I2C-Objekt zur Kommunikation mit dem Controller.
        :param poll: Aktiviert oder deaktiviert Polling (Standard: True).
        :param poll_interval: Polling-Intervall in Millisekunden (Standard: 50ms).
        """
        self.i2c = i2c
        self.address = 0x52
        self.buffer = bytearray(6)  # Puffer zur Speicherung der Sensordaten

        # Initialisierungssequenz für den Nunchuk
        self.i2c.writeto(self.address, b'\xf0\x55')
        self.i2c.writeto(self.address, b'\xfb\x00')

        # Zeitstempel der letzten Polling-Aktualisierung
        self.last_poll = time.ticks_ms()
        
        # Polling-Intervall in Millisekunden
        self.polling_threshold = poll_interval if poll else -1

    def update(self):
        """
        Fordert einen Sensor-Readout vom Controller an und speichert die
        Daten im internen Puffer.
        """
        self.i2c.writeto(self.address, b'\x00')
        self.i2c.readfrom_into(self.address, self.buffer)

    def __poll(self):
        """
        Überprüft, ob ein Polling erforderlich ist, und führt ggf. eine
        Aktualisierung der Sensorwerte durch.
        """
        if self.polling_threshold > 0 and time.ticks_diff(time.ticks_ms(), self.last_poll) > self.polling_threshold:
            self.update()
            self.last_poll = time.ticks_ms()

    def accelerator(self):
        """
        Gibt die aktuellen Werte des Beschleunigungssensors zurück.
        
        :return: Ein Tuple mit den Werten für die Achsen X, Y und Z.
        """
        self.__poll()
        return (
            (self.buffer[2] << 2) + ((self.buffer[5] & 0x0C) >> 2),
            (self.buffer[3] << 2) + ((self.buffer[5] & 0x30) >> 4),
            (self.buffer[4] << 2) + ((self.buffer[5] & 0xC0) >> 6)
        )

    def buttons(self):
        """
        Gibt den aktuellen Zustand der Tasten C und Z zurück.
        
        :return: Ein Tuple mit booleschen Werten für die Tasten C und Z (True = gedrückt).
        """
        self.__poll()
        return (
            not (self.buffer[5] & 0x02),  # C-Taste
            not (self.buffer[5] & 0x01)   # Z-Taste
        )

    def joystick(self):
        """
        Gibt die aktuellen X- und Y-Werte des Joysticks zurück.
        
        :return: Ein Tuple mit den Werten für die X- und Y-Achse.
        """
        self.__poll()
        return (self.buffer[0], self.buffer[1])

    def joystick_left(self):
        """
        Gibt True zurück, wenn der Joystick nach links geneigt ist.
        """
        self.__poll()
        return self.buffer[0] < 55

    def joystick_right(self):
        """
        Gibt True zurück, wenn der Joystick nach rechts geneigt ist.
        """
        self.__poll()
        return self.buffer[0] > 200

    def joystick_up(self):
        """
        Gibt True zurück, wenn der Joystick nach oben geneigt ist.
        """
        self.__poll()
        return self.buffer[1] > 200

    def joystick_down(self):
        """
        Gibt True zurück, wenn der Joystick nach unten geneigt ist.
        """
        self.__poll()
        return self.buffer[1] < 55

    def joystick_center(self):
        """
        Gibt True zurück, wenn der Joystick in der Mitte steht.
        """
        self.__poll()
        return 100 < self.buffer[0] < 155 and 100 < self.buffer[1] < 155

    def joystick_x(self):
        """
        Gibt den normierten X-Wert des Joysticks zurück.
        
        :return: X-Wert, normiert auf einen Bereich von etwa -34 bis 222.
        """
        self.__poll()
        return (self.buffer[0] >> 2) - 34

    def joystick_y(self):
        """
        Gibt den normierten Y-Wert des Joysticks zurück.
        
        :return: Y-Wert, normiert auf einen Bereich von etwa -34 bis 222.
        """
        self.__poll()
        return (self.buffer[1] >> 2) - 34

    def is_shaking(self):
        """
        Prüft, ob der Nunchuk heftig geschüttelt wird, basierend auf den Beschleunigungswerten.
        
        :return: True, wenn die Beschleunigungswerte einen bestimmten Schwellenwert überschreiten.
        """
        x, y, z = self.accelerator()
        return max(x, y, z) > 800  # Schwellenwert für Erkennung

    def button_combination(self):
        """
        Prüft, ob beide Tasten gleichzeitig gedrückt sind.
        
        :return: True, wenn sowohl C als auch Z gedrückt sind.
        """
        c, z = self.buttons()
        return c and z


def main():
    # Initialisierung des I2C-Busses
    i2c = machine.I2C(0, scl=machine.Pin(21), sda=machine.Pin(20), freq=100000)
    
    # Erstellen des Nunchuck-Objekts
    nunchuk = Nunchuck(i2c, poll=True, poll_interval=100)

    # Endlosschleife zur kontinuierlichen Abfrage und Ausgabe der Daten
    while True:
        print("Joystick:", nunchuk.joystick())
        print("Accelerator:", nunchuk.accelerator())
        print("Buttons:", nunchuk.buttons())
        print("Shaking:", nunchuk.is_shaking())
        print("-" * 40)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
