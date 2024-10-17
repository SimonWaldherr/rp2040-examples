from machine import Pin, SPI
from os import uname
import utime
import array, time
import rp2

brightness = 0.8

# Definition des PIO-Programms für die WS2812 LEDs
@rp2.asm_pio(
    sideset_init=rp2.PIO.OUT_LOW,  # Initialzustand der Side-Set-Pins.
    out_shiftdir=rp2.PIO.SHIFT_LEFT,  # Richtung, in der Daten aus dem Shift-Register geschoben werden.
    autopull=True,  # Automatisches Nachladen des Shift-Registers aus dem FIFO (First In, First Out-Speicher).
    pull_thresh=24  # Schwellenwert in Bits, bei dessen Erreichen automatisch Daten aus dem FIFO nachgeladen werden.
)
def ws2812():
    # Timing-Konstanten für die Bit-Übertragung
    T1, T2, T3 = 2, 5, 3
    wrap_target()
    label("bitloop")
    # Übertrage ein Bit, beginnend mit dem MSB; setze die Leitung auf Low und verzögere T3-1 Zyklen
    out(x, 1).side(0)[T3 - 1]
    # Springe zu "do_zero", wenn das Bit 0 ist, und setze die Leitung auf High für T1-1 Zyklen
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    # Setze die Leitung zurück auf High und wiederhole die Schleife für das nächste Bit
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    # Setze die Leitung auf Low und verzögere für T2-1 Zyklen, um das Signal für eine 0 zu senden
    nop().side(0)[T2 - 1]
    wrap()
    
    
def hsb_to_rgb(h, s, b):
    # Konvertiert einen HSB-Farbwert in einen RGB-Farbwert.
    
    if s == 0:
        return int(b * 255), int(b * 255), int(b * 255)
    
    h = h % 360
    
    h = h / 60
    i = int(h)
    f = h - i
    p = b * (1 - s)
    q = b * (1 - s * f)
    t = b * (1 - s * (1 - f))
    
    p, q, t = int(p * 255), int(q * 255), int(t * 255)
    b = int(b * 255)
    
    if i == 0:
        return b, t, p
    elif i == 1:
        return q, b, p
    elif i == 2:
        return p, b, t
    elif i == 3:
        return p, q, b
    elif i == 4:
        return t, p, b
    elif i == 5:
        return b, p, q
    
def update_pix(brightness_input=brightness):
    # Skaliere die Farbwerte basierend auf der gewünschten Helligkeit
    dimmer_array = array.array("I", (int(((c >> 16) & 0xFF) * brightness_input) << 16 |
                                     int(((c >> 8) & 0xFF) * brightness_input) << 8 |
                                     int((c & 0xFF) * brightness_input) for c in pixel_array))
    # Übertrage die skalierten Farbwerte an die LEDs
    state_mach.put(dimmer_array, 8)
    time.sleep_ms(10)
    
def set_led(ii, color):
    # Setze den Farbwert einer einzelnen LED
    pixel_array[ii] = (color[1] << 16) + (color[0] << 8) + color[2]

class RC522:

    DEBUG = False
    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26
    REQALL = 0x52
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61

    PICC_ANTICOLL1 = 0x93
    PICC_ANTICOLL2 = 0x95
    PICC_ANTICOLL3 = 0x97

    def __init__(self, sck, mosi, miso, rst, cs, baudrate=1000000, spi_id=0):
        self.sck = Pin(sck, Pin.OUT)
        self.mosi = Pin(mosi, Pin.OUT)
        self.miso = Pin(miso)
        self.rst = Pin(rst, Pin.OUT)
        self.cs = Pin(cs, Pin.OUT)
        
        self.rst.value(0)
        self.cs.value(1)
        
        board = uname()[0]
        if board == 'rp2':
            self.spi = SPI(spi_id, baudrate=baudrate, sck=self.sck, mosi=self.mosi, miso=self.miso)
        else:
            raise RuntimeError("Unsupported platform")
        
        self.rst.value(1)
        self.init()

    def _wreg(self, reg, val):
        self.cs.value(0)
        self.spi.write(b'%c' % int(0xff & ((reg << 1) & 0x7e)))
        self.spi.write(b'%c' % int(0xff & val))
        self.cs.value(1)

    def _rreg(self, reg):
        self.cs.value(0)
        self.spi.write(b'%c' % int(0xff & (((reg << 1) & 0x7e) | 0x80)))
        val = self.spi.read(1)
        self.cs.value(1)
        return val[0]

    def _sflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) | mask)

    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    def _tocard(self, cmd, send):
        recv = []
        bits = irq_en = wait_irq = n = 0
        stat = self.ERR
        if cmd == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10
        elif cmd == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(0x02, irq_en | 0x80)
        self._cflags(0x04, 0x80)
        self._sflags(0x0A, 0x80)
        self._wreg(0x01, 0x00)

        for c in send:
            self._wreg(0x09, c)
        self._wreg(0x01, cmd)

        if cmd == 0x0C:
            self._sflags(0x0D, 0x80)

        i = 2000
        while True:
            n = self._rreg(0x04)
            i -= 1
            if not ((i != 0) and not (n & 0x01) and not (n & wait_irq)):
                break

        self._cflags(0x0D, 0x80)

        if i:
            if (self._rreg(0x06) & 0x1B) == 0x00:
                stat = self.OK
                if n & irq_en & 0x01:
                    stat = self.NOTAGERR
                elif cmd == 0x0C:
                    n = self._rreg(0x0A)
                    lbits = self._rreg(0x0C) & 0x07
                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8
                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16
                    for _ in range(n):
                        recv.append(self._rreg(0x09))
            else:
                stat = self.ERR

        return stat, recv, bits

    def _crc(self, data):
        self._cflags(0x05, 0x04)
        self._sflags(0x0A, 0x80)
        for c in data:
            self._wreg(0x09, c)
        self._wreg(0x01, 0x03)

        i = 0xFF
        while True:
            n = self._rreg(0x05)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break
        return [self._rreg(0x22), self._rreg(0x21)]

    def init(self):
        self.reset()
        self._wreg(0x2A, 0x8D)
        self._wreg(0x2B, 0x3E)
        self._wreg(0x2D, 30)
        self._wreg(0x2C, 0)
        self._wreg(0x15, 0x40)
        self._wreg(0x11, 0x3D)
        self.antenna_on()

    def reset(self):
        self._wreg(0x01, 0x0F)

    def antenna_on(self, on=True):
        if on and not (self._rreg(0x14) & 0x03):
            self._sflags(0x14, 0x03)
        else:
            self._cflags(0x14, 0x03)

    def request(self, mode):
        self._wreg(0x0D, 0x07)
        stat, recv, bits = self._tocard(0x0C, [mode])
        if stat != self.OK or bits != 0x10:
            stat = self.ERR
        return stat, bits

    def anticoll(self, anticolN):
        ser_chk = 0
        ser = [anticolN, 0x20]
        self._wreg(0x0D, 0x00)
        stat, recv, bits = self._tocard(0x0C, ser)
        if stat == self.OK:
            if len(recv) == 5:
                for i in range(4):
                    ser_chk ^= recv[i]
                if ser_chk != recv[4]:
                    stat = self.ERR
            else:
                stat = self.ERR
        return stat, recv

    def SelectTagSN(self):
        valid_uid = []
        status, uid = self.anticoll(self.PICC_ANTICOLL1)
        if status != self.OK:
            return self.ERR, []
        if self.PcdSelect(uid, self.PICC_ANTICOLL1) == 0:
            return self.ERR, []
        if uid[0] == 0x88:
            valid_uid.extend(uid[1:4])
            status, uid = self.anticoll(self.PICC_ANTICOLL2)
            if status != self.OK:
                return self.ERR, []
            if self.PcdSelect(uid, self.PICC_ANTICOLL2) == 0:
                return self.ERR, []
            if uid[0] == 0x88:
                valid_uid.extend(uid[1:4])
                status, uid = self.anticoll(self.PICC_ANTICOLL3)
                if status != self.OK:
                    return self.ERR, []
                if self.PcdSelect(uid, self.PICC_ANTICOLL3) == 0:
                    return self.ERR, []
        valid_uid.extend(uid[0:5])
        return self.OK, valid_uid[:-1]
    
    def PcdSelect(self, serNum, anticolN):
        buf = [anticolN, 0x70] + serNum
        pOut = self._crc(buf)
        buf += pOut
        status, backData, backLen = self._tocard(0x0C, buf)
        return 1 if status == self.OK and backLen == 0x18 else 0


if __name__ == "__main__":
    reader = RC522(spi_id=0, sck=2, miso=4, mosi=3, cs=1, rst=0)
    last_card_id = None
    i = 0
    print("scanning ...\n")
    while True:
        reader.init()
        stat, tag_type = reader.request(reader.REQIDL)
        if stat == reader.OK:
            stat, uid = reader.SelectTagSN()
            if stat == reader.OK:
                card = int.from_bytes(bytes(uid), "little", False)
                if card != last_card_id:
                    print("CARD ID: " + str(card))
                    last_card_id = card
                    
                    # Anzahl der LEDs im Ring
                    led_count = 24
                    # GPIO-Pin-Nummer, an den die Datenleitung der LEDs angeschlossen ist
                    PIN_NUM = 28
                    
                    # Erstellen und Aktivieren des StateMachine-Objekts für das PIO-Programm
                    state_mach = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))
                    state_mach.active(1)
                    # Array für die Farbwerte der LEDs
                    pixel_array = array.array("I", [0] * led_count)
                    
                    # Erzeuge einen Lauflichteffekt, bei dem die nachfolgenden vier LEDs nachleuchten
                    background = (15, 15, 15)  # Hintergrund
                    cycles = 1
                    trail_length = 4  # Länge des Nachleuchtens
                    
                    for ii in range(int(cycles * led_count) + 1):
                        # Haupt-LED
                        set_led(ii % led_count, hsb_to_rgb(ii * 9, 1, 0.8))  # Setzt jede LED auf eine unterschiedliche Farbe
                        # Nachleuchtende LEDs
                        for j in range(trail_length):
                            if (ii - j - 1) >= 0:
                                # Verringere die Helligkeit für jede nachfolgende LED
                                set_led((ii - j - 1) % led_count, hsb_to_rgb(ii * 9, 1, 0.8 * (0.8 ** (j + 1))))
                        if ii > trail_length:
                            # Setze die ältere LED, die nicht mehr nachleuchtet, auf den Hintergrund
                            set_led((ii - trail_length - 1) % led_count, background)
                        update_pix()
                        
                    for ii in range(int(led_count)):
                        set_led(ii, (0,0,0))
                    update_pix()
                    
        utime.sleep_ms(100)
        i = i+1
        if i > 1000:
            last_card_id = None
            