package main

import (
	"machine"
	"time"
)

func main() {
	// Configure button pin with pull-up resistor
	button := machine.GP14
	button.Configure(machine.PinConfig{Mode: machine.PinInputPullup})

	// Configure LED pin
	led := machine.LED
	led.Configure(machine.PinConfig{Mode: machine.PinOutput})

	// Button state tracking
	var lastButtonState bool = true // Pull-up means true when not pressed
	var buttonPressed bool = false

	println("Button and LED Control Example")
	println("Press button on GP14 to toggle LED")

	for {
		// Read current button state
		currentButtonState := button.Get()

		// Detect button press (transition from high to low due to pull-up)
		if lastButtonState && !currentButtonState {
			buttonPressed = !buttonPressed
			led.Set(buttonPressed)

			if buttonPressed {
				println("LED ON")
			} else {
				println("LED OFF")
			}
		}

		lastButtonState = currentButtonState

		// Small delay to debounce and prevent excessive CPU usage
		time.Sleep(50 * time.Millisecond)
	}
}
