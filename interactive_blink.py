import machine
import sys
import select
import time

# Pin-Datenstruktur initialisieren
pins = {
    25: {'pin_obj': machine.Pin(25, machine.Pin.OUT), 'on_time': 0, 'off_time': 0, 'next_toggle': time.time_ns()}
}

# Eingabebereitschaft prüfen
spoll = select.poll()
spoll.register(sys.stdin, select.POLLIN)

# Eingabe lesen Funktion
def read_full_input():
    input_str = ''
    while True:
        if spoll.poll(0):
            char = sys.stdin.read(1)
            if char == '\n':
                break
            input_str += char
        else:
            break
    return input_str.strip()

def manage_blink(pin, on_time, off_time):
    """Erstellt oder aktualisiert das Blinken für einen bestimmten Pin."""
    global pins
    if pin not in pins:
        pins[pin] = {'pin_obj': machine.Pin(pin, machine.Pin.OUT), 'on_time': 0, 'off_time': 0, 'next_toggle': time.time_ns()}
    # Update blink times and reset toggle
    pins[pin]['on_time'] = on_time * 100000000
    pins[pin]['off_time'] = off_time * 100000000
    if on_time > 0 and off_time > 0:
        pins[pin]['next_toggle'] = time.time_ns()  # Start blinking immediately
    else:
        pins[pin]['pin_obj'].value(0)  # Ensure pin is off when stopped

def set_pin(pin, state):
    """Setzt den Pin auf einen festen Zustand."""
    global pins
    if pin not in pins:
        pins[pin] = {'pin_obj': machine.Pin(pin, machine.Pin.OUT), 'on_time': 0, 'off_time': 0}
    pins[pin]['pin_obj'].value(state)
    pins[pin]['on_time'] = 0
    pins[pin]['off_time'] = 0

# Hauptprogrammschleife
print("Kommando eingeben (Format 'Pin,Bool' oder 'Pin,Delay,Delay'):")
while True:
    command = read_full_input()
    if command:
        parts = command.split(',')
        if len(parts) == 2:
            pin, state = int(parts[0]), int(parts[1])
            set_pin(pin, state)
        elif len(parts) == 3:
            pin, on_time, off_time = int(parts[0]), float(parts[1]), float(parts[2])
            manage_blink(pin, on_time, off_time)

    # Blinklogik verwalten
    current_time = time.time_ns()
    for pin, info in pins.items():
        if info['on_time'] > 0 and info['off_time'] > 0 and current_time >= info['next_toggle']:
            new_state = 1 - info['pin_obj'].value()  # Zustand toggeln
            info['pin_obj'].value(new_state)
            next_delay = info['on_time'] if new_state else info['off_time']
            info['next_toggle'] = current_time + int(next_delay)

    time.sleep(0.1)  # Kleine Verzögerung, um CPU-Last zu minimieren
