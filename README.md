# RP2040 Examples

Welcome to the RP2040 Examples repository! This collection showcases various projects and code samples for the [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/) and other RP2040-based microcontroller boards. Whether you're a beginner looking to get started with MicroPython or an experienced developer exploring Golang on embedded systems, you'll find something useful here.

If you're also interested in Raspberry Pi projects using Golang, be sure to check out my [Raspberry Pi Golang examples](https://github.com/SimonWaldherr/rpi-examples).

---

## Table of Contents

- [Where to Buy](#where-to-buy)
- [Documentation & Resources](#documentation--resources)
- [MicroPython](#micropython)
  - [MicroPython Examples](#micropython-examples)
- [Golang](#golang)
  - [Golang Examples](#golang-examples)
- [Contributing](#contributing)
- [License](#license)

---

## Where to Buy

The Raspberry Pi Pico is a powerful yet affordable microcontroller that you can purchase from various retailers worldwide. Here are some trusted sources:

- [Amazon](https://amzn.to/3JscWee)
- [AZ-Delivery](https://www.az-delivery.de/products/raspberry-pi-pico?variant=39388890988640)
- [BerryBase](https://www.berrybase.de/raspberry-pi-pico-rp2040-mikrocontroller-board)
- [Reichelt](https://www.reichelt.de/raspberry-pi-pico-rp2040-cortex-m0-microusb-rasp-pi-pico-p295706.html)
- [Sparkfun](https://www.sparkfun.com/products/17829?src=raspberrypi)
- [Mouser](https://www.mouser.de/ProductDetail/Raspberry-Pi/SC0915?qs=T%252BzbugeAwjgnLi4azxXVFA%3D%3D&src=raspberrypi)
- [Welectron](https://www.welectron.com/Raspberry-Pi-Pico?src=raspberrypi)

---

## Documentation & Resources

To get the most out of your Raspberry Pi Pico, you can refer to the following documentation and resources:

- [Official Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html) - Comprehensive guide to getting started, programming, and using the Pico.
- [Raspberry Pi Pico Pinout](https://pico.pinout.xyz/) - Visual reference for the GPIO pins on the Pico.

---

## MicroPython

MicroPython is an efficient and beginner-friendly way to program your Raspberry Pi Pico. Follow the links below to download the latest firmware:

- [RPI Pico](https://micropython.org/download/RPI_PICO/)
- [RPI Pico W](https://micropython.org/download/RPI_PICO_W/)
- [RPI Pico 2](https://micropython.org/download/RPI_PICO2/)

### MicroPython Examples

Explore these example scripts to get hands-on with MicroPython:

- **[blink_with_pcf8574.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_pcf8574.py)**  
  Need more GPIO pins? Use a [PCF8574](https://amzn.to/3UzPqCc) I/O expander.

- **[blink_with_ws2812.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_ws2812.py)**  
  Create stunning LED displays with [WS2812 light strips](https://amzn.to/49YVDfr) or [modules](https://amzn.to/3vZMN3t).

- **[distance_with_hc-sr04.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/distance_with_hc-sr04.py)**  
  Accurately measure distances with the [HC-SR04 ultrasonic sensor](https://amzn.to/4bfb30p).

- **[info.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/info.py)**  
  Retrieve and display system information from your Raspberry Pi Pico.

- **[interactive_blink.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/interactive_blink.py)**  
  Control GPIO pins interactively via text input, ideal for use with [Thonny](https://thonny.org/).

- **[morse_blink.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/morse_blink.py)**  
  Convert text into Morse code using an LED on the Pico.

- **[nunchuck.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/nunchuck.py)**  
  Interface with a [Wii Nunchuck](https://amzn.to/3z5ISDt) using a [Nunchuck adapter](https://www.berrybase.de/adafruit-wii-nunchuck-breakout-adapter).

- **[pwm_with_pca9685.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/pwm_with_pca9685.py)**  
  Control up to 16 servos using the [PCA9685](https://amzn.to/3UemVsB) PWM driver.

- **[read_rfid_with_rc522.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/read_rfid_with_rc522.py)**  
  Implement RFID reading using the [RC522 module](https://amzn.to/3xKmvm3).

- **[snake_on_hub75_zeroplayer.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/snake_on_hub75_zeroplayer.py)**  
  Display a snake animation on a [Hub75 LED-Matrix](https://amzn.to/4bbOwSm) with a [Pimoroni Interstate 75 W](https://shop.pimoroni.com/products/interstate-75-w?variant=40453881299027). For a playable version, see my [DIY-Arcade-Machine](https://github.com/SimonWaldherr/DIY-Arcade-Machine).

- **[weigh_with_hx711.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/weigh_with_hx711.py)**  
  Build a digital scale using a [load cell and the HX711](https://amzn.to/4b3HnTE) A/D converter.

- **[wlan.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/wlan.py)**  
  Connect your Pico to WiFi and fetch data from the web.

- **[adc.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/adc.py)**  
  Read analog signals using the Pico’s built-in ADC pins.

- **[balls_on_hub75.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/balls_on_hub75.py)**  
  Simulate bouncing balls on a Hub75 LED-Matrix.

- **[conway_on_hub75.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/conway_on_hub75.py)**  
  Implement Conway's Game of Life on a Hub75 LED-Matrix.

- **[floodfill_on_hub75.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/floodfill_on_hub75.py)**  
  Visualize a flood fill algorithm on a Hub75 LED-Matrix.

- **[joystick.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/joystick.py)**  
  Interface a joystick with the Pico for simple gaming or control applications.

- **[read_rfid_with_rc522_with_light.py](https://github.com/SimonWaldherr/rp2040-examples/blob/main/read_rfid_with_rc522_with_light.py)**  
  Enhance RFID reading with visual feedback using LEDs.

---

## Golang

For those who prefer to code in Golang, this section provides examples of using Golang on the Raspberry Pi Pico with the [TinyGo](https://tinygo.org/) compiler.

### Golang Examples

- **[blink.go](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink.go)**  
  Blink an LED using Golang. Install TinyGo and compile with:

  ```bash
  tinygo build -o blink.uf2 -target=pico blink.go
  ```

  Flash directly to the Pico with:

  ```bash
  tinygo flash -target=pico blink.go
  ```

  Add `-monitor` to the command to see the program’s output in the terminal.

- **[blink_with_ws2812.go](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_ws2812.go)**  
  Control WS2812 LEDs using Golang, creating vibrant lighting effects.

- **[blink_with_ws2812_struct.go](https://github.com/SimonWaldherr/rp2040-examples/blob/main/blink_with_ws2812_struct.go)**  
  An advanced example for controlling WS2812 LEDs using structured Golang code.

- **[read_rfid_with_rc522.go](https://github.com/SimonWaldherr/rp2040-examples/blob/main/read_rfid_with_rc522.go)**  
  Read RFID cards and tags using the RC522 module and Golang.

---

## Contributing

Contributions are welcome! If you have a project or code sample you'd like to share, feel free to submit a pull request.

---

## License

This repository is licensed under the MIT License. For more details, see the [LICENSE](LICENSE) file.

---

Feel free to explore the examples and contribute to this growing repository! Whether you're building a simple LED blinker or a complex sensor network, these examples are designed to help you get the most out of your Raspberry Pi Pico.

---
