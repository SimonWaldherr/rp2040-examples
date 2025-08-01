from machine import Pin
import time
import dht

# Initialize DHT22 sensor on pin 2
sensor = dht.DHT22(Pin(2))

def read_temperature_humidity():
    """Read temperature and humidity from DHT22 sensor"""
    try:
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        return temperature, humidity
    except OSError as e:
        print("Failed to read from DHT22 sensor:", e)
        return None, None

def main():
    print("DHT22 Temperature and Humidity Sensor Example")
    print("=" * 45)
    
    while True:
        temp, hum = read_temperature_humidity()
        
        if temp is not None and hum is not None:
            print(f"Temperature: {temp:.1f}°C")
            print(f"Humidity: {hum:.1f}%")
            print("-" * 30)
        else:
            print("Sensor reading failed!")
        
        time.sleep(2)  # Read every 2 seconds

if __name__ == "__main__":
    main()
