# SMART Camera with a LoPy
#
# Boot script
#
# Author:  J. Barthelemy
# Update: N. Verstaevel - nicolas.verstaevel@uow.edu.au
# Version: 07 March 2018

# credentials
APP_EUI = ''
APP_KEY = ''

# max number of connection attemps to TTN
MAX_JOIN_ATTEMPT = const(50)

# number of packets to be transmit with the same data  (retries)
# default is 3
N_TX = const(3)

FRAME_SIZE = 10

# data rate used to send message via LoRaWAN:
# 1 (slowest - longest range) to 4 (fastest - smallest range)
DATA_RATE = const(4)

# sampling interval (in milliseconds)
INT_SAMPLING = const(10 * 60 * 1000)

# Set flag to true if you want to force the join to The Things Network
# and have access to the REPL interface
FORCE_JOIN = False
