from machine import Pin, I2C
import time

class BME280:
    """Simple BME280 temperature, humidity, and pressure sensor driver"""
    
    def __init__(self, i2c, address=0x76):
        self.i2c = i2c
        self.address = address
        self._load_calibration()
        
    def _load_calibration(self):
        """Load calibration data from sensor"""
        # Read temperature calibration
        cal = self.i2c.readfrom_mem(self.address, 0x88, 24)
        self.dig_T1 = cal[1] << 8 | cal[0]
        self.dig_T2 = cal[3] << 8 | cal[2]
        if self.dig_T2 > 32767:
            self.dig_T2 -= 65536
        self.dig_T3 = cal[5] << 8 | cal[4]
        if self.dig_T3 > 32767:
            self.dig_T3 -= 65536
            
        # Read humidity calibration  
        cal_h = self.i2c.readfrom_mem(self.address, 0xA1, 1)
        cal_h += self.i2c.readfrom_mem(self.address, 0xE1, 7)
        self.dig_H1 = cal_h[0]
        self.dig_H2 = cal_h[2] << 8 | cal_h[1]
        if self.dig_H2 > 32767:
            self.dig_H2 -= 65536
        self.dig_H3 = cal_h[3]
        
    def read_compensated_data(self):
        """Read and return compensated temperature, humidity, pressure"""
        # Set sensor to forced mode
        self.i2c.writeto_mem(self.address, 0xF2, b'\x01')  # humidity oversampling
        self.i2c.writeto_mem(self.address, 0xF4, b'\x25')  # temp and pressure oversampling, forced mode
        
        # Wait for measurement
        time.sleep_ms(50)
        
        # Read raw data
        data = self.i2c.readfrom_mem(self.address, 0xF7, 8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]
        
        # Temperature compensation
        var1 = (temp_raw / 16384.0 - self.dig_T1 / 1024.0) * self.dig_T2
        var2 = ((temp_raw / 131072.0 - self.dig_T1 / 8192.0) * 
                (temp_raw / 131072.0 - self.dig_T1 / 8192.0)) * self.dig_T3
        t_fine = var1 + var2
        temperature = t_fine / 5120.0
        
        # Humidity compensation (simplified)
        humidity = (hum_raw - (self.dig_H1 * 64.0 - self.dig_H3 / 2.0 * temperature)) * \
                   (self.dig_H2 / 65536.0 * (1.0 + self.dig_H3 / 67108864.0 * temperature))
        humidity = max(0.0, min(100.0, humidity))
        
        # Pressure compensation (simplified, returns raw value)
        pressure = pres_raw / 256.0  # Simplified pressure reading
        
        return temperature, humidity, pressure

def main():
    """Main example function"""
    print("BME280 Environmental Sensor Example")
    print("=" * 40)
    
    # Initialize I2C
    i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=100000)
    
    # Scan for devices
    devices = i2c.scan()
    print(f"I2C devices found: {[hex(d) for d in devices]}")
    
    if 0x76 not in devices and 0x77 not in devices:
        print("BME280 sensor not found!")
        return
    
    # Initialize BME280
    address = 0x76 if 0x76 in devices else 0x77
    bme = BME280(i2c, address)
    print(f"BME280 initialized at address {hex(address)}")
    
    while True:
        try:
            temp, hum, pres = bme.read_compensated_data()
            print(f"Temperature: {temp:.2f}°C")
            print(f"Humidity: {hum:.1f}%")
            print(f"Pressure: {pres:.2f} Pa")
            print("-" * 30)
        except Exception as e:
            print(f"Error reading sensor: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
