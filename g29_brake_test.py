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

def run_test(serial, g29, start, end, step=10, period=1, debug=False):

    start_time = time()
    current_time = start_time

    # G29 
    # 43 bytes before the wheel
    WHEEL_AXIS = 43
    GAS_PEDAL = WHEEL_AXIS + 2
    BRAKE_PEDAL = GAS_PEDAL + 2
    CLUTCH_PEDAL = BRAKE_PEDAL + 2

    dac_value = start

    while 1:
        # check if there is data in the serial buffer to be displayed
        if debug and serial.in_waiting > 0:
            b = serial.read(serial.in_waiting)
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
            if debug:
                print(f'SET DAC: {dac_value}')
            serial.write(make_dac_cmd(dac_value))
            start_time = current_time
            dac_value += step
            if dac_value > end:
                return # we are done

def serial_list():
    ports = list_ports.comports()

    print('Serial Ports')

    for port in ports:
        print(port)

def open_serial(description):
    ports = list_ports.comports()
    for port in ports:
        if port.description.startswith(description):
            return serial.Serial(
                    port=port.name, 
                    baudrate=115200, 
                    bytesize=8, 
                    timeout=2, 
                    stopbits=serial.STOPBITS_ONE
            )

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
    serial = open_serial(arduino)
    if not serial:
        print('{arduino} not found')
        serial_list()
        return

    print(f'found {arduino} on serial port {serial.name}')

    g29 = open_g29()
    if not g29:
        print('G29 not found')
        hid_list()
        return

    print(f'found {g29.get_manufacturer_string()}, {g29.get_product_string()}')

    # 4096 / 3.3 = 1241 dac/v
    # James logged values between approx 
    # on  1.93 * 1241 = 1836 
    # off 2.93 * 1241 = 3636
    # maybe start with mid-point of 2736 and work outwards
    run_test(serial=serial, g29=g29, start=1836, end=3636, period=0.1, debug=True)

if __name__ == "__main__":
    main()