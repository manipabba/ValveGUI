import serial
import time
'''
arduino = serial.Serial('COM4',9600)
time.sleep(2)

while True:
    user = input()
    if(user == 'a'):
        arduino.write(b'a')
    if(user == 'b'):
        arduino.write(b'b')
'''
'''
ard = serial.Serial(port,9600,timeout=5)
time.sleep(2) # wait for Arduino

i = 0

while (i < 4):
    # Serial write section

    setTempCar1 = 63
    setTempCar2 = 37
    ard.flush()
    setTemp1 = str(setTempCar1)
    setTemp2 = str(setTempCar2)
    print ("Python value sent: ")
    print (setTemp1)
    ard.write(setTemp1)
    time.sleep(1) # I shortened this to match the new value in your Arduino code

    # Serial read section
    msg = ard.read(ard.inWaiting()) # read all characters in buffer
    print ("Message from arduino: ")
    print (msg)
    i = i + 1
else:
    print "Exiting"
exit()
'''
ser = serial.Serial('COM4',baudrate = 9600, timeout = 1)
def getValues(val):
    ser.write(val)
    data = ser.readline().decode('ascii')
    return data

while(1):
    inputU = input()
    if(inputU == 'o'):
        print(getValues(b'o'))
    if(inputU == 'q'):
        print(getValues(b'q'))

    
