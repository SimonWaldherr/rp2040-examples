from machine import Pin, Timer
import time

class Button:
    """Simple button handler with debouncing and interrupt support"""
    
    def __init__(self, pin_num, pull_up=True, debounce_ms=50):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP if pull_up else Pin.PULL_DOWN)
        self.debounce_ms = debounce_ms
        self.last_time = 0
        self.pressed = False
        self.callback = None
        self.pull_up = pull_up
        
        # Set up interrupt
        self.pin.irq(trigger=Pin.IRQ_FALLING if pull_up else Pin.IRQ_RISING, 
                     handler=self._irq_handler)
    
    def _irq_handler(self, pin):
        """Internal interrupt handler with debouncing"""
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_time) > self.debounce_ms:
            self.last_time = current_time
            expected_value = 0 if self.pull_up else 1
            if self.pin.value() == expected_value:
                self.pressed = True
                if self.callback:
                    self.callback()
    
    def set_callback(self, callback_func):
        """Set callback function for button press"""
        self.callback = callback_func
    
    def is_pressed(self):
        """Check if button was pressed (clears the flag)"""
        if self.pressed:
            self.pressed = False
            return True
        return False
    
    def wait_for_press(self, timeout_ms=None):
        """Wait for button press with optional timeout"""
        start_time = time.ticks_ms()
        while not self.is_pressed():
            if timeout_ms and time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
                return False
            time.sleep_ms(10)
        return True

def button1_callback():
    """Callback function for button 1"""
    print("Button 1 pressed!")

def button2_callback():
    """Callback function for button 2"""
    print("Button 2 pressed!")

def main():
    """Main example function"""
    print("Button and Interrupt Example")
    print("=" * 30)
    print("Press buttons connected to GPIO 14 and 15")
    print("Press Ctrl+C to exit")
    
    # Initialize LED for visual feedback
    led = Pin(25, Pin.OUT)
    led_state = False
    
    # Initialize buttons with interrupts
    button1 = Button(14, pull_up=True, debounce_ms=50)
    button2 = Button(15, pull_up=True, debounce_ms=50)
    
    # Set callback functions
    button1.set_callback(button1_callback)
    button2.set_callback(button2_callback)
    
    # Timer for LED blinking
    def toggle_led(timer):
        nonlocal led_state
        led_state = not led_state
        led.value(led_state)
    
    led_timer = Timer()
    led_timer.init(period=1000, mode=Timer.PERIODIC, callback=toggle_led)
    
    # Main loop
    button_count = 0
    try:
        while True:
            # Check for button presses using polling method
            if button1.is_pressed():
                button_count += 1
                print(f"Button 1 press count: {button_count}")
            
            if button2.is_pressed():
                button_count += 1
                print(f"Button 2 press count: {button_count}")
            
            # Small delay to prevent excessive CPU usage
            time.sleep_ms(50)
            
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
        led_timer.deinit()
        led.value(0)

if __name__ == "__main__":
    main()
