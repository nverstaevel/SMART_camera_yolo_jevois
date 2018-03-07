# SMART Camera with a LoPy
#
# Boot script
#
# Author:  J. Barthelemy
# Update: N. Verstaevel - nicolas.verstaevel@uow.edu.au
# Version: 07 March 2018

from machine import UART
from network import WLAN
import pycom
import os

# deactivate wifi
if pycom.wifi_on_boot:
    wlan = WLAN()
    wlan.deinit()
    pycom.wifi_on_boot(False)

# disabling the heartbeat
pycom.heartbeat(False)

# setting up the communication interface
uart = UART(0, 115200)
os.dupterm(uart)
