# rp2040-examples
Examples for [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/) (RP2040 MCU based SBCs)  
If you're looking for my Raspberry Pi Golang examples, you will find them [here](https://github.com/SimonWaldherr/rpi-examples).  

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
I also recommend this great [Raspberry Pi Pico Pinout](https://pico.pinout.xyz/)-page.  

---

## [blink_with_pcf8574.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_pcf8574.py)  
you need more GPIO-Pins, just use some [PCF8574](https://amzn.to/3UzPqCc).  

## [blink_with_ws2812.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_ws2812.py)  
need more fun with LEDs? Get some [WS2812 light stripes](https://amzn.to/49YVDfr) or [modules](https://amzn.to/3vZMN3t).  

## [distance_with_hc-sr04.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/distance_with_hc-sr04.py)  
measure real world distance with the help of the [HC-SR04 hypersonic module](https://amzn.to/4bfb30p).  

## [info.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/info.py)  
show information about your Pi.  

## [interactive_blink.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/interactive_blink.py)  
accepts text input (e.g. via [Thonny](https://thonny.org/)) in two different formats ```Pin,Status``` or ```Pin,On-Time,Off-Time``` and allows pins to be switched on and off (or flashing the LED (pin 25)).  

## [morse_blink.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/morse_blink.py)  
expects text input and causes the LED on the Raspberry Pi Pico to output this text as Morse code.  

## [pwm_with_pca9685.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/pwm_with_pca9685.py)  
control up to 16 servo motors with only 2 pins from your pico and the magical [PCA9685](https://amzn.to/3UemVsB).  

## [read_rfid_with_rc522.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/read_rfid_with_rc522.py)  
read RFID cards with the [rc522](https://amzn.to/3xKmvm3).  

## [snake_on_hub75.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/snake_on_hub75.py)  
show a funny snake animation on a [hub75 LED-Matrix](https://amzn.to/4bbOwSm) with an [Pimoroni Interstate 75 W](https://shop.pimoroni.com/products/interstate-75-w?variant=40453881299027).  

## [weigh_with_hx711.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/weigh_with_hx711.py)  
uses a [load cell and the HX711](https://amzn.to/4b3HnTE)-24bit A/D converter to measure a weight.  

## [wlan.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/wlan.py)  
connect to your wifi and read json data from the internet.  
