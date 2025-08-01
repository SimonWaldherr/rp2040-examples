package main

import (
	"machine"
	"time"
)

func main() {
	// Configure I2C
	machine.I2C0.Configure(machine.I2CConfig{
		Frequency: 100000, // 100 kHz
		SDA:       machine.GP16,
		SCL:       machine.GP17,
	})

	println("I2C Scanner Example")
	println("Scanning for I2C devices...")
	println("SDA: GP16, SCL: GP17")

	// Scan for devices
	var foundDevices []uint8

	for addr := uint8(0x08); addr < 0x78; addr++ {
		// Try to write to the address
		err := machine.I2C0.Tx(uint16(addr), []byte{}, nil)

		if err == nil {
			foundDevices = append(foundDevices, addr)
			println("Found device at address:", "0x"+formatHex(addr))
		}

		time.Sleep(1 * time.Millisecond)
	}

	if len(foundDevices) == 0 {
		println("No I2C devices found")
	} else {
		println("Scan complete. Found", len(foundDevices), "device(s)")

		// Print summary
		println("\nDevice addresses:")
		for _, addr := range foundDevices {
			println("  0x" + formatHex(addr) + " (" + identifyDevice(addr) + ")")
		}
	}

	// Example of communicating with a found device
	if len(foundDevices) > 0 {
		exampleCommunication(foundDevices[0])
	}

	// Keep running
	for {
		time.Sleep(1 * time.Second)
	}
}

// formatHex formats a byte as a two-digit hex string
func formatHex(b uint8) string {
	const hex = "0123456789ABCDEF"
	return string([]byte{hex[b>>4], hex[b&0x0F]})
}

// identifyDevice provides a guess about what device might be at the address
func identifyDevice(addr uint8) string {
	switch addr {
	case 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27:
		return "PCF8574 I/O Expander"
	case 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47:
		return "PCA9685 PWM Driver"
	case 0x48, 0x49, 0x4A, 0x4B:
		return "ADS1115 ADC or Temperature Sensor"
	case 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57:
		return "EEPROM (24LC series)"
	case 0x68:
		return "DS3231 RTC or MPU6050 IMU"
	case 0x76, 0x77:
		return "BME280/BMP280 Environmental Sensor"
	case 0x3C, 0x3D:
		return "SSD1306 OLED Display"
	default:
		return "Unknown Device"
	}
}

// exampleCommunication demonstrates basic I2C communication
func exampleCommunication(addr uint8) {
	println("\nTesting communication with device at 0x" + formatHex(addr))

	// Try reading some data
	readBuf := make([]byte, 2)
	err := machine.I2C0.Tx(uint16(addr), nil, readBuf)

	if err == nil {
		println("Successfully read", len(readBuf), "bytes:")
		for i, b := range readBuf {
			println("  Byte", i, ": 0x"+formatHex(b))
		}
	} else {
		println("Failed to read from device")
	}

	// Try writing some data (register 0x00 with value 0x01)
	writeBuf := []byte{0x00, 0x01}
	err = machine.I2C0.Tx(uint16(addr), writeBuf, nil)

	if err == nil {
		println("Successfully wrote", len(writeBuf), "bytes")
	} else {
		println("Failed to write to device")
	}
}
