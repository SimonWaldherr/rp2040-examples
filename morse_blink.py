import machine
import time
import _thread

# Initialisierung der Onboard-LED
led_onboard = machine.Pin(25, machine.Pin.OUT, value=0)

# Morse-Code Definitionen
morse_code = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '0': '-----',
    ' ': ' '
}

# Funktion zum Senden eines Morse-Codes über die LED
def send_morse(text):
    for char in text.upper():
        code = morse_code.get(char, '')
        for symbol in code:
            if symbol == '.':
                led_onboard.on()
                time.sleep(0.2)  # Kurzes Blinken für Punkt
            elif symbol == '-':
                led_onboard.on()
                time.sleep(0.6)  # Langes Blinken für Strich
            led_onboard.off()
            time.sleep(0.2)  # Wartezeit zwischen Symbolen
        time.sleep(0.6)  # Wartezeit zwischen Buchstaben
        
# Hauptprogramm für die Benutzereingabe
while True:
    text = input('Text eingeben, der als Morse-Code gesendet werden soll: ')
    _thread.start_new_thread(send_morse, (text,))
    