import network
import urequests
import json
import time

# local time
print("time before network connect: ", time.time())

# connect to wlan
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('SSID', 'Password') # replace these values

# request world time api data
r = urequests.get("http://worldtimeapi.org/api/timezone/Europe/Berlin")

# parse json
data = json.loads(r.content)

# print unix timestamp from json
print("local time: ", time.time(), " online time: ", data['unixtime'], " delta: ", time.time()-data['unixtime'])

r.close()
