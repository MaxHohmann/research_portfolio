# ---------------------------------------------------------
#   MMBTS
# ---------------------------------------------------------
"""
This module provides code for using the MMBT-S Trigger Box 
(NEUROSPEC) to send trigger to EEG systems.

The class supports:
- opening serial connection to the trigger box
- sending digital event triggers
- closing serial connection to the trigger box
- listing available serial ports for setup

Debugging mode:
In debugging mode no port is openend or closed and no triggers
are send. Trigger values are still validated, so experiment 
scripts can be run without actual connection to hardware while
trigger errors are still caught.


Version:    1.1.4
Date:       09/11/2026  
Author:     Maximilian Hohmann
            maximilian.hohmann@stud.uni-goettingen.de
            https://github.com/MaxHohmann
"""



# ----- SETUP ---------------------------------------------

import serial
import serial.tools.list_ports



# ----- MMBT-S Module -------------------------------------

class MMBTS:

    # -----------------------------------------------------
    # INITIALIZE
    # -----------------------------------------------------
    def __init__(self):

        # initiate with placeholders
        self.ser        = None
        self.debugging  = False

        print(f"MMBT-S: assigned object ({self})")



    # -----------------------------------------------------
    # OPEN PORT
    # -----------------------------------------------------
    def open_port(self, port=None, debugging=False):
        """
        # set mode for all subsequent calls:
        # debugging = True  : no port connection
        # debugging = False : connect to serial port
        """
        
        self.debugging = debugging


        if self.debugging:

            # no real connection
            self.ser = None

            print(f"MMBT-S: [debugging] simulate opened port!")
            return


        # check port input
        if port is None or port == "":
            raise ValueError("no port defined!")


        # open port
        try:
            # default settings
            self.ser = serial.Serial(
                port            = port,                 # device path
                baudrate        = 9600,
                bytesize        = serial.EIGHTBITS,
                parity          = serial.PARITY_NONE,
                stopbits        = serial.STOPBITS_ONE,
                timeout         = 0.5,
                write_timeout   = 0.5,
                xonxoff         = False,
                rtscts          = False,
                dsrdtr          = False
            )
            
            self.ser.setDTR(True)
            self.ser.setRTS(False)

            # timeout values are only set to limit how long read/write operations
            # can block the application in case of serial port issues (e.g. USB 
            # diconnetcion or COM port failure).


            print(f"MMBT-S: opened port ({port})")

   
        except serial.SerialException:
            raise ValueError(f"Could not open port ({port})!") from None



    # -----------------------------------------------------
    # VALIDATE TRIGGER
    # -----------------------------------------------------
    @staticmethod
    def _validate_trigger(value=None):
 
        # check trigger value
        if value is None:
            raise ValueError("no trigger value defined!")
 
        # check trigger format
        if not isinstance(value, int):
            raise TypeError(f"trigger value must be integer ({type(value)})")
 
        # only accept triggers within range (0 to 255)
        if not (0 <= value <= 255):
            raise ValueError(f"trigger value out of range ({value})!")
 
        return value



    # -----------------------------------------------------
    # SEND TRIGGER
    # -----------------------------------------------------
    def send_trigger(self, value=None):

        if self.debugging:

            # validate trigger values
            value = self._validate_trigger(value)

            # continue without hardware
            print(f"MMBT-S: [debugging] simulate sent trigger! ({value})")
            return
        

        # send trigger
        try:
            self.ser.write(bytes([value]))

        except (serial.SerialException, AttributeError, TypeError):
            raise ConnectionError(f"could not send trigger! ({value})!") from None   



    # -----------------------------------------------------
    # CLOSE PORT
    # -----------------------------------------------------
    def close_port(self):

        if self.debugging:

            # no port to close
            self.ser = None

            print("MMBT-S: [debugging] simulate closed port!")
            return
        

        # check for opened port
        if self.ser is None or not self.ser.is_open:
            raise ConnectionError("no open port found!")


        port = self.ser.port


        # close port
        try:            
            self.ser.close()

            print(f"MMBT-S: closed port ({port})")

        except serial.SerialException:
            raise ValueError(f"could not close port ({port})!") from None



    # -----------------------------------------------------
    # SHOW AVAILABLE PORTS
    # -----------------------------------------------------
    @staticmethod
    def show_ports():
        """
        Print device names od all available serial ports.
        """

        ports = serial.tools.list_ports.comports()

        print("MMBT-S: list of available ports")
        for p in ports:
            print(f"\t- {p.device}:\t{p.description}")

        return

    