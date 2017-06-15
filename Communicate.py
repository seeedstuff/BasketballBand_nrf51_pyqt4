import serial
import sys
from time import sleep

class Communicate:                        
    def __init__(self, bus):
        self.bus = bus
        self.DEBUG = True

        self.targetBoard = -1  # target board being tested, 1 - WeBuzz Wristband , 2 - WeBuzz Ball
        self.event_begin = 0
        self.event_discharge = 1
        self.event_charging = 2
        self.event_data_streaming = 3
        self.event_failCharge = 4
        self.event_doneCharge = 5
        self.event_getMac = 6
        self.event_getUID = 7
        self.event_flash_test_fail = 8
        self.event_flash_test_pass = 9
        self.event = -1

        self.acc = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.mac = ''
        self.uid = ''

    def listen(self):
        try:
            # self.bus.flush()
            line = self.bus.readline()
            if self.DEBUG:
                print line

            if "acc" in line:
                self.event = self.event_data_streaming
                self.update_acc_gyro_data(line)
            # elif 'WeBuzz Wristband' in line:
            elif 'WeBuzz Wristband' in line:
                self.targetBoard = 1
                self.event = self.event_begin 
            elif 'WeBuzz Ball' in line:
                self.targetBoard = 2
                self.event = self.event_begin                
            # elif "recharge:0" in line:
            #     self.event = self.event_failCharge
            # elif "recharge:1" in line:
            #     self.event = self.event_doneCharge           
            # elif "charge:0" in line:
            #     self.event = self.event_discharge            
            # elif "charge:1" in line:
            #     self.event = self.event_charging
            elif "MAC" in line:
                self.event = self.event_getMac
                self.update_mac_addr(line)
            elif "UID" in line:
                self.event = self.event_getUID
                self.update_uid(line)
            elif "flash:0" in line:
                self.event = self.event_flash_test_fail
            elif "flash:1" in line:
                self.event = self.event_flash_test_pass
        except IOError as e:
            print(e)
            sys.exit(1)


            # self.bus.close()



    def disable_charge(self):
        try:
            # self.bus.flush()
            self.bus.write('charge_0\r\n')
            sleep(.5)
            self.bus.write('charge_0\r\n')
            sleep(.5)
            self.bus.write('charge_0\r\n')
            sleep(.5)
            self.bus.write('charge_0\r\n')
            sleep(.5)
            self.bus.flush()
            if True == self.DEBUG:
                print 'Disabled charge!'
        except Exception as ex:
            print(ex)

    def enable_charge(self):
        # self.bus.flush()
        try:    
            self.bus.flush()
            self.bus.write('charge_1\r\n')
            sleep(.5)
            self.bus.write('charge_1\r\n')
            sleep(.5)
            self.bus.write('charge_1\r\n')
            sleep(.5)
            self.bus.write('charge_1\r\n')
            sleep(.5)
            self.bus.flush()
            if True == self.DEBUG:
                print 'Enabled charge!'
        except Exception as ex:
            print(ex)


    def get_charge_state(self):
        ret = -1
        line = self.bus.readline()
        
        if True == self.DEBUG:
            print line

        if 'charge:0' in line:
            ret = 0
        if 'charge:1' in line:
            ret = 1
        return ret

    def get_flash_test_result(self):
        ret = -1
        line = self.bus.readline()
        if 'flash:1' in line:
            ret = 1
        else:
            ret = 0
        return ret

    def update_acc_gyro_data(self, str):
        try:
            acc_gryo = str.replace('\r\n', '').split(',')
            self.acc = acc_gryo[0].split(':')[1].split(' ')
            self.gyro = acc_gryo[1].split(':')[1].split(' ')
        except Exception as e:
            print e


    def update_mac_addr(self, str):
        # self.mac =  str.replace('\r\n', '').replace(',', '').split(': ')[1]
        self.mac = str

    def update_uid(self, str):
        #  self.uid = str.replace('\r\n', '').replace(',', '').split(': ')[1]
        self.uid = str

    def close(self):
        self.bus.close()
        print('Close serialport.')

    def open(self):
        self.bus.open()

    def __del__(self):
        self.bus.close()

if __name__ == "__main__":
    ser = serial.Serial("COM6", baudrate = 115200)
    com = Communicate(ser)
    com.DEBUG = True
    com.disable_charge()
    while True:
        try:
            '''
            # sys.stdout.write(ser.read())
            com.enable_charge()
            sleep(2)
            com.disable_charge()
            sleep(2)
            
            
            if 0 == com.get_charge_state():
                com.enable_charge()
                if 1 == com.get_charge_state():
                    print 'Charging now!'
                else:
                    print 'Charge Failed!'
                del ser
                exit(0)
            '''
            com.listen()
            if com.event == com.event_data_streaming:
                print com.acc
        except (KeyboardInterrupt, SystemExit):        
            del com
            exit(0)


    