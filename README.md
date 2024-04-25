# rp2040-examples
Examples for [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/) (RP2040 MCU based SBCs)

---

You can get the very cheap Raspberry Pi Pico from many retailers:  
* [Amazon](https://amzn.to/3JscWee)
* [AZ-Delivery](https://www.az-delivery.de/products/raspberry-pi-pico?variant=39388890988640)
* [BerryBase](https://www.berrybase.de/raspberry-pi-pico-rp2040-mikrocontroller-board)
* [Reichelt](https://www.reichelt.de/raspberry-pi-pico-rp2040-cortex-m0-microusb-rasp-pi-pico-p295706.html)
* [Sparkfun](https://www.sparkfun.com/products/17829?src=raspberrypi)
* [Mouser](https://www.mouser.de/ProductDetail/Raspberry-Pi/SC0915?qs=T%252BzbugeAwjgnLi4azxXVFA%3D%3D&src=raspberrypi)
* [Welectron](https://www.welectron.com/Raspberry-Pi-Pico?src=raspberrypi)

---

A good documentation is also available [here](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html).  

---

## [blink_with_pcf8574.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_pcf8574.py)  
you need more GPIO-Pins, just use some [PCF8574](https://amzn.to/3UzPqCc).  

## [blink_with_ws2812.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_ws2812.py)  
need more fun with LEDs? Get some [WS2812 light stripes](https://amzn.to/49YVDfr) or [modules](https://amzn.to/3vZMN3t).  

## [distance_with_hc-sr04.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/distance_with_hc-sr04.py)  
measure real world distance with the help of the [HC-SR04 hypersonic module](https://amzn.to/4bfb30p).  

## [interactive_blink.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/interactive_blink.py)  
accepts text input (e.g. via [Thonny](https://thonny.org/)) in two different formats ```Pin,Status``` or ```Pin,On-Time,Off-Time``` and allows pins to be switched on and off (or flashing the LED (pin 25)).  

## [morse_blink.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/morse_blink.py)  
expects text input and causes the LED on the Raspberry Pi Pico to output this text as Morse code.  

## [read_rfid_with_rc552.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/read_rfid_with_rc552.py)  
read RFID cards with the [rc522](https://amzn.to/3xKmvm3).  

## [weigh_with_hx711.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/weigh_with_hx711.py)  
uses a [load cell and the HX711](https://amzn.to/4b3HnTE)-24bit A/D converter to measure a weight.  
