from machine import Pin, UART
import time

def main():
    """UART communication example with GPS-like data simulation"""
    print("UART Communication Example")
    print("=" * 30)
    
    # Initialize UART
    # UART0: TX=Pin(0), RX=Pin(1)
    # UART1: TX=Pin(4), RX=Pin(5) or TX=Pin(8), RX=Pin(9)
    uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
    
    # LED for status indication
    led = Pin(25, Pin.OUT)
    
    # GPS-like NMEA sentence simulation
    sentence_count = 0
    
    print("Sending GPS-like NMEA sentences via UART...")
    print("Connect another device to GPIO 4 (TX) and GPIO 5 (RX)")
    print("Baudrate: 9600, 8N1")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Create a sample NMEA sentence (GPS format)
            sentence_count += 1
            latitude = 52.5200 + (sentence_count % 100) / 10000  # Berlin area
            longitude = 13.4050 + (sentence_count % 100) / 10000
            
            # GPGGA sentence format (GPS Fix Data)
            nmea_sentence = f"$GPGGA,120000.00,{latitude:.6f},N,{longitude:.6f},E,1,08,1.0,50.0,M,46.0,M,,*47"
            
            # Send via UART
            uart.write(nmea_sentence + '\r\n')
            print(f"Sent: {nmea_sentence}")
            
            # Check for incoming data
            if uart.any():
                received = uart.read()
                if received:
                    print(f"Received: {received.decode('utf-8', errors='ignore').strip()}")
            
            # Toggle LED to show activity
            led.toggle()
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nUART communication stopped")
        led.value(0)

def echo_server():
    """Simple UART echo server"""
    print("UART Echo Server")
    print("=" * 20)
    
    uart = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
    
    print("Echo server started on UART1 (GPIO 4/5)")
    print("Baudrate: 115200")
    print("Send data to see it echoed back")
    
    try:
        while True:
            if uart.any():
                data = uart.read()
                if data:
                    # Echo back the received data
                    uart.write(data)
                    print(f"Echoed: {data.decode('utf-8', errors='ignore').strip()}")
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        print("\nEcho server stopped")

def uart_bridge():
    """Bridge between two UART interfaces"""
    print("UART Bridge Example")
    print("=" * 20)
    
    # Initialize two UART interfaces
    uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
    uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
    
    print("UART Bridge active:")
    print("UART0: GPIO 0 (TX), GPIO 1 (RX)")
    print("UART1: GPIO 4 (TX), GPIO 5 (RX)")
    print("Data will be forwarded between interfaces")
    
    try:
        while True:
            # Forward data from UART0 to UART1
            if uart0.any():
                data = uart0.read()
                if data:
                    uart1.write(data)
                    print(f"0->1: {data.decode('utf-8', errors='ignore').strip()}")
            
            # Forward data from UART1 to UART0
            if uart1.any():
                data = uart1.read()
                if data:
                    uart0.write(data)
                    print(f"1->0: {data.decode('utf-8', errors='ignore').strip()}")
            
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        print("\nUART bridge stopped")

if __name__ == "__main__":
    # Uncomment the function you want to run:
    main()              # GPS-like data transmission
    # echo_server()     # Echo server
    # uart_bridge()     # UART bridge
