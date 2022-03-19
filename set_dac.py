from g29_brake_test import open_serial, serial_list, make_dac_cmd
import sys

def main():

    if len(sys.argv) < 2:
        print('no value specified')
        return

    arduino = 'Arduino LilyPad USB'
    serial = open_serial(arduino)
    if not serial:
        print('{arduino} not found')
        serial_list()
        return

    print(f'found {arduino} on serial port {serial.name}')

    dac_value = int(sys.argv[1], 10)
    print(f'setting dac value to: {dac_value}')

    serial.write(make_dac_cmd(dac_value))


if __name__ == "__main__":
    main()