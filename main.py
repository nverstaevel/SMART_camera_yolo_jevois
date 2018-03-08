from network import LoRa
from machine import UART
import binascii
import socket
import time
import struct
import config
import gc
import cayenneLPP

# enabling garbage collector
gc.enable()

nb_people = 0
nb_frame = 0

detect_list = [0, 0, 0, 0, 0, 0, 0, 0 , 0, 0,0, 0, 0, 0, 0, 0, 0, 0 , 0, 0]
detect_list_index = 0

# init Lorawan
lora = LoRa(mode=LoRa.LORAWAN, adr=False, tx_retries=0, device_class=LoRa.CLASS_A, region=LoRa.AU915)

# init uart
uart1 = UART(1, baudrate=115200, timeout_chars=7)

security_delay = 0.5

FRAME_SIZE = 10

def init_camera():
    global security_delay
    print("Talking to camera")
    #Init JeVois
    print("Initiating camera serout")
    uart1.write("setpar serout Hard\n")
    time.sleep(security_delay)
    print("Initiating camera serlog")
    uart1.write("setpar serlog Hard\n")
    time.sleep(security_delay)
    print("Initiating YOLO detection")
    uart1.write("setmapping2 YUYV 640 480 15.0 Jevois DarknetYOLO \n")
    time.sleep(security_delay)
    print("Initiating serstyle")
    uart1.write("setpar serstyle Normal\n")
    time.sleep(security_delay)
    print("Starting stream")
    uart1.write("streamon\n")
    time.sleep(security_delay)
    print("Camera Initialised")

def deactivate_camera():
    global security_delay
    uart1.write("streamoff\n")
    time.sleep(security_delay)


def join_lora(force_join = False):
    print ('''Joining The Things Network ''')

    # restore previous state
    if not force_join:
        lora.nvram_restore()

    # remove default channels
    for i in range(16, 65):
        lora.remove_channel(i)
    for i in range(66, 72):
        lora.remove_channel(i)

    if not lora.has_joined() or force_join == True:

        # create an OTA authentication params
        app_eui = binascii.unhexlify(config.APP_EUI.replace(' ',''))
        app_key = binascii.unhexlify(config.APP_KEY.replace(' ',''))

        # join a network using OTAA if not previously done
        lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

        # wait until the module has joined the network
        attempt = 0
        while not lora.has_joined() and attempt < config.MAX_JOIN_ATTEMPT:
            time.sleep(2.5)
            attempt = attempt + 1
            print("Trying to join...")
        print("TTN Joined")
        # saving the state
        if not force_join:
            lora.nvram_save()

        # returning whether the join was successful
        if lora.has_joined():
            return True
        else:
            return False
    else:
        return True

def send_nb_people():
    global nb_people
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)
    s.setblocking(True)

    # creating Cayenne LPP packet
    lpp = cayenneLPP.CayenneLPP(size = 100, sock = s)

    lpp.add_analog_input(nb_people)

    # sending the packet via the socket
    lpp.send()
    return nb_people

def read_YOLO_output():
    global nb_people
    global nb_frame
    global detect_list
    global detect_list_index
    global FRAME_SIZE
    '''Reading the YOLO output via serial port '''
    # reading the value from serial port (RS232)
    yolo_output_string = uart1.readline()
    if(not yolo_output_string is None):
        yolo_output_list = yolo_output_string.split()
    #print (yolo_output)
    #dist = int(str(dist_raw).split('\\rR')[-2])
        # print(yolo_output_list)
        if(len(yolo_output_list) > 2 and "person" in yolo_output_list[1] ):
            s = yolo_output_list[1] + ' ' + yolo_output_list[2] + ' ' + yolo_output_list[3] + '\n'
            print(s)
            nb_people += 1
            # print(nb_people)
        if(len(yolo_output_list) > 2 and "Predicted" in yolo_output_list[2]):
            print("New Frame : " + str(nb_people) + " detected!")
            print("Frame number : " + str(detect_list_index))
            detect_list[detect_list_index] = nb_people
            print(detect_list)
            if detect_list_index >= (FRAME_SIZE-1):
                nb_people = max(detect_list)
                print("Sending " + str(nb_people) + " people detected....")
                send_nb_people()
            nb_people = 0
            detect_list_index = (detect_list_index + 1) % FRAME_SIZE

'''
################################################################################
#
# Main script
#
# 1. Join Lorawan
# 2. Read YOLO output
# 3. Send nbPeople
#
################################################################################
'''
# try:
init_camera()
if join_lora(config.FORCE_JOIN):
    send_nb_people()
    while True:
        read_YOLO_output()
# except:
#     nb_people = -2
#     send_nb_people()
#     nb_people = 0
#deepsleep(time) + from machine import deepsleep
