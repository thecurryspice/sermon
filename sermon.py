import serial
import io
import subprocess
import pyautogui
from time import sleep
from enum import IntEnum
###########################################################################################################################################
# Priority definitions for output
class Priority(IntEnum):
    SILENT = 5
    ERROR = 4
    SETTING = 3
    EVENT = 2
    GUI = 1
    ALL = 0

# Variables
BAUD_LIST = [9600, 19200, 38400, 57600, 115200, 230400]
BAUDRATE = 9600
PORT = ""
PORT_LIST = []
serialReceiver = serial.Serial()
VerbosePriority = Priority.ALL

BLUE =  '\033[1;38;2;32;64;227m'
RED =   '\033[1;38;2;227;32;32m'
GREEN = '\033[0;38;2;0;192;0m'
YELLOW ='\033[0;38;2;192;192;0m'
NC =    '\033[0m'

###########################################################################################################################################
# console messages according to priority
def consolePrint(msg, *options):
    # check whether only priority has been specified
    if len(options) == 1:
        priority = options[0]
        if priority >= VerbosePriority:
            if priority == Priority.ERROR:
                print(RED + '>>> ' + msg + NC)
            elif priority == Priority.SETTING:
                print(BLUE + '>>> ' + msg + NC)
            elif priority == Priority.EVENT:
                print(YELLOW + '>>> ' + msg + NC)
    # check whether both have been specified
    elif len(options) == 2:
        priority = options[0]
        colour = options[1]
        if priority >= VerbosePriority:
            print(colour + '>>> ' + msg + NC)
    else:
        if VerbosePriority == Priority.ALL:
            print('>>> ' + msg)


# returns output of a terminal command
def cmdLine(cmd):
    process = subprocess.Popen(args = cmd, stdout = subprocess.PIPE, universal_newlines = True, shell = True)
    return process.communicate()[0]

###########################################################################################################################################
'''
-------------------------
SERIAL SPECIFIC FUNCTIONS
-------------------------
'''

# scan ports
def quickScan():
    global PORT_LIST, PORT
    for x in range(len(PORT_LIST)):
        PORT_LIST.pop(0)
    portList = str(cmdLine("python -m serial.tools.list_ports")).split("\n")
    for port in portList:
        # find and eliminate trailing whitespaces
        wsi = str(port).find(' ')
        PORT_LIST.append(str(port)[0:wsi])
    
#return choice
def choosePort():
    global PORT_LIST, PORT
    print("\nScanning Available Ports...\n---------------------")
    sleep(0.5)
    for x in range(len(PORT_LIST)):
        PORT_LIST.pop(0)
    portList = str(cmdLine("python -m serial.tools.list_ports")).split("\n")
    for port in portList:
        # find and eliminate trailing whitespaces
        wsi = str(port).find(' ')
        PORT_LIST.append(str(port)[0:wsi])
    # subtract 1 to compensate newline
    for x in range(len(PORT_LIST)-1):
        print (str(x+1)+") "+str(PORT_LIST[x]))
    print (str(len(PORT_LIST))+") Rescan")
    i = int(input("---------------------\nSelect Option #"))
    # print(PORT_LIST)
    # an extra "newline" is stored in the list, therefore only <, not <=
    if(i < len(PORT_LIST)):
        return PORT_LIST[i-1]
    else:
        choosePort()

# configure port specifics
def configurePort():
    global PORT, BAUDRATE, BAUD_LIST, serialReceiver
    PORT = choosePort()
    print("\nAvailable Baud Rates:\n---------------------")
    for x in range(len(BAUD_LIST)):
        print (str(x+1)+") "+str(BAUD_LIST[x]))
    i = int(input("---------------------\nSelect Option #"))
    if(i <= len(BAUD_LIST)):
        BAUDRATE = BAUD_LIST[i-1]
    else:
        BAUDRATE = 115200

# start Receiver
def startReceiver():
    global PORT, BAUDRATE, serialReceiver
    configurePort()
    try:
        sleep(1)
        serialReceiver =  serial.Serial(PORT, BAUDRATE)
        sleep(0.5)
        consolePrint("Driver Running", Priority.EVENT, GREEN)
    except serial.serialutil.SerialException as e:
        consolePrint("No device was detected on " + str(PORT), Priority.ERROR)
        startReceiver()

# restart on fail
def restartReceiver():
    global PORT, BAUDRATE, serialReceiver
    try:
        consolePrint("Attempting to restart", Priority.EVENT)
        # may have failed because of jitter on wires, give it time to rest 
        sleep(0.5)
        serialReceiver =  serial.Serial(PORT, BAUDRATE)
        consolePrint("Monitoring Serial", Priority.EVENT, GREEN)
        manageDevice(' ')
    except serial.serialutil.SerialException as e:
        consolePrint("Port collapsed. Device disconnected unexpectedly", Priority.ERROR)
        serialReceiver.close()
        startReceiver()

'''
-------------------------
SERIAL SPECIFIC FUNCTIONS
-------------------------
'''
###########################################################################################################################################
'''
-----------------
INPUT AND CONTROL
-----------------
'''

# manager
def manageDevice(ch):

    # example function: print cursor position when 'c' is read
    if ch == 'c':
        try:
            x, y = pyautogui.position()
            msg = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            consolePrint(msg, Priority.GUI)
        except:
            pass
'''
-----------------
INPUT AND CONTROL
-----------------
'''
###########################################################################################################################################
'''
BOOT

if serialReceiver.isOpen():
    consolePrint("Serial Open", Priority.EVENT)
else:
    consolePrint("Serial Closed", Priority.EVENT)

'''

startReceiver()
sleep(0.5)

if serialReceiver.isOpen():
    while 1:
        try:
            x = (serialReceiver.read()).decode("utf-8")
            manageDevice(x)
        except UnicodeDecodeError as ude:
            # maybe we entered here because of wrong message relay and not a baud mismatch
            try:
                consolePrint("Corrupt byte(s) received",Priority.ERROR)
                serialReceiver =  serial.Serial(PORT, BAUDRATE)
                x = (serialReceiver.read()).decode("utf-8")
            except UnicodeDecodeError as ude:
                # this is a baud mismatch
                # ude won't be fixed until port is closed and then opened again
                consolePrint("Fatal UDError encountered", Priority.ERROR)
                serialReceiver.close()
                startReceiver()
        except Exception as e:
            # something might have happened
            consolePrint("Serial Disturbed", Priority.ERROR)
            sleep(0.5)
            # try a quick fix of switching ports
            try:
                quickScan()
                PORT = PORT_LIST[0]
                serialReceiver =  serial.Serial(PORT, BAUDRATE)
                consolePrint("Monitoring Serial", Priority.EVENT, GREEN)
                x = (serialReceiver.read()).decode("utf-8")
            except Exception as e:
                consolePrint("Attempting Port Transfer..." + PORT, Priority.EVENT)
                restartReceiver();