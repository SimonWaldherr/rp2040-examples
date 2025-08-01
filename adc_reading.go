package main

import (
	"machine"
	"time"
)

func main() {
	// Configure ADC pins
	machine.InitADC()
	adc0 := machine.ADC{Pin: machine.ADC0}
	adc1 := machine.ADC{Pin: machine.ADC1}
	adc2 := machine.ADC{Pin: machine.ADC2}

	// Configure pins
	adc0.Configure(machine.ADCConfig{})
	adc1.Configure(machine.ADCConfig{})
	adc2.Configure(machine.ADCConfig{})

	// LED for status
	led := machine.LED
	led.Configure(machine.PinConfig{Mode: machine.PinOutput})

	println("ADC Reading Example")
	println("Reading from ADC0, ADC1, ADC2")
	println("Connect analog sensors or potentiometers")

	for {
		// Read ADC values (0-65535)
		val0 := adc0.Get()
		val1 := adc1.Get()
		val2 := adc2.Get()

		// Convert to voltage (3.3V reference)
		voltage0 := float32(val0) * 3.3 / 65535.0
		voltage1 := float32(val1) * 3.3 / 65535.0
		voltage2 := float32(val2) * 3.3 / 65535.0

		// Print values
		println("ADC0:", val0, "Voltage:", voltage0)
		println("ADC1:", val1, "Voltage:", voltage1)
		println("ADC2:", val2, "Voltage:", voltage2)
		println("------------------------")

		// Toggle LED to show activity
		led.Set(!led.Get())

		time.Sleep(1 * time.Second)
	}
}
