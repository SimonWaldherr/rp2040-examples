from machine import Pin
from time import sleep, sleep_us, ticks_us

def setup_pin(pin_number, mode):
    return Pin(pin_number, mode)

def measure_distance(trigger, echo):
    trigger.low()
    sleep_us(2)
    trigger.high()
    sleep_us(10)
    trigger.low()
    
    timeout = 25000
    start_time = ticks_us()
    
    while echo.value() == 0:
        if ticks_us() - start_time > timeout:
            return None
    
    signal_off = ticks_us()
    
    while echo.value() == 1:
        if ticks_us() - signal_off > timeout:
            return None

    signal_on = ticks_us()
    
    # Berechnung der Distanz
    time_elapsed = signal_on - signal_off
    distance = (time_elapsed * 0.03432) / 2
    return distance

trigger_pin = setup_pin(16, Pin.OUT)
echo_pin = setup_pin(17, Pin.IN)

while True:
    distance = measure_distance(trigger_pin, echo_pin)
    if distance is not None:
        print('Distance:', "{:.2f} cm".format(distance))
    else:
        print("Measurement timed out or failed.")
    sleep(1)  # Pause zwischen den Messungen

