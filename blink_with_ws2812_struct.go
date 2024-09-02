package main

import (
	"image/color"
	"machine"
	"time"

	"tinygo.org/x/drivers/ws2812"
)

// LEDStrip represents the LED strip and its associated properties.
type LEDStrip struct {
	leds        ws2812.Device
	pixelArray  []color.RGBA
	ledCount    int
	brightness  float32
	trailLength int
	background  color.RGBA
}

// NewLEDStrip initializes and returns a new LEDStrip.
func NewLEDStrip(pinNum uint8, ledCount int, brightness float32, trailLength int, background color.RGBA) *LEDStrip {
	pin := machine.Pin(pinNum)
	pin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	leds := ws2812.New(pin)

	return &LEDStrip{
		leds:        leds,
		pixelArray:  make([]color.RGBA, ledCount),
		ledCount:    ledCount,
		brightness:  brightness,
		trailLength: trailLength,
		background:  background,
	}
}

// hsbToRGB converts a color from HSB (Hue, Saturation, Brightness) to RGB format.
// h: Hue angle in degrees [0, 360)
// s: Saturation [0, 1]
// b: Brightness [0, 1]
// Returns: red, green, and blue color components as bytes.
func (strip *LEDStrip) hsbToRGB(h, s, b float32) (byte, byte, byte) {
	if s == 0 {
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

// SetLED sets the RGB color of a specific LED in the array.
func (strip *LEDStrip) SetLED(index int, r, g, b byte) {
	strip.pixelArray[index] = color.RGBA{R: r, G: g, B: b, A: 255}
}

// UpdatePixels sends the current pixel array to the LED strip.
func (strip *LEDStrip) UpdatePixels() {
	strip.leds.WriteColors(strip.pixelArray)
	time.Sleep(10 * time.Millisecond)
}

// Animate runs the main loop to animate the LEDs.
func (strip *LEDStrip) Animate(cycle int) {
	for ii := 0; ii < strip.ledCount*cycle+1; ii++ {
		// Calculate the RGB values for the current position in the animation
		r, g, b := strip.hsbToRGB(float32(ii*9), 1, strip.brightness)
		strip.SetLED(ii%strip.ledCount, r, g, b)

		// Create a trailing effect by gradually dimming the previous LEDs
		for j := 0; j < strip.trailLength; j++ {
			if ii-j-1 >= 0 {
				r, g, b := strip.hsbToRGB(float32(ii*9), 1, strip.brightness*float32(strip.trailLength-j)/float32(strip.trailLength))
				strip.SetLED((ii-j-1)%strip.ledCount, r, g, b)
			}
		}

		// Reset the LED at the end of the trail to the background color
		if ii > strip.trailLength {
			strip.SetLED((ii-strip.trailLength-1)%strip.ledCount, strip.background.R, strip.background.G, strip.background.B)
		}

		// Update the LED strip with the new colors
		strip.UpdatePixels()

		// Delay to control the speed of the animation
		time.Sleep(50 * time.Millisecond)
	}
}

func main() {
	// Create a new LED strip instance with the desired configuration
	ledStrip := NewLEDStrip(
		28,                                      // GPIO pin number
		24,                                      // LED count
		0.8,                                     // Brightness
		4,                                       // Trail length
		color.RGBA{R: 15, G: 15, B: 15, A: 255}, // Dim gray background color
	)

	// Start the LED animation
	ledStrip.Animate(3)
}
