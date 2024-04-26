import array, time
from machine import Pin
import rp2

brightness = 0.3

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


if __name__ == "__main__":
    # Anzahl der LEDs im Ring
    led_count = 12
    # GPIO-Pin-Nummer, an den die Datenleitung der LEDs angeschlossen ist
    PIN_NUM = 0
    
    # Erstellen und Aktivieren des StateMachine-Objekts für das PIO-Programm
    state_mach = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))
    state_mach.active(1)
    # Array für die Farbwerte der LEDs
    pixel_array = array.array("I", [0] * led_count)
    
    # Erzeuge einen Lauflichteffekt, bei dem die nachfolgenden vier LEDs nachleuchten
    background = (15, 15, 15)  # Hintergrund
    cycles = 20000
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
        time.sleep(0.05)
