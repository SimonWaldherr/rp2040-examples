from machine import ADC
import time

adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)

while True:
	read0 = adc0.read_u16()
	read1 = adc1.read_u16()
	read2 = adc2.read_u16()
	
	valueX = round(read0 * 10 / 65536)
	valueY = round(read1 * 10 / 65536)
	
	if read2 < 500:
		Button = 1
	else:
		Button = 0
	
	print('X:', valueX, ' Y:', valueY, ' Button:', Button)
	time.sleep(0.4)
