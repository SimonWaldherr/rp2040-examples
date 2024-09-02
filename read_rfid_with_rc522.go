package main

import (
	"machine"
	"time"
)

// Constants for RC522
const (
	DEBUG    = false
	OK       = 0
	NOTAGERR = 1
	ERR      = 2

	REQIDL        = 0x26
	REQALL        = 0x52
	AUTHENT1A     = 0x60
	AUTHENT1B     = 0x61
	PICCANTICOLL1 = 0x93
	PICCANTICOLL2 = 0x95
	PICCANTICOLL3 = 0x97
)

type RC522 struct {
	sck  machine.Pin
	mosi machine.Pin
	miso machine.Pin
	rst  machine.Pin
	cs   machine.Pin
	spi  *machine.SPI
}

func NewRC522(sckPin, mosiPin, misoPin, rstPin, csPin uint8) *RC522 {
	r := &RC522{
		sck:  machine.Pin(sckPin),
		mosi: machine.Pin(mosiPin),
		miso: machine.Pin(misoPin),
		rst:  machine.Pin(rstPin),
		cs:   machine.Pin(csPin),
	}
	r.sck.Configure(machine.PinConfig{Mode: machine.PinOutput})
	r.mosi.Configure(machine.PinConfig{Mode: machine.PinOutput})
	r.miso.Configure(machine.PinConfig{Mode: machine.PinInput})
	r.rst.Configure(machine.PinConfig{Mode: machine.PinOutput})
	r.cs.Configure(machine.PinConfig{Mode: machine.PinOutput})

	r.spi = machine.SPI0
	r.spi.Configure(machine.SPIConfig{
		Frequency: 1000000,
		Mode:      0,
		SCK:       r.sck,
		SDO:       r.mosi,
		SDI:       r.miso,
	})

	r.rst.Low()
	r.cs.High()
	r.rst.High()
	r.init()
	return r
}

func (r *RC522) WriteRegister(reg uint8, val uint8) {
	r.cs.Low()
	r.spi.Transfer(uint8((reg << 1) & 0x7E))
	r.spi.Transfer(val)
	r.cs.High()
}

func (r *RC522) ReadRegister(reg uint8) uint8 {
	r.cs.Low()
	r.spi.Transfer(uint8(((reg << 1) & 0x7E) | 0x80))
	val, _ := r.spi.Transfer(0) // Ignore the error for now
	r.cs.High()
	return val
}

func (r *RC522) SetFlags(reg, mask uint8) {
	val := r.ReadRegister(reg)
	r.WriteRegister(reg, val|mask)
}

func (r *RC522) ClearFlags(reg, mask uint8) {
	val := r.ReadRegister(reg)
	r.WriteRegister(reg, val & ^mask)
}

func (r *RC522) init() {
	r.reset()
	r.WriteRegister(0x2A, 0x8D)
	r.WriteRegister(0x2B, 0x3E)
	r.WriteRegister(0x2D, 30)
	r.WriteRegister(0x2C, 0)
	r.WriteRegister(0x15, 0x40)
	r.WriteRegister(0x11, 0x3D)
	r.antennaOn(true)
}

func (r *RC522) reset() {
	r.WriteRegister(0x01, 0x0F)
}

func (r *RC522) antennaOn(on bool) {
	if on {
		val := r.ReadRegister(0x14)
		if val&0x03 == 0 {
			r.SetFlags(0x14, 0x03)
		}
	} else {
		r.ClearFlags(0x14, 0x03)
	}
}

// Implementation for request method
func (r *RC522) request(mode uint8) (uint8, []uint8) {
	r.WriteRegister(0x0D, 0x07)
	status, recv, _ := r.toCard(0x0C, []uint8{mode})
	if status != OK || len(recv)*8 != 0x10 {
		status = ERR
	}
	return status, recv
}

// Implementation for anticoll method
func (r *RC522) anticoll(anticolN uint8) (uint8, []uint8) {
	serChk := uint8(0)
	ser := []uint8{anticolN, 0x20}
	r.WriteRegister(0x0D, 0x00)
	status, recv, _ := r.toCard(0x0C, ser)
	if status == OK {
		if len(recv) == 5 {
			for i := 0; i < 4; i++ {
				serChk ^= recv[i]
			}
			if serChk != recv[4] {
				status = ERR
			}
		} else {
			status = ERR
		}
	}
	return status, recv
}

// Implementation for SelectTagSN method
func (r *RC522) SelectTagSN() (uint8, []uint8) {
	validUID := []uint8{}
	status, uid := r.anticoll(PICCANTICOLL1)
	if status != OK {
		return ERR, nil
	}
	if r.PcdSelect(uid, PICCANTICOLL1) == 0 {
		return ERR, nil
	}
	if uid[0] == 0x88 {
		validUID = append(validUID, uid[1:4]...)
		status, uid = r.anticoll(PICCANTICOLL2)
		if status != OK {
			return ERR, nil
		}
		if r.PcdSelect(uid, PICCANTICOLL2) == 0 {
			return ERR, nil
		}
		if uid[0] == 0x88 {
			validUID = append(validUID, uid[1:4]...)
			status, uid = r.anticoll(PICCANTICOLL3)
			if status != OK {
				return ERR, nil
			}
			if r.PcdSelect(uid, PICCANTICOLL3) == 0 {
				return ERR, nil
			}
		}
	}
	validUID = append(validUID, uid[0:5]...)
	return OK, validUID[:len(validUID)-1]
}

func (r *RC522) toCard(cmd uint8, send []uint8) (uint8, []uint8, uint8) {
	var recv []uint8
	var bits, irqEn, waitIRq uint8
	var n uint8
	var stat uint8 = ERR

	if cmd == 0x0E {
		irqEn = 0x12
		waitIRq = 0x10
	} else if cmd == 0x0C {
		irqEn = 0x77
		waitIRq = 0x30
	}

	r.WriteRegister(0x02, irqEn|0x80)
	r.ClearFlags(0x04, 0x80)
	r.SetFlags(0x0A, 0x80)
	r.WriteRegister(0x01, 0x00)

	for _, c := range send {
		r.WriteRegister(0x09, c)
	}
	r.WriteRegister(0x01, cmd)

	if cmd == 0x0C {
		r.SetFlags(0x0D, 0x80)
	}

	for i := 2000; i > 0; i-- {
		n = r.ReadRegister(0x04)
		if n&0x01 == 0 && n&waitIRq == 0 {
			continue
		}
		break
	}

	r.ClearFlags(0x0D, 0x80)

	if (r.ReadRegister(0x06) & 0x1B) == 0x00 {
		stat = OK
		if n&irqEn&0x01 != 0 {
			stat = NOTAGERR
		} else if cmd == 0x0C {
			n = r.ReadRegister(0x0A)
			lBits := r.ReadRegister(0x0C) & 0x07
			if lBits != 0 {
				bits = (n-1)*8 + lBits
			} else {
				bits = n * 8
			}
			if n == 0 {
				n = 1
			} else if n > 16 {
				n = 16
			}
			for i := uint8(0); i < n; i++ {
				recv = append(recv, r.ReadRegister(0x09))
			}
		}
	}
	return stat, recv, bits
}

// PcdSelect is the helper method for selecting the tag.
func (r *RC522) PcdSelect(serNum []uint8, anticolN uint8) uint8 {
	buf := append([]uint8{anticolN, 0x70}, serNum...)
	pOut := r.calculateCRC(buf)
	buf = append(buf, pOut...)
	status, _, backLen := r.toCard(0x0C, buf)
	if status == OK && backLen == 0x18 {
		return 1
	}
	return 0
}

// calculateCRC calculates CRC value required for RFID communication.
func (r *RC522) calculateCRC(data []uint8) []uint8 {
	r.ClearFlags(0x05, 0x04)
	r.SetFlags(0x0A, 0x80)
	for _, c := range data {
		r.WriteRegister(0x09, c)
	}
	r.WriteRegister(0x01, 0x03)
	for i := 0xFF; i > 0; i-- {
		n := r.ReadRegister(0x05)
		if n&0x04 != 0 {
			break
		}
	}
	return []uint8{r.ReadRegister(0x22), r.ReadRegister(0x21)}
}

func main() {
	r := NewRC522(2, 3, 4, 0, 1)
	var lastCardID uint32 = 0
	i := 0
	println("scanning ...\n")
	for {
		r.init()
		stat, _ := r.request(REQIDL)
		if stat == OK {
			stat, uid := r.SelectTagSN()
			if stat == OK {
				card := uint32(uid[0]) | uint32(uid[1])<<8 | uint32(uid[2])<<16 | uint32(uid[3])<<24
				if card != lastCardID {
					println("CARD ID: ", card)
					lastCardID = card
				}
			}
		}
		time.Sleep(100 * time.Millisecond)
		i++
		if i > 1000 {
			lastCardID = 0
		}
	}
}
