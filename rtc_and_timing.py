import time
import machine

class DS3231:
    """Real-time clock DS3231 driver"""
    
    def __init__(self, i2c, address=0x68):
        self.i2c = i2c
        self.address = address
    
    def _bcd_to_dec(self, bcd):
        """Convert BCD to decimal"""
        return ((bcd >> 4) * 10) + (bcd & 0x0F)
    
    def _dec_to_bcd(self, dec):
        """Convert decimal to BCD"""
        return ((dec // 10) << 4) + (dec % 10)
    
    def get_time(self):
        """Get current time from RTC"""
        data = self.i2c.readfrom_mem(self.address, 0x00, 7)
        
        seconds = self._bcd_to_dec(data[0] & 0x7F)
        minutes = self._bcd_to_dec(data[1] & 0x7F)
        hours = self._bcd_to_dec(data[2] & 0x3F)
        day = self._bcd_to_dec(data[3] & 0x07)
        date = self._bcd_to_dec(data[4] & 0x3F)
        month = self._bcd_to_dec(data[5] & 0x1F)
        year = self._bcd_to_dec(data[6]) + 2000
        
        return (year, month, date, day, hours, minutes, seconds)
    
    def set_time(self, year, month, date, day, hours, minutes, seconds):
        """Set RTC time"""
        data = bytearray(7)
        data[0] = self._dec_to_bcd(seconds)
        data[1] = self._dec_to_bcd(minutes)
        data[2] = self._dec_to_bcd(hours)
        data[3] = self._dec_to_bcd(day)
        data[4] = self._dec_to_bcd(date)
        data[5] = self._dec_to_bcd(month)
        data[6] = self._dec_to_bcd(year - 2000)
        
        self.i2c.writeto_mem(self.address, 0x00, data)
    
    def get_temperature(self):
        """Get temperature from DS3231 internal sensor"""
        data = self.i2c.readfrom_mem(self.address, 0x11, 2)
        temp = data[0] + (data[1] >> 6) * 0.25
        return temp

def rtc_example():
    """Real-time clock example"""
    print("DS3231 Real-Time Clock Example")
    print("=" * 30)
    
    # Initialize I2C
    i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17), freq=100000)
    
    # Check for DS3231
    devices = i2c.scan()
    if 0x68 not in devices:
        print("DS3231 not found on I2C bus")
        return
    
    rtc = DS3231(i2c)
    
    # Set initial time (uncomment and modify as needed)
    # rtc.set_time(2024, 8, 1, 4, 12, 30, 0)  # Year, Month, Date, Day, Hour, Min, Sec
    
    print("Reading time from DS3231...")
    
    try:
        while True:
            # Get current time
            year, month, date, day, hours, minutes, seconds = rtc.get_time()
            
            # Get temperature
            temp = rtc.get_temperature()
            
            # Format and display
            weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            day_name = weekdays[day - 1] if 1 <= day <= 7 else "???"
            
            time_str = f"{year:04d}-{month:02d}-{date:02d} {day_name} {hours:02d}:{minutes:02d}:{seconds:02d}"
            print(f"Time: {time_str}, Temp: {temp:.2f}°C")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nRTC example stopped")

def timer_example():
    """Timer and timing example"""
    print("Timer and Timing Example")
    print("=" * 25)
    
    # LED for visual feedback
    led = machine.Pin(25, machine.Pin.OUT)
    
    # Timer callback function
    def timer_callback(timer):
        led.toggle()
        print(f"Timer fired at {time.ticks_ms()}ms")
    
    # Create and start timer
    timer = machine.Timer()
    timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=timer_callback)
    
    print("Timer started - LED should blink every second")
    print("Demonstrating various timing functions...")
    
    start_time = time.ticks_ms()
    
    try:
        for i in range(10):
            print(f"Loop {i+1}/10")
            
            # Precise timing with ticks
            loop_start = time.ticks_ms()
            
            # Do some work
            time.sleep_ms(500)
            
            loop_end = time.ticks_ms()
            elapsed = time.ticks_diff(loop_end, loop_start)
            print(f"  Loop took {elapsed}ms")
            
        total_time = time.ticks_diff(time.ticks_ms(), start_time)
        print(f"Total execution time: {total_time}ms")
        
    except KeyboardInterrupt:
        print("\nTimer example stopped")
    finally:
        timer.deinit()
        led.value(0)

def watchdog_example():
    """Watchdog timer example"""
    print("Watchdog Timer Example")
    print("=" * 22)
    
    # Initialize watchdog with 8 second timeout
    wdt = machine.WDT(timeout=8000)
    
    print("Watchdog enabled with 8 second timeout")
    print("Feeding watchdog every 5 seconds...")
    print("Press Ctrl+C to stop feeding (will cause reset)")
    
    count = 0
    try:
        while True:
            # Feed the watchdog
            wdt.feed()
            count += 1
            print(f"Fed watchdog #{count} at {time.ticks_ms()}ms")
            
            # Wait 5 seconds
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopped feeding watchdog - system will reset in ~8 seconds")
        # Let the watchdog reset the system
        while True:
            time.sleep(1)

def sleep_example():
    """Deep sleep and power management example"""
    print("Sleep and Power Management Example")
    print("=" * 35)
    
    # Button for wake-up
    wake_pin = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
    
    # LED for status
    led = machine.Pin(25, machine.Pin.OUT)
    
    print("Press button on GPIO 14 to wake from sleep")
    
    for i in range(3):
        print(f"Active for 3 seconds... ({3-i})")
        led.value(1)
        time.sleep(1)
        led.value(0)
        time.sleep(1)
    
    print("Going to sleep...")
    print("Press GPIO 14 button to wake up")
    
    # Configure wake-up source
    machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
    
    # Go to sleep (this will stop execution until wake-up)
    # Note: This is a simplified example - actual deep sleep 
    # implementation may vary depending on the specific board
    try:
        machine.lightsleep()  # Light sleep - can be woken by GPIO
    except:
        # If lightsleep is not available, simulate with regular sleep
        print("Light sleep not available, using regular sleep")
        time.sleep(10)
    
    print("Woke up from sleep!")

def main():
    """Main function"""
    print("Real-Time Clock and Timing Examples")
    print("=" * 35)
    
    # Uncomment the example you want to run:
    rtc_example()
    # timer_example()
    # watchdog_example()  # Be careful - this will reset the system!
    # sleep_example()

if __name__ == "__main__":
    main()
