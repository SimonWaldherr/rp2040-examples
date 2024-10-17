package main

import (
	"image/color"
	"machine"
	"time"

	"tinygo.org/x/drivers/ws2812"
)

const (
	// ledCount defines the total number of LEDs in the strip.
	ledCount int = 24
	// pinNum specifies the GPIO pin connected to the LED strip.
	pinNum uint8 = 28
	// brightness is a multiplier to adjust the overall brightness of the LEDs.
	brightness float32 = 0.8
)

var (
	// pixelArray holds the current color values for each LED.
	pixelArray [ledCount]color.RGBA
	// leds is the device instance to control the WS2812 LED strip.
	leds ws2812.Device
)

// hsbToRGB converts a color from HSB (Hue, Saturation, Brightness) to RGB format.
// h: Hue angle in degrees [0, 360)
// s: Saturation [0, 1]
// b: Brightness [0, 1]
// Returns: red, green, and blue color components as bytes.
func hsbToRGB(h, s, b float32) (byte, byte, byte) {
	if s == 0 {
		// If saturation is zero, the color is a shade of gray.
		brightness := byte(b * 255)
		return brightness, brightness, brightness
	}

	h = float32(int(h)%360) / 60 // Convert hue to a position within a hexagon (0-6)
	i := int(h)                  // Get the hexagon sector
	f := h - float32(i)          // Fractional part of h within the sector
	p := b * (1 - s)             // Intermediate value for color mixing
	q := b * (1 - s*f)
	t := b * (1 - s*(1-f))

	// Convert intermediate float values to bytes
	p8, q8, t8, b8 := byte(p*255), byte(q*255), byte(t*255), byte(b*255)

	// Return the correct RGB values depending on the sector of the hexagon
	switch i {
	case 0:
		return b8, t8, p8
	case 1:
		return q8, b8, p8
	case 2:
		return p8, b8, t8
	case 3:
		return p8, q8, b8
	case 4:
		return t8, p8, b8
	default:
		return b8, p8, q8
	}
}

// setLED sets the RGB color of a specific LED in the array.
func setLED(index int, r, g, b byte) {
	pixelArray[index] = color.RGBA{R: r, G: g, B: b, A: 255}
}

// updatePixels sends the current pixel array to the LED strip.
func updatePixels() {
	// Create a buffer to hold the colors to be sent to the LED strip.
	buf := make([]color.RGBA, ledCount)
	for i := 0; i < ledCount; i++ {
		buf[i] = pixelArray[i]
	}
	// Write the colors to the LED strip
	leds.WriteColors(buf)
	// Small delay to ensure the update is visible
	time.Sleep(10 * time.Millisecond)
}

func main() {
	// Initialize the hardware (e.g., ADC) if necessary
	machine.InitADC()

	// Configure the GPIO pin for output to control the LED strip
	pin := machine.Pin(pinNum)
	pin.Configure(machine.PinConfig{Mode: machine.PinOutput})

	// Initialize the WS2812 device with the specified pin
	leds = ws2812.New(pin)

	// Background color (dim gray)
	background := [3]byte{15, 15, 15}
	// Length of the LED trail effect
	trailLength := 4

	// Main loop to animate the LEDs
	for ii := 0; ii < ledCount*20000+1; ii++ {
		// Calculate the RGB values for the current position in the animation
		r, g, b := hsbToRGB(float32(ii*9), 1, brightness)
		setLED(ii%ledCount, r, g, b)

		// Create a trailing effect by gradually dimming the previous LEDs
		for j := 0; j < trailLength; j++ {
			if ii-j-1 >= 0 {
				r, g, b := hsbToRGB(float32(ii*9), 1, brightness*float32(trailLength-j)/float32(trailLength))
				setLED((ii-j-1)%ledCount, r, g, b)
			}
		}

		// Reset the LED at the end of the trail to the background color
		if ii > trailLength {
			setLED((ii-trailLength-1)%ledCount, background[0], background[1], background[2])
		}

		// Update the LED strip with the new colors
		updatePixels()

		// Delay to control the speed of the animation
		time.Sleep(50 * time.Millisecond)
	}
}
