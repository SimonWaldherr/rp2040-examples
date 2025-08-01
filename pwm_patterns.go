package main

import (
	"machine"
	"time"
)

func main() {
	// Configure PWM pins
	pwm0 := machine.PWM0
	pwm1 := machine.PWM1

	// Configure pins for PWM output
	pin0 := machine.GP0
	pin1 := machine.GP1
	pin2 := machine.GP2
	pin3 := machine.GP3

	pin0.Configure(machine.PinConfig{Mode: machine.PinPWM})
	pin1.Configure(machine.PinConfig{Mode: machine.PinPWM})
	pin2.Configure(machine.PinConfig{Mode: machine.PinPWM})
	pin3.Configure(machine.PinConfig{Mode: machine.PinPWM})

	// Configure PWM
	err := pwm0.Configure(machine.PWMConfig{
		Period: 1e6, // 1 second period = 1 Hz
	})
	if err != nil {
		println("PWM0 configuration failed")
		return
	}

	err = pwm1.Configure(machine.PWMConfig{
		Period: 1e6, // 1 second period = 1 Hz
	})
	if err != nil {
		println("PWM1 configuration failed")
		return
	}

	// Get PWM channels for each pin
	ch0, err := pwm0.Channel(pin0)
	if err != nil {
		println("Failed to get channel for pin0")
		return
	}

	ch1, err := pwm0.Channel(pin1)
	if err != nil {
		println("Failed to get channel for pin1")
		return
	}

	ch2, err := pwm1.Channel(pin2)
	if err != nil {
		println("Failed to get channel for pin2")
		return
	}

	ch3, err := pwm1.Channel(pin3)
	if err != nil {
		println("Failed to get channel for pin3")
		return
	}

	println("PWM Example")
	println("PWM signals on GP0, GP1, GP2, GP3")
	println("Connect LEDs or oscilloscope to see the signals")

	// Variables for different PWM patterns
	var counter uint32 = 0

	for {
		// Calculate duty cycles with different patterns
		// Channel 0: Sawtooth wave (0-100%)
		duty0 := (counter % 100) * 65535 / 100

		// Channel 1: Triangle wave
		triangle := counter % 200
		if triangle > 100 {
			triangle = 200 - triangle
		}
		duty1 := triangle * 65535 / 100

		// Channel 2: Sine-like approximation using steps
		sineSteps := []uint32{0, 25, 50, 75, 100, 75, 50, 25}
		duty2 := sineSteps[counter%8] * 65535 / 100

		// Channel 3: Square wave (50% duty cycle with 2x period)
		var duty3 uint32
		if (counter/50)%2 == 0 {
			duty3 = 32767 // ~50% duty
		} else {
			duty3 = 0
		}

		// Set PWM duty cycles
		pwm0.Set(ch0, duty0)
		pwm0.Set(ch1, duty1)
		pwm1.Set(ch2, duty2)
		pwm1.Set(ch3, duty3)

		// Print current values every 10 iterations
		if counter%10 == 0 {
			println("Counter:", counter)
			println("  CH0 (Sawtooth):", duty0*100/65535, "%")
			println("  CH1 (Triangle):", duty1*100/65535, "%")
			println("  CH2 (Steps):", duty2*100/65535, "%")
			println("  CH3 (Square):", duty3*100/65535, "%")
		}

		counter++
		time.Sleep(100 * time.Millisecond)
	}
}
