import array, time
from machine import Pin
import rp2

brightness = 0.3

# Definition of the PIO program for the WS2812 LEDs
@rp2.asm_pio(
    sideset_init=rp2.PIO.OUT_LOW,  # Initial state of the side-set pins.
    out_shiftdir=rp2.PIO.SHIFT_LEFT,  # Direction in which data is shifted out of the shift register.
    autopull=True,  # Automatic reloading of the shift register from the FIFO (First In, First Out memory).
    pull_thresh=24  # Threshold in bits at which data is automatically reloaded from the FIFO.
)
def ws2812():
    # Timing constants for bit transmission
    T1, T2, T3 = 2, 5, 3
    wrap_target()
    label("bitloop")
    # Transmit one bit, starting with the MSB; set the line to low and delay T3-1 cycles
    out(x, 1).side(0)[T3 - 1]
    # Jump to "do_zero" if the bit is 0, and set the line to high for T1-1 cycles
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    # Set the line back to high and repeat the loop for the next bit
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    # Set the line to low and delay for T2-1 cycles to send the signal for a 0
    nop().side(0)[T2 - 1]
    wrap()


def hsb_to_rgb(h, s, b):
    # Converts an HSB color value to an RGB color value.

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
    # Scale the color values based on the desired brightness
    dimmer_array = array.array("I", (int(((c >> 16) & 0xFF) * brightness_input) << 16 |
                                     int(((c >> 8) & 0xFF) * brightness_input) << 8 |
                                     int((c & 0xFF) * brightness_input) for c in pixel_array))
    # Transmit the scaled color values to the LEDs
    state_mach.put(dimmer_array, 8)
    time.sleep_ms(10)

def set_led(ii, color):
    # Set the color value of a single LED
    pixel_array[ii] = (color[1] << 16) + (color[0] << 8) + color[2]


if __name__ == "__main__":
    # Number of LEDs in the ring
    led_count = 12
    # GPIO pin number to which the data line of the LEDs is connected
    PIN_NUM = 0
    
    # Create and activate the StateMachine object for the PIO program
    state_mach = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))
    state_mach.active(1)
    # Array for the color values of the LEDs
    pixel_array = array.array("I", [0] * led_count)
    
    # Create a running light effect where the following four LEDs leave a trail
    background = (15, 15, 15)  # Background
    cycles = 20000
    trail_length = 4  # Length of the trail
    
    
    for ii in range(int(cycles * led_count) + 1):
        # Main LED
        set_led(ii % led_count, hsb_to_rgb(ii * 9, 1, 0.8))  # Sets each LED to a different color
        # Trailing LEDs
        for j in range(trail_length):
            if (ii - j - 1) >= 0:
                # Decrease brightness for each following LED
                set_led((ii - j - 1) % led_count, hsb_to_rgb(ii * 9, 1, 0.8 * (0.8 ** (j + 1))))
        if ii > trail_length:
            # Set the older LED that no longer trails to the background
            set_led((ii - trail_length - 1) % led_count, background)
        update_pix()
        time.sleep(0.05)
