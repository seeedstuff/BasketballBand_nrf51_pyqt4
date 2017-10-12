# -*- coding: utf-8 -*-
"""
Test programmatically setting log transformation modes.
"""

# import win32api
import sys, os, datetime, time
import numpy as np
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.dockarea import *
import pyqtgraph as pg
import numpy as np
from Communicate import *
from serial_tools import *
import subprocess
import threading
# from nrf51_flashtool import *



class MainWindow:
    def __init__(self):
        self.com = None
        self.port = None
        self.code = None
        #  This paramater indecate which board to test
        self.targetBoard = -1           

        # test result
        self.upload_thread_run_once = False
        self.upload_state = 0  # -1 - fail, 0 - default, 1 - ok
        self.isCharge_ok = False
        self.isFlash_ok = False
        self.isComOpend = False                

        # QtGui
        self.app = QtGui.QApplication([])
        self.win = QtGui.QMainWindow()                
        self.com_ports = QtGui.QComboBox()
        # self.win_drive = QtGui.QComboBox()
        self.log_box = QtGui.QPlainTextEdit()
        self.btn_start = QtGui.QPushButton("Start/stop")
        # self.btn_stop = QtGui.QPushButton("Stop")
        self.btn1 = QtGui.QPushButton("Wristband FW")
        self.btn2 = QtGui.QPushButton("ball FW")
        self.btn_start.setFixedHeight(30)
        # self.btn_stop.setFixedHeight(30)
        self.btn1.setFixedHeight(30)
        self.btn2.setFixedHeight(30)

        ports = get_ports("mbed")
        for port in ports:
            self.com_ports.addItem(port)

        # drives_ = []
        # drives = win32api.GetLogicalDriveStrings()
        # drives = drives.split('\000')[:-1]        
        '''
        mbed_drive = None
        for drive in drives:
            name = win32api.GetVolumeInformation(drive)[0]
            if 'MBED' in name:
                print "Get mbed drive!"
                mbed_drive = drive
            else:
                drives_.append(drive)
        if drives_ != None:
            drives_ = [mbed_drive] + drives_        
        for drive in drives_:
            self.win_drive.addItem(drive)
        '''
        # for drive in drives:
        #     self.win_drive.addItem(drive)

        self.dock1 = Dock("Test Log", size=(500, 400))
        self.dock2 = Dock("", size=(500, 400))
        self.dock3 = Dock("", size=(500, 400))
        self.dock4 = Dock("", size=(10,1))
        # self.dock5 = Dock("", size=(10,1))

        self.area = DockArea()
        self.area.addDock(self.dock1, 'left')
        self.area.addDock(self.dock2, 'right')
        self.area.addDock(self.dock3, 'right', self.dock2)
        self.area.addDock(self.dock4, 'bottom', self.dock1)
        # self.area.addDock(self.dock5, 'bottom', self.dock1)

        self.plot1 = pg.PlotWidget(title="Accel_x")
        self.plot2 = pg.PlotWidget(title="Accel_y")
        self.plot3 = pg.PlotWidget(title="Accel_z")
        self.plot4 = pg.PlotWidget(title="Gyro_x")
        self.plot5 = pg.PlotWidget(title="Gyro_y")
        self.plot6 = pg.PlotWidget(title="Gyro_z")
        self.curve1 = self.plot1.plot()
        self.curve2 = self.plot2.plot()
        self.curve3 = self.plot3.plot()
        self.curve4 = self.plot4.plot()
        self.curve5 = self.plot5.plot()
        self.curve6 = self.plot6.plot()

        self.dock1.addWidget(self.com_ports)
        self.dock1.addWidget(self.btn_start)
        # self.dock1.addWidget(self.btn_stop)
        self.dock1.addWidget(self.log_box)
        self.dock2.addWidget(self.plot1)
        self.dock2.addWidget(self.plot2)
        self.dock2.addWidget(self.plot3)
        self.dock3.addWidget(self.plot4)
        self.dock3.addWidget(self.plot5)
        self.dock3.addWidget(self.plot6)
        # self.dock4.addWidget(self.win_drive)
        self.dock4.addWidget(self.btn1)
        self.dock4.addWidget(self.btn2)

        self.data1 = [0]
        self.data2 = [0]
        self.data3 = [0]
        self.data4 = [0]
        self.data5 = [0]
        self.data6 = [0]

        self.win.setCentralWidget(self.area)
        self.win.resize(1000,500)
        self.win.setWindowTitle('WristBand: Manufacture Test')
        self.btn_start.clicked.connect(self.com_prot_init)
        # self.btn_stop.clicked.connect(self.close_com_port)
        self.btn1.clicked.connect(self.upload_fw_wristband)
        self.btn2.clicked.connect(self.upload_fw_ball)

        y = np.random.normal(size=1000)
        x = np.linspace(0, 1, 1000)
        self.plot1.plot(x, y)
        self.plot2.plot(x, y)
        self.plot3.plot(x, y)
        self.plot4.plot(x, y)
        self.plot5.plot(x, y)
        self.plot6.plot(x, y)

    def resetState(self):
        self.clear_log()
        self.isCharge_ok = False
        self.isFlash_ok = False
        self.isComOpend = False
        
    def resume_serve(self):
        if self.com:            
            self.com.close()
            self.resetState()

    def start_serve(self):
        self.com_prot_init()

    def com_prot_init(self):        
        self.resetState()
        self.clear_log() 
        if self.com == None:
            self.add_log("")
            self.add_log("")
            self.add_log("")
            self.add_log("")
            self.add_log("")
            self.add_log("")
            self.add_log(" ____    _____      _      ____    _____ ")
            self.add_log("/ ___|  |_   _|    / \    |  _ \  |_   _|")
            self.add_log("\___ \    | |     / _ \   | |_) |   | |  ")
            self.add_log(" ___) |   | |    / ___ \  |  _ <    | |  ")
            self.add_log("|____/    |_|   /_/   \_\ |_| \_\   |_|  ")
      
            port = str(self.com_ports.currentText())
            print "Serial init!"            
            try: 
                ser = serial.Serial(port, baudrate = 115200)
                self.isComOpend = True
                self.com = Communicate(ser)
                self.com.open()
                print("Open Serial port!")
            except Exception as ex:
                print ex
                return None
        else:
            # print "COM port instanced!" 
            if self.com.bus.is_open:
                self.com.close()
                self.isComOpend = False
                self.add_log(" ____    _____    ___    ____  ")
                self.add_log("/ ___|  |_   _|  / _ \  |  _ \ ")
                self.add_log("\___ \    | |   | | | | | |_) |")
                self.add_log(" ___) |   | |   | |_| | |  __/ ")
                self.add_log("|____/    |_|    \___/  |_|    ")              
                print("Close Serial port!")
            else:
                try:                   
                    self.add_log("")
                    self.add_log("")
                    self.add_log("")
                    self.add_log("")
                    self.add_log("")
                    self.add_log("")
                    self.add_log(" ____    _____      _      ____    _____ ")
                    self.add_log("/ ___|  |_   _|    / \    |  _ \  |_   _|")
                    self.add_log("\___ \    | |     / _ \   | |_) |   | |  ")
                    self.add_log(" ___) |   | |    / ___ \  |  _ <    | |  ")
                    self.add_log("|____/    |_|   /_/   \_\ |_| \_\   |_|  ")
                    self.com.open()
                    self.isComOpend = True
                    print("Open Serial!")
                except Exception as ex:
                    print(ex)
                    self.isComOpend = False
                    self.add_log("")
                    self.add_log("")
                    self.add_log("")
                    self.add_log("")
                    self.add_log("")
                    self.add_log("")
                    self.add_log(" _____   ____    ____     ___    ____  ")
                    self.add_log("| ____| |  _ \  |  _ \   / _ \  |  _ \ ")
                    self.add_log("|  _|   | |_) | | |_) | | | | | | |_) |")
                    self.add_log("| |___  |  _ <  |  _ <  | |_| | |  _ < ")
                    self.add_log("|_____| |_| \_\ |_| \_\  \___/  |_| \_\.")
                    self.add_log("")
                    self.add_log("")
                    print("Open Serial failed!")
        

    def close_com_port(self):
        if self.com:
            if self.com.bus.is_open:                
                self.resetState()
                self.com.close()

    def add_log(self, str):
        #self.log_box.appendPlainText('[' + datetime.datetime.now().strftime("%H:%M:%S") + "] " + str)
        self.log_box.appendPlainText(str)

    def clear_log(self):
        self.log_box.clear()

    # Thread of uploading firmware by pyocd-flashtool
    def T_upload(self, hexFilePath):
        # pyocd-flashtool
        errOut = os.popen("pyocd-flashtool -t nrf51 " + hexFilePath).read()        
        if "100%" in errOut:
            self.upload_state = 1
        else:
            self.upload_state = -1        
        # If upload OK, than begin test part
        self.upload_thread_run_once = True

        # pyOCD api
        # ret = SBK_Test_Flash(hexFilePath)
        # if 1 == ret:
        #     self.upload_state = 1
        # else:
        #     self.upload_state = -1        
        # # If upload OK, than begin test part
        # self.upload_thread_run_once = True

        
    # Upload factory firmware, this produce part will be done with mobile phone OTA
    def upload_fw_wristband(self):
        if self.com != None:
            if self.com.bus.is_open:
                self.com.close()
        self.clear_log()
        self.add_log(" _   _   ____    _        ___       _      ____  ")
        self.add_log("| | | | |  _ \  | |      / _ \     / \    |  _ \ ")
        self.add_log("| | | | | |_) | | |     | | | |   / _ \   | | | |")
        self.add_log("| |_| | |  __/  | |___  | |_| |  / ___ \  | |_| |")
        self.add_log(" \___/  |_|     |_____|  \___/  /_/   \_\ |____/ ")        
        self.add_log("__        __  _____           _   _               ")
        self.add_log("\ \      / / |_   _|         | | | |   ___  __  __")
        self.add_log(" \ \ /\ / /    | |           | |_| |  / _ \ \ \/ /")
        self.add_log("  \ V  V /     | |           |  _  | |  __/  >  < ")
        self.add_log("   \_/\_/      |_|    _____  |_| |_|  \___| /_/\_\.")
        self.add_log("                     |_____|                      ")              
        path = "hex/wristband.hex"           
        t = threading.Thread(target=self.T_upload, args=(path,))
        t.start()

    # Upload firmware for test
    def upload_fw_ball(self):         
        if self.com != None:
            if self.com.bus.is_open:
                self.com.close()
        self.clear_log()
        self.add_log(" _   _   ____    _        ___       _      ____  ")
        self.add_log("| | | | |  _ \  | |      / _ \     / \    |  _ \ ")
        self.add_log("| | | | | |_) | | |     | | | |   / _ \   | | | |")
        self.add_log("| |_| | |  __/  | |___  | |_| |  / ___ \  | |_| |")
        self.add_log(" \___/  |_|     |_____|  \___/  /_/   \_\ |____/ ") 
        self.add_log("  ____            _   _           _   _               ")
        self.add_log(" | __ )    __ _  | | | |         | | | |   ___  __  __")
        self.add_log(" |  _ \   / _` | | | | |         | |_| |  / _ \ \ \/ /")
        self.add_log(" | |_) | | (_| | | | | |         |  _  | |  __/  >  < ")
        self.add_log(" |____/   \__,_| |_| |_|  _____  |_| |_|  \___| /_/\_\.")
        self.add_log("                         |_____|                      ")   
        path = 'hex/ball.hex'
        t = threading.Thread(target=self.T_upload, args=(path,))
        t.start()
        


    def report_error(self, error):
        self.add_log("")
        self.add_log("")
        self.add_log("")
        self.add_log("")
        self.add_log("")
        self.add_log("#######  ######   ######   #######  ######")
        self.add_log("#        #     #  #     #  #     #  #     #")
        self.add_log("#        #     #  #     #  #     #  #     #")
        self.add_log("#####    ######   ######   #     #  ######")
        self.add_log("#        #   #    #   #    #     #  #   #")
        self.add_log("#        #    #   #    #   #     #  #    #")
        self.add_log("#######  #     #  #     #  #######  #     #")
        self.add_log("")
        self.add_log("")    
        self.add_log(error)   

    def update(self):    
        if self.com != None and self.isComOpend:                     
            self.com.listen()
            if self.com.event == self.com.event_data_streaming:
                test_state = ""
                # if self.isCharge_ok:
                #     test_state += "Charge: OK!\r\n"
                # else:
                #     test_state += "Charge: Failed!\r\n"
                if self.isFlash_ok:
                    test_state += "Flash: OK!\r\n"
                else:
                    test_state += "Flash: Failed!\r\n"

                self.clear_log()
                self.add_log(test_state)
                
                self.data1.append(10*float(self.com.acc[0]))
                self.data2.append(10*float(self.com.acc[1]))
                self.data3.append(10*float(self.com.acc[2]))
                self.data4.append(float(self.com.gyro[0]))
                self.data5.append(float(self.com.gyro[1]))
                self.data6.append(float(self.com.gyro[2]))
                if len(self.data1) > 100:
                    self.data1.pop(0)
                    self.data2.pop(0)
                    self.data3.pop(0)
                    self.data4.pop(0)
                    self.data5.pop(0)
                    self.data6.pop(0)
                self.curve1.setData(np.hstack(self.data1))
                self.curve2.setData(np.hstack(self.data2))
                self.curve3.setData(np.hstack(self.data3))
                self.curve4.setData(np.hstack(self.data4))
                self.curve5.setData(np.hstack(self.data5))
                self.curve6.setData(np.hstack(self.data6))

                # 平摆时 - acc_x = 0, acc_y = 0, acc_z = 10
                # 斜摆时 - acc_x = -6, acc_y = -6, acc_z = 6
                #print self.com.acc[0], self.com.acc[1], self.com.acc[2] 
                # Ball board acc pass state
                    #if self.targetBoard == 1:
                    #    if float(self.com.acc[0]) > -0.7 and \
                    #        float(self.com.acc[0]) < -0.4 and \
                    #        float(self.com.acc[1]) > -0.7 and \
                    #        float(self.com.acc[1]) < -0.4 and \
                    #        float(self.com.acc[2]) > 0.4  and \
                    #        float(self.com.acc[2]) < 0.7:
                    #        accTestResult = True
                    
                # if self.printer_reset == True and self.isCharge_ok == True and self.isFlash_ok == True:                    
                if self.isFlash_ok == True: 
                    accTestResult = False  

                    # Wristband board acc pass state               
                    # if self.targetBoard == 2:
                    #     if float(self.com.acc[0]) > 0.6 and \
                    #         float(self.com.acc[0]) < 0.7 and \
                    #         float(self.com.acc[1]) > 0.5 and \
                    #         float(self.com.acc[1]) < 0.6 and \
                    #         float(self.com.acc[2]) > 0.6  and \
                    #         float(self.com.acc[2]) < 0.7:
                    #         accTestResult = True

                    # # Ball board acc pass state
                    # if self.targetBoard == 1:
                    #     if float(self.com.acc[0]) > 0.4 and \
                    #         float(self.com.acc[0]) < 0.7 and \
                    #         float(self.com.acc[1]) > 0.4 and \
                    #         float(self.com.acc[1]) < 0.7 and \
                    #         float(self.com.acc[2]) > 0.4  and \
                    #         float(self.com.acc[2]) < 0.7:
                    #         accTestResult = True 

                    # V1.0 data comparation set
                    if float(self.com.acc[0]) > 0.4 and \
                        float(self.com.acc[0]) < 0.7 and \
                        float(self.com.acc[1]) > 0.4 and \
                        float(self.com.acc[1]) < 0.7 and \
                        float(self.com.acc[2]) > 0.4  and \
                        float(self.com.acc[2]) < 0.7:
                        accTestResult = True

                    # V2.0 data comparation set
                    # if float(self.com.acc[0]) > -0.7 and \
                    #     float(self.com.acc[0]) < -0.4 and \
                    #     float(self.com.acc[1]) > -0.7 and \
                    #     float(self.com.acc[1]) < -0.4 and \
                    #     float(self.com.acc[2]) > 0.4  and \
                    #     float(self.com.acc[2]) < 0.7:
                    #     accTestResult = True
                    
                    if accTestResult == True:
                        self.clear_log()                                                        
                        self.add_log("")
                        self.add_log("")
                        self.add_log("")
                        self.add_log("")
                        self.add_log("")                        
                        self.add_log("      ######      #      #####    #####")
                        self.add_log("      #     #    # #    #     #  #     #")
                        self.add_log("      #     #   #   #   #        #")
                        self.add_log("      ######   #     #   #####    #####")
                        self.add_log("      #        #######        #        #")
                        self.add_log("      #        #     #  #     #  #     #")
                        self.add_log("      #        #     #   #####    #####") 
                        # Save Mac Address and UID to file
                        self.saveMacAddrUID(self.code)                            
                        self.com.close()
                        self.isComOpend = False



            elif self.com.event == self.com.event_getMac:
                # Mac address will be combined with UID, see condition com.event_getUID
                # self.add_log(self.com.mac)
                pass
                
                  
            elif self.com.event == self.com.event_getUID:
                #self.add_log('   [UID]: ' + self.com.uid)                            
                self.code = self.com.mac + self.com.uid               


            elif self.com.event == self.com.event_flash_test_pass:
                self.isFlash_ok = True
                #self.add_log(" [Flash]: pass!")
                self.clear_log()
                self.add_log("")
                self.add_log("")
                self.add_log("")
                self.add_log("")
                self.add_log("")
                self.add_log("              ###      ")
                self.add_log("             #   #      ")
                self.add_log("                 #      ")
                self.add_log("              ###      ")
                self.add_log("                 #      ")
                self.add_log("             #   #      ")
                self.add_log("              ###      ")

            elif self.com.event == self.com.event_flash_test_fail:
                self.isFlash_ok = False
                #self.add_log(" [Flash]: failed!")
                self.report_error(" [Flash]: failed!")

            elif self.com.event == self.com.event_begin:
                # Default state                
                self.clear_log()
                self.add_log("")
                self.add_log("")
                self.add_log("")
                self.add_log("")
                self.add_log("")
                self.add_log("              ###      ")
                self.add_log("             #   #      ")
                self.add_log("             #   #      ")
                self.add_log("                #      ")
                self.add_log("               #      ")
                self.add_log("              #      ")
                self.add_log("             #####      ")
                self.add_log("")
                self.add_log("")

                # Get detected target board
                self.targetBoard = self.com.targetBoard
                if self.targetBoard == 1:
                    self.add_log("Target board WeBuzz Wristband detected!")
                elif self.targetBoard == 2:
                    self.add_log("Target board WeBuzz Ball detected!")

                # self.com.enable_charge()
                # self.isFlash_ok = False
                # self.isCharge_ok = False
                # self.com.disable_charge()
                #time.sleep(1)                 
                # self.com.listen()
                # if self.com.event == self.com.event_discharge:
                #     self.com.enable_charge()
                #     self.com.listen()
                #     print "com.event: ", self.com.event
                #     if self.com.event == self.com.event_doneCharge:
                #         self.isCharge_ok = True
                #         print('[Charge]: pass!')                        
                #     elif self.com.event ==self.com.event_failCharge:
                #         self.isCharge_ok = False
                #         print("[Charge]: failed!")
                #         self.report_error("[Charge]: failed!") 

                # elif self.com.event == self.com.event_charging:
                #     self.isCharge_ok = False
                #     self.report_error("[Charge]: error!")
        
        if self.upload_thread_run_once == True:
            self.upload_thread_run_once = False            
            if self.upload_state == 1:                
                self.add_log("  ___        _  __    ")
                self.add_log(" / _ \      | |/ /    ")
                self.add_log("| | | |     | ' /     ")
                self.add_log("| |_| |  _  | . \   _ ")
                self.add_log(" \___/  (_) |_|\_\ (_)")
            elif self.upload_state == -1:                
                self.add_log(" _____   ____    ____     ___    ____  ")
                self.add_log("| ____| |  _ \  |  _ \   / _ \  |  _ \ ")
                self.add_log("|  _|   | |_) | | |_) | | | | | | |_) |")
                self.add_log("| |___  |  _ <  |  _ <  | |_| | |  _ < ")
                self.add_log("|_____| |_| \_\ |_| \_\  \___/  |_| \_\.")
            self.upload_state = 0
        
    def saveMacAddrUID(self, content):
        savefile = open('macAddrUID.txt', 'a')
        savefile.write(content)
        savefile.write("\r\n")
        savefile.close()
    
    def show(self):
        self.win.show()
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(50)
        sys.exit(self.app.exec_())
        

    def __del__(self):
        self.resume_serve()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__': 
    main_win = MainWindow()   
    main_win.show()
