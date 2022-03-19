import serial
from serial.tools import list_ports
import io
from time import time
import sys
import hid


def set_dac_value(ser, value):
    mode = int('01000000', 2) # Sets the control byte (010-Sets in Write mode)
    msb = (value >> 4) & 0xff # get the 8 most significant bits
    lsb = (value << 4) & 0xff # get the 4 lest significant bits

    ser.write(bytes([ mode, msb, lsb ]))


def get_report_value(report, start, bytes, signed=False):
    b = report[start:start + bytes]
    print(f'get_report_value {b}')
    return int.from_bytes(b, byteorder='little', signed=signed)

def monitor(port, g29, debug=False):

    ser = serial.Serial(
        port=port, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
    )
    sio = io.TextIOWrapper(io.BufferedReader(ser))

    serialString = ""  # Used to hold data coming over UART
    start_time = time()
    current_time = time()
    period = 3

    # G29 
    # 43 bytes before the wheel
    WHEEL_AXIS = 43
    GAS_PEDAL = WHEEL_AXIS + 2
    BRAKE_PEDAL = GAS_PEDAL + 2
    CLUTCH_PEDAL = BRAKE_PEDAL + 2

    value = 0

    while 1:
        # Wait until there is data waiting in the serial buffer
        if debug and ser.in_waiting > 0:

            # Read data out of the buffer until a carraige return / new line is found
            serialString = sio.readline()
            #serialString = serialString.decode("Ascii")
            serialString = serialString.rstrip('\r\n')

            # Print the contents of the serial data
            try:
                print(serialString)
            except:
                pass

        report = g29.read(64)
        if report:

            wheel = get_report_value(report, WHEEL_AXIS, 2)
            gas = get_report_value(report, GAS_PEDAL, 2)
            brake = get_report_value(report, BRAKE_PEDAL, 2)
            clutch = get_report_value(report, CLUTCH_PEDAL, 2)

            print(f'report len: {len(report)}')
            print(report)
            print(f'wheel: {wheel}, gas: {gas}, brake: {brake}, clutch: {clutch}')

        current_time = time()
        if(current_time - start_time > period):
            set_dac_value(value)
            start_time = current_time
            value += 1

def serial_list():
    ports = list_ports.comports()

    print('Serial Ports')

    for port in ports:
        print(port)
        if port.description.startswith('Arduino LilyPad USB'):
            print(f'found on {port.name}')

def find_port(description):
    ports = list_ports.comports()
    for port in ports:
        if port.description.startswith(description):
            return port.name

def open_g29():
    try:
        g29 = hid.device()
        g29.open(0x046d, 0xc260)
        g29.set_nonblocking(True)
        return g29
    except:
        pass

def hid_list():
    print('Input devices')
    for device in hid.enumerate():
        print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")
 

def main():
    arduino = 'Arduino LilyPad USB'
    port = find_port(arduino)
    if not port:
        print('{arduino} not found')
        serial_list()
        return

    print(f'found {arduino} on port {port}')

    g29 = open_g29()
    if not g29:
        print('G29 not found')
        hid_list()
        return

    monitor(port, g29)

if __name__ == "__main__":
    main()