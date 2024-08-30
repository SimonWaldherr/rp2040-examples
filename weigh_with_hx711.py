import _thread
import time
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from micropython import const

class HX711:
    # Constants for HX711 operation
    READ_BITS = const(24)  # Number of bits to read from HX711
    MIN_VALUE = const(-0x800000)  # Minimum value for 24-bit signed integer
    MAX_VALUE = const(0x7fffff)  # Maximum value for 24-bit signed integer
    POWER_DOWN_TIMEOUT = const(60)  # Timeout for power down in microseconds
    SETTLING_TIMES = [const(400), const(50)]  # Settling times in milliseconds for different rates
    SAMPLES_RATES = [const(10), const(80)]  # Sampling rates in Hz

    # Enumeration for sample rates
    class Rate:
        RATE_10 = const(0)
        RATE_80 = const(1)

    # Enumeration for gain settings
    class Gain:
        GAIN_128 = const(25)
        GAIN_32 = const(26)
        GAIN_64 = const(27)

    # Enumeration for power states
    class Power:
        POWER_UP = const(0)
        POWER_DOWN = const(1)

    # Enumeration for modes
    class Mode:
        MODE_A = const(0)
        MODE_B = const(1)

    def __init__(self, clk_pin: Pin, dat_pin: Pin, sm_index: int = 0):
        # Initialize the HX711 object
        self._lock = _thread.allocate_lock()  # Create a lock for thread safety
        self._lock.acquire()  # Acquire the lock to ensure safe initialization
        
        self.clock_pin = clk_pin  # Pin for the clock signal
        self.data_pin = dat_pin  # Pin for the data signal
        self.sm_index = sm_index  # Index for the state machine
        
        # Initialize the GPIO pins
        self.clock_pin.init(mode=Pin.OUT)
        self.data_pin.init(mode=Pin.IN)

        # Initialize the state machine for PIO operations
        self._sm = StateMachine(
            sm_index,
            self.pio_program,
            freq=10_000_000,  # Frequency of the state machine
            in_base=dat_pin,
            out_base=clk_pin,
            set_base=clk_pin,
            jmp_pin=None,
            sideset_base=clk_pin
        )

        self._lock.release()  # Release the lock after initialization

    @asm_pio(
        out_init=(PIO.OUT_LOW,),  # Initialize output to low
        set_init=(PIO.OUT_LOW,),  # Initialize set to low
        sideset_init=(PIO.OUT_LOW,),  # Initialize sideset to low
        out_shiftdir=PIO.SHIFT_LEFT,  # Shift direction for output
        autopush=True,  # Automatically push data to the FIFO
        autopull=False,  # Do not automatically pull data from the FIFO
        push_thresh=READ_BITS,  # Threshold for pushing data to FIFO
        fifo_join=PIO.JOIN_NONE  # FIFO join mode
    )
    def pio_program():
        # Assembly program to control HX711 timing and data retrieval
        set(x, 0)  # Initialize x register to 0
        label("start")
        set(y, 23)  # Set y register to 23
        wait(0, pin, 0)  # Wait for pin to be low
        label("read_bit")
        set(pins, 1)  # Set pins to high
        in_(pins, 1)  # Read input from pins
        jmp(y_dec, "read_bit").side(0).delay(1)  # Loop until y register is decremented
        pull(noblock).side(1)  # Pull data from FIFO
        out(x, 2)  # Output data to x register
        jmp(not_x, "start").side(0)  # Loop to "start" if x register is not zero
        mov(y, x)  # Move x register value to y register
        label("apply_gain")
        set(pins, 1).delay(1)  # Set pins to high and delay
        jmp(y_dec, "apply_gain").side(0).delay(1)  # Loop to "apply_gain" until y register is decremented
        wrap()  # Wrap the program

    def get_twos_complement(self, raw_value: int) -> int:
        # Convert raw ADC reading to a signed integer using two's complement
        return -(raw_value & self.MIN_VALUE) + (raw_value & self.MAX_VALUE)

    def read_weight(self) -> int:
        # Safely retrieve a single weight measurement from the load cell
        with self._lock:
            while self._sm.rx_fifo() == 0:
                pass  # Wait until data is available in the FIFO
            return self.get_twos_complement(self._sm.get())  # Read and convert the data

    def read_average(self, times: int) -> int:
        # Retrieve an average weight measurement from the load cell
        values = []
        for _ in range(times):
            values.append(self.read_weight())  # Collect measurements
        values.sort()  # Sort the values
        return sum(values[1:-1]) // (times - 2)  # Compute the average excluding the min and max values

    def power(self, state: int) -> None:
        # Control the power state of the HX711
        with self._lock:
            if state == self.Power.POWER_UP:
                self.clock_pin.low()  # Set clock pin low
                self._sm.restart()  # Restart the state machine
                self._sm.active(1)  # Activate the state machine
            elif state == self.Power.POWER_DOWN:
                self._sm.active(0)  # Deactivate the state machine
                self.clock_pin.high()  # Set clock pin high

    def wait_for_settling(self, rate: int) -> None:
        # Wait for the load cell to settle after a rate change or power up
        time.sleep_ms(self.SETTLING_TIMES[rate])

if __name__ == "__main__":
    from machine import Pin
    
    # Define the pins for clock and data
    CLOCK_PIN = Pin(14, Pin.OUT)
    DATA_PIN = Pin(15, Pin.IN)
    
    # Initialize the HX711 scale object
    scale = HX711(clk_pin=CLOCK_PIN, dat_pin=DATA_PIN)
    
    # Power up the scale and wait for settling
    scale.power(scale.Power.POWER_UP)
    scale.wait_for_settling(scale.Rate.RATE_80)
    
    try:
        while True:
            weight = scale.read_average(3)  # Read the average weight measurement
            print("Measured Weight:", weight)  # Print the measured weight
            time.sleep(0.1)  # Wait before the next measurement
    except KeyboardInterrupt:
        print("Measurement stopped.")  # Handle keyboard interrupt
        scale.power(scale.Power.POWER_DOWN)  # Power down the scale
