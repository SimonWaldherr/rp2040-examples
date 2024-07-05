# Bibliotheken laden
from machine import ADC

# Initialisierung des ADC0 (GPIO26)
adc = ADC(0)

while True:
	# ADC0 als Dezimalzahl lesen
	read = adc.read_u16()
	
	# Spannung berechnen
	voltage = read * 3.3 / 65536
	
	# Daten ausgeben
	print('ADC:', read, '/', voltage, 'V')
	
	sleep(1)  # Pause zwischen den Messungen


	