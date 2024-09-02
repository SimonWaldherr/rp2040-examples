# rp2040-examples
Examples for [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/) (RP2040 MCU-based SBCs).  
If you're looking for my Raspberry Pi Golang examples, you can find them [here](https://github.com/SimonWaldherr/rpi-examples).

---

## Where to Buy

You can purchase the very affordable Raspberry Pi Pico from various retailers:

- [Amazon](https://amzn.to/3JscWee)
- [AZ-Delivery](https://www.az-delivery.de/products/raspberry-pi-pico?variant=39388890988640)
- [BerryBase](https://www.berrybase.de/raspberry-pi-pico-rp2040-mikrocontroller-board)
- [Reichelt](https://www.reichelt.de/raspberry-pi-pico-rp2040-cortex-m0-microusb-rasp-pi-pico-p295706.html)
- [Sparkfun](https://www.sparkfun.com/products/17829?src=raspberrypi)
- [Mouser](https://www.mouser.de/ProductDetail/Raspberry-Pi/SC0915?qs=T%252BzbugeAwjgnLi4azxXVFA%3D%3D&src=raspberrypi)
- [Welectron](https://www.welectron.com/Raspberry-Pi-Pico?src=raspberrypi)

---

## Documentation & Resources

- [Official Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- [Raspberry Pi Pico Pinout](https://pico.pinout.xyz/)

---

## MicroPython

To run MicroPython on your Pico, download the firmware from the official MicroPython page:
- [RPI Pico](https://micropython.org/download/RPI_PICO/)
- [RPI Pico W](https://micropython.org/download/RPI_PICO_W/)
- [RPI Pico 2](https://micropython.org/download/RPI_PICO2/)

### Examples

- **[blink_with_pcf8574.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_pcf8574.py)**  
  Need more GPIO pins? Use a [PCF8574](https://amzn.to/3UzPqCc).

- **[blink_with_ws2812.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_ws2812.py)**  
  Want to have more fun with LEDs? Try using [WS2812 light strips](https://amzn.to/49YVDfr) or [modules](https://amzn.to/3vZMN3t).

- **[distance_with_hc-sr04.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/distance_with_hc-sr04.py)**  
  Measure distances with the [HC-SR04 ultrasonic module](https://amzn.to/4bfb30p).

- **[info.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/info.py)**  
  Display information about your Raspberry Pi Pico.

- **[interactive_blink.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/interactive_blink.py)**  
  Control pins interactively via text input (e.g., using [Thonny](https://thonny.org/)).

- **[morse_blink.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/morse_blink.py)**  
  Translate text input into Morse code with an LED on the Raspberry Pi Pico.

- **[nunchuck.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/nunchuck.py)**  
  Read data from a [Wii Nunchuck](https://amzn.to/3z5ISDt) using a [Nunchuck adapter](https://www.berrybase.de/adafruit-wii-nunchuck-breakout-adapter).

- **[pwm_with_pca9685.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/pwm_with_pca9685.py)**  
  Control up to 16 servos with just 2 pins using the [PCA9685](https://amzn.to/3UemVsB).

- **[read_rfid_with_rc522.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/read_rfid_with_rc522.py)**  
  Read RFID cards with the [RC522](https://amzn.to/3xKmvm3).

- **[snake_on_hub75_zeroplayer.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/snake_on_hub75_zeroplayer.py)**  
  Display a snake animation on a [Hub75 LED-Matrix](https://amzn.to/4bbOwSm) using a [Pimoroni Interstate 75 W](https://shop.pimoroni.com/products/interstate-75-w?variant=40453881299027). For a fully playable game, check out my [DIY-Arcade-Machine](https://github.com/SimonWaldherr/DIY-Arcade-Machine).

- **[weigh_with_hx711.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/weigh_with_hx711.py)**  
  Measure weight using a [load cell and the HX711](https://amzn.to/4b3HnTE) 24-bit A/D converter.

- **[wlan.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/wlan.py)**  
  Connect to WiFi and fetch JSON data from the internet.

- **[adc.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/adc.py)**  
  Read analog signals using the Pico’s ADC pins.

- **[balls_on_hub75.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/balls_on_hub75.py)**  
  Display bouncing balls on a Hub75 LED-Matrix.

- **[conway_on_hub75.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/conway_on_hub75.py)**  
  Implement Conway's Game of Life on a Hub75 LED-Matrix.

- **[floodfill_on_hub75.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/floodfill_on_hub75.py)**  
  Visualize a flood fill algorithm on a Hub75 LED-Matrix.

- **[joystick.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/joystick.py)**  
  Interface with a joystick using the Pico.

- **[read_rfid_with_rc522_with_light.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/read_rfid_with_rc522_with_light.py)**  
  Enhanced RFID reading example with visual feedback.

## Golang

### Examples

- **[blink.go](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink.go)**  
  Blink an LED using Golang. Install [tinygo](https://tinygo.org/) and compile with:

  ```bash
  tinygo build -o blink.uf2 -target=pico blink.go
  ```

  Alternatively, flash directly to the Pico with:

  ```bash
  tinygo flash -target=pico blink.go
  ```

  Add `-monitor` to the command to see the program’s output in the terminal.

- **[blink_with_ws2812.go](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_ws2812.go)**  
  Control WS2812 LEDs using Golang.

- **[blink_with_ws2812_struct.go](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_ws2812_struct.go)**  
  Advanced WS2812 LED control with Golang.

- **[read_rfid_with_rc522.go](https://github.com/SimonWaldherr/rp2040-examples/blob/main/read_rfid_with_rc522.go)**  
  Read RFID cards using Golang.

---

Feel free to explore the examples and contribute!
