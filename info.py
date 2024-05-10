import os
import machine
import network
import sys
import gc
import time

def system_info():
    print("Systeminformationen und Status:")

    # MicroPython Version und Build-Datum
    print("MicroPython Version:", sys.version)
    print("Build-Datum:", os.uname().version)

    # CPU-Informationen
    print("CPU: {}, Frequenz: {} MHz".format(os.uname().machine, machine.freq() // 1000000))

    # System-Uptime
    uptime = time.ticks_ms() // 1000  # Uptime in Sekunden
    print("System-Uptime: {} Sekunden".format(uptime))

    # Speicherinformationen
    gc.collect()  # Bereinigt den nicht verwendeten Speicher
    print("Freier RAM: {} Bytes".format(gc.mem_free()))
    print("Gesamter RAM: {} Bytes".format(gc.mem_alloc() + gc.mem_free()))

    # Netzwerkinformationen
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        print("WLAN verbunden mit:", wlan.config('essid'))
        print("IP-Adresse:", wlan.ifconfig()[0])
        print("Subnetzmaske:", wlan.ifconfig()[1])
        print("Gateway:", wlan.ifconfig()[2])
        print("DNS:", wlan.ifconfig()[3])
        print("Signalstärke:", wlan.status('rssi'), "dBm")
    else:
        print("WLAN nicht verbunden")

    # Maschinen-ID und eindeutige ID
    print("Maschinen-ID:", machine.unique_id())

# Aufruf der Funktion
system_info()
