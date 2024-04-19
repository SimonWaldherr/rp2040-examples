import _thread
import time
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from micropython import const

class HX711:
    READ_BITS = const(24)
    MIN_VALUE = const(-0x800000)
    MAX_VALUE = const(0x7fffff)
    POWER_DOWN_TIMEOUT = const(60)  # microseconds
    SETTLING_TIMES = [const(400), const(50)]  # milliseconds
    SAMPLES_RATES = [const(10), const(80)]


    class Rate:
        RATE_10 = const(0)
        RATE_80 = const(1)

    class Gain:
        GAIN_128 = const(25)
        GAIN_32 = const(26)
        GAIN_64 = const(27)

    class Power:
        POWER_UP = const(0)
        POWER_DOWN = const(1)

    class Mode:
        MODE_A = const(0)
        MODE_B = const(1)

    def __init__(self, clk_pin: Pin, dat_pin: Pin, sm_index: int = 0):
        self._lock = _thread.allocate_lock()
        self._lock.acquire()
        
        self.clock_pin = clk_pin
        self.data_pin = dat_pin
        self.sm_index = sm_index
        
        self.clock_pin.init(mode=Pin.OUT)
        self.data_pin.init(mode=Pin.IN)

        self._sm = StateMachine(
            sm_index,
            self.pio_program,
            freq=10_000_000,
            in_base=dat_pin,
            out_base=clk_pin,
            set_base=clk_pin,
            jmp_pin=None,
            sideset_base=clk_pin
        )

        self._lock.release()

    @asm_pio(
        out_init=(PIO.OUT_LOW,),
        set_init=(PIO.OUT_LOW,),
        sideset_init=(PIO.OUT_LOW,),
        out_shiftdir=PIO.SHIFT_LEFT,
        autopush=True,
        autopull=False,
        push_thresh=READ_BITS,
        fifo_join=PIO.JOIN_NONE
    )
    def pio_program():
        # Program to control HX711 timing and data retrieval.
        set(x, 0)
        label("start")
        set(y, 23)
        wait(0, pin, 0)
        label("read_bit")
        set(pins, 1)
        in_(pins, 1)
        jmp(y_dec, "read_bit").side(0).delay(1)
        pull(noblock).side(1)
        out(x, 2)
        jmp(not_x, "start").side(0)
        mov(y, x)
        label("apply_gain")
        set(pins, 1).delay(1)
        jmp(y_dec, "apply_gain").side(0).delay(1)
        wrap()

    def get_twos_complement(self, raw_value: int) -> int:
        # Convert raw ADC reading to a signed integer using two's complement.
        return -(raw_value & self.MIN_VALUE) + (raw_value & self.MAX_VALUE)

    def read_weight(self) -> int:
        # Safely retrieve a single weight measurement from the load cell.
        with self._lock:
            while self._sm.rx_fifo() == 0:
                pass
            return self.get_twos_complement(self._sm.get())
        
    def read_average(self, times: int) -> int:
        # Retrieve an average weight measurement from the load cell.
        values = []
        for _ in range(times):
            values.append(self.read_weight())
        values.sort()
        return sum(values[1:-1]) // (times - 2)

    def power(self, state: int) -> None:
        # Control the power state of the HX711.
        with self._lock:
            if state == self.Power.POWER_UP:
                self.clock_pin.low()
                self._sm.restart()
                self._sm.active(1)
            elif state == self.Power.POWER_DOWN:
                self._sm.active(0)
                self.clock_pin.high()

    def wait_for_settling(self, rate: int) -> None:
        # Wait for the load cell to settle after a rate change or power up.
        time.sleep_ms(self.SETTLING_TIMES[rate])

if __name__ == "__main__":
    from machine import Pin
    
    CLOCK_PIN = Pin(14, Pin.OUT)
    DATA_PIN = Pin(15, Pin.IN)
    
    scale = HX711(clk_pin=CLOCK_PIN, dat_pin=DATA_PIN)
    
    scale.power(scale.Power.POWER_UP)
    scale.wait_for_settling(scale.Rate.RATE_80)
    
    try:
        while True:
            weight = scale.read_average(3)
            print("Measured Weight:", weight)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Measurement stopped.")
        scale.power(scale.Power.POWER_DOWN)
