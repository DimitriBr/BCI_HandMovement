import serial


arduino = serial.Serial(port = 'COM6', baudrate = 115200, timeout = 0.1)
def send_trig(x):
    x = str(x)
    arduino.write(bytes(x, 'utf-8'))
    core.wait(0.1)
    arduino.write(bytes(str(0), 'utf-8'))

while True:
    for i in range(2):
        time.sleep(0.1)

        send_trig(2)
        time.sleep(0.1)
        send_trig(0)

        print('Y', i+10)