package main

import (
	"image/color"
	"machine"
	"time"

	"tinygo.org/x/drivers/ws2812"
)

const (
	ledCount   int     = 24
	pinNum     uint8   = 28
	brightness float32 = 0.8
)

var (
	pixelArray [ledCount]color.RGBA
	leds       ws2812.Device
)

func hsbToRGB(h, s, b float32) (byte, byte, byte) {
	if s == 0 {
		brightness := byte(b * 255)
		return brightness, brightness, brightness
	}

	h = float32(int(h)%360) / 60
	i := int(h)
	f := h - float32(i)
	p := b * (1 - s)
	q := b * (1 - s*f)
	t := b * (1 - s*(1-f))

	p8, q8, t8, b8 := byte(p*255), byte(q*255), byte(t*255), byte(b*255)

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

func setLED(index int, r, g, b byte) {
	pixelArray[index] = color.RGBA{R: r, G: g, B: b, A: 255}
}

func updatePixels() {
	buf := make([]color.RGBA, ledCount)
	for i := 0; i < ledCount; i++ {
		buf[i] = pixelArray[i]
	}
	leds.WriteColors(buf)
	time.Sleep(10 * time.Millisecond)
}

func main() {
	machine.InitADC()
	pin := machine.Pin(pinNum)
	pin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	leds = ws2812.New(pin)

	background := [3]byte{15, 15, 15}
	trailLength := 4

	for ii := 0; ii < ledCount*20000+1; ii++ {
		r, g, b := hsbToRGB(float32(ii*9), 1, 0.8)
		setLED(ii%ledCount, r, g, b)
		for j := 0; j < trailLength; j++ {
			if ii-j-1 >= 0 {
				r, g, b := hsbToRGB(float32(ii*9), 1, 0.8*float32(trailLength-j)/float32(trailLength))
				setLED((ii-j-1)%ledCount, r, g, b)
			}
		}
		if ii > trailLength {
			setLED((ii-trailLength-1)%ledCount, background[0], background[1], background[2])
		}
		updatePixels()
		time.Sleep(50 * time.Millisecond)
	}
}
