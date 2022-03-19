import serial
from serial.tools import list_ports
import io
from time import time
import sys
import hid


def make_dac_cmd(value):
    mode = int('01000000', 2) # Sets the control byte (010-Sets in Write mode)
    msb = (value >> 4) & 0xff # get the 8 most significant bits
    lsb = (value << 4) & 0xff # get the 4 lest significant bits

    return(bytes([ mode, msb, lsb ]))


def get_report_value(report, start, bytes, signed=False):
    b = report[start:start + bytes]
    #print(f'get_report_value {b}')
    return int.from_bytes(b, byteorder='little', signed=signed)

def monitor(port, g29):

    ser = serial.Serial(
        port=port, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
    )

    start_time = time()
    current_time = start_time
    period = 3

    # G29 
    # 43 bytes before the wheel
    WHEEL_AXIS = 43
    GAS_PEDAL = WHEEL_AXIS + 2
    BRAKE_PEDAL = GAS_PEDAL + 2
    CLUTCH_PEDAL = BRAKE_PEDAL + 2

    dac_value = 0

    while 1:
        # check if there is data in the serial buffer to be displayed
        if ser.in_waiting > 0:
            b = ser.read(ser.in_waiting)
            sys.stdout.write(b.decode('Ascii'))

        report = g29.read(64)
        if report:

            wheel = get_report_value(report, WHEEL_AXIS, 2)
            gas = get_report_value(report, GAS_PEDAL, 2)
            brake = get_report_value(report, BRAKE_PEDAL, 2)
            clutch = get_report_value(report, CLUTCH_PEDAL, 2)

            #print(f'report len: {len(report)}')
            #print(report)
            print(f'dac_value: {dac_value}, wheel: {wheel}, gas: {gas}, brake: {brake}, clutch: {clutch}')

        # check if we need to update the dac value
        current_time = time()
        if(current_time - start_time > period):
            ser.write(make_dac_cmd(dac_value))
            start_time = current_time
            dac_value += 1

def serial_list():
    ports = list_ports.comports()

    print('Serial Ports')

    for port in ports:
        print(port)

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