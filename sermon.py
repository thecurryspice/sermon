import serial
import subprocess
import sys
from time import sleep
from enum import IntEnum
#import NumPy as np

class Priority(IntEnum):
    SILENT = 5
    ERROR = 4
    SETTING = 3
    EVENT = 2
    GUI = 1
    ALL = 0

PORT = "/dev/ttyACM0"
PortList = []
VerbosePriority = Priority.ERROR

def consolePrint(msg, priority):
    if priority >= VerbosePriority:
        print ("#~# sermonConsole: " + msg + " #~#")

def cmdLine(cmd):
    process = subprocess.Popen(args = cmd, stdout = subprocess.PIPE, universal_newlines = True, shell = True)
    return process.communicate()[0]

def fetchPorts():
    global PortList
    PortList = []
    recBuff = ""
    recBuff = cmdLine("python3 -m serial.tools.list_ports")
    while(recBuff == ""):
        consolePrint("Couldn't find any ports, scanning again after 3 seconds...", Priority.ERROR)
        sleep(3)
        recBuff = cmdLine("python3 -m serial.tools.list_ports")
    port = ""
    for char in recBuff:
        # extract Port Alias
        if(char != " " and char != "\n"):
            port += char
        elif(char == " "):
            continue
        else:
            # skip till end of buffer and store in list
            PortList.append(port)
            port = ""
    print("-----")
    for x in PortList:
        print(x)
    print("-----")

def configurePort():
    global PORT, BAUDRATE, sermon, PortList
    fetchPorts()
    PORT = "/dev/tty" + input("Choose Serial Port to Use:" + str(PortList) + "\n/dev/tty")
    BAUDRATE = input("Input Baud Rate: [19200, 38400, 57600, 115200, 230400]\n")
    try:
        sermon =  serial.Serial(PORT, BAUDRATE)
        sleep(0.5)
        consolePrint("Monitor Running", Priority.EVENT)
    except serial.serialutil.SerialException as e:
        consolePrint("Port Unavailable!", Priority.ERROR)
        configurePort()

def restartSerial():
    global PORT, BAUDRATE, sermon, PortList
    try:
        sermon =  serial.Serial(PORT, BAUDRATE)
        consolePrint("Reconnecting", Priority.EVENT)
        sleep(0.5)
        consolePrint("Monitor Running", Priority.EVENT)
    except serial.serialutil.SerialException as e:
        consolePrint("Port Unavailable!", Priority.ERROR)
        fetchPorts()
        PORT = "/dev/tty" + input("Choose Serial Port to Use:" + str(PortList) + "\n/dev/tty")
        restartSerial()

sermon = serial.Serial()
configurePort()

if sermon.isOpen():
    while 1:
        try:
            linuxdcpp&
            sendRaw = input("")
            x = (sermon.read()).decode("utf-8")
            print (x, end = "")
        except Exception as e:
            consolePrint("Serial Disturbed!", Priority.ERROR)
            sleep(0.25)
            restartSerial();

