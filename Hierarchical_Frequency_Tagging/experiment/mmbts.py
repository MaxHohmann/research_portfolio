"""
This module provides code for communicating with the
MMBT-S Trigger Box (NEUROSPEC).

The class supports:
- Opening serial connection to the trigger box
- Sending digital event markers (triggers)
- Closing serial connection to the trigger box
- Listing available serial ports for setup

adapted from:   Maximilian Hohmann
                https://github.com/MaxHohmann/NeurospecMMBTS

adjusted to match trigger values of the EEG experiment
"""


import serial
import serial.tools.list_ports


class MMBTS:

    def __init__(self):

        self.ser = None  # placeholder

        print(f"MMBT-S\t: Assigned Trigger Box object ({self})")


    # ----------------------
    # OPEN PORT
    # ----------------------
    def open_port(self, port=None):

        # check port input
        if port is None or port == "":
            raise ValueError("No port defined!")
        

        # open port
        try:
            self.ser = serial.Serial(
                port        = port, # change port accordingly
                baudrate    = 9600  # default
            )

            # use MMTB-S default settings
            self.ser.write(bytes([0]))
            self.ser.setRTS(False)
            self.ser.setDTR(False)

            print(f"MMBT-S\t: Opened port ({port})")
   
        except serial.SerialException:
            raise ValueError(f"Could not open port ({port})!") from None
            # you should check port name, and installed drivers

    
    # ----------------------
    # SEND TRIGGER
    # ----------------------
    def send_trigger(self, value=None):

        # commented out for speed
        # ----------------------------------------
        # # check for port object
        # if self.ser is None or not self.ser.is_open:
        #     raise ConnectionError("No opened port found!")
        #
        #
        # # check trigger value 
        # if value is None:
        #     raise ValueError("No trigger value defined!")
        #
        # if not isinstance(value, int):
        #     raise TypeError(f"Trigger value must be integer ({type(value)})")
        #
        # # only accept triggers within range (0 to 255)
        # if not (0 <= value <= 255):
        #     raise ValueError(f"Trigger value out of range ({value})!")
        # ----------------------------------------

        # send trigger
        self.ser.write(bytes([value]))


    # ----------------------
    # CLOSE PORT
    # ----------------------
    def close_port(self):

        # check for port object
        if self.ser is None or not self.ser.is_open:
            raise ConnectionError("No open port found!")
        
        port = getattr(self.ser, "port", None)

        self.ser.write(bytes([0]))
        self.ser.close()

        print(f"MMBT-S\t: Closed port ({port})")


    # ----------------------
    # SHOW AVAILABLE PORTS
    # ----------------------
    @staticmethod
    def show_ports():
        ports = serial.tools.list_ports.comports()

        print("MMBT-S\t: Display list of available ports")

        for p in ports:
            print(p.device, p.description)

