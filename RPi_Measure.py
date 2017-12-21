#!/usr/bin/python

# Libraries to Include
from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
import datetime
import time
import math


# ----------------------------------------------------
# Global Variables
# ----------------------------------------------------
# Measurement Reading Parameters
number_of_channels = 2
sleep_duration_sec = 4
file_to_save_data = '/home/pi/Desktop/RPi_Proj/Readings/ADC_Data.txt'

# PT-100 Sensor Coefficients
pt100_alpha = 3.90766 * 0.001
pt100_beta = 5.76568 * 0.0000001
pt100_rNot = 100
pt100_offset = 0.0

# Initiating I2C Comm with ADC
i2c_helper = ABEHelpers()
bus = i2c_helper.get_smbus()
adc = ADCPi(bus, 0x68, 0x69, 18)


# ----------------------------------------------------
# Function to read from the ADC Channels
# ----------------------------------------------------
def read_from_adc():

    # Creating an Array of Volt and Temperature of Size Number of Channels
    measured_volt = [0 for i in range(number_of_channels + 1)]
    measured_temp = [0 for i in range(number_of_channels + 1)]

    text_to_write = ""
    for each_channel in range(1, number_of_channels + 1):

        # Read Voltage from each channel
        measured_volt[each_channel] = adc.read_voltage(each_channel)

        # Convert Voltage to Temperature
        # text_to_write = convert_to_temperature(measured_volt, measured_temp, each_channel, text_to_write)

        # Channel 1 is supplied Vcc so that exact Vcc is also measured
        if each_channel is 1:
            print "Channel", each_channel, " -> V Reference :", measured_volt[each_channel]
            text_to_write = text_to_write + str(measured_volt[each_channel]) + ","

        # Convert Measured Voltage to Temperature
        else:
            try:
                #
                Rt_measured = ((measured_volt[1] - measured_volt[each_channel]) * 92) / measured_volt[each_channel]
                measured_temp[each_channel] = (Rt_measured - pt100_rNot) / (pt100_alpha * pt100_rNot)

                # measured_temp[each_channel] = (measured_volt[1] - (2 * measured_volt[each_channel])) \
                #                             / (measured_volt[each_channel] * pt100_alpha)

                # Remove the Offset from measurement
                # measured_temp[each_channel] = remove_offset(measured_temp[each_channel])
                print "Channel", each_channel, ":", measured_volt[each_channel], ":", measured_temp[each_channel]

            except ZeroDivisionError:
                measured_temp[each_channel] = "Not Connected."
                print "Channel", each_channel, ":", measured_temp[each_channel]

            # [Date, Time, Vcc Ch1, Temperature Ch2, .... , Temperature Ch_N ]
            text_to_write = text_to_write + str(measured_temp[each_channel]) + ","

    return text_to_write


# ----------------------------------------------------
# Function to convert ADC Voltage to Temperature
# ----------------------------------------------------
def convert_to_temperature(measured_volt, measured_temp, each_channel, text_to_write):

    # Channel 1 is supplied Vcc so that exact Vcc is also measured
    if each_channel is 1:
        print "Channel", each_channel, " -> V Reference :", measured_volt[each_channel]
        text_to_write = text_to_write + str(measured_volt[each_channel]) + ","

    # Convert Measured Voltage to Temperature
    else:
        try:
            #
            Rt_measured = ((measured_volt[1] - measured_volt[each_channel]) * 92) / measured_volt[each_channel]
            measured_temp[each_channel] = (Rt_measured - pt100_rNot ) / (pt100_alpha * pt100_rNot)

            # measured_temp[each_channel] = (measured_volt[1] - (2 * measured_volt[each_channel])) \
            #                             / (measured_volt[each_channel] * pt100_alpha)

            # Remove the Offset from measurement
            # measured_temp[each_channel] = remove_offset(measured_temp[each_channel])
            print "Channel", each_channel, ":", measured_volt[each_channel], ":", measured_temp[each_channel]

        except ZeroDivisionError:
            measured_temp[each_channel] = "Not Connected."
            print "Channel", each_channel, ":", measured_temp[each_channel]

        # [Date, Time, Vcc Ch1, Temperature Ch2, .... , Temperature Ch_N ]
        text_to_write = text_to_write + str(measured_temp[each_channel]) + ","

    return text_to_write


# ----------------------------------------------------
# Function to deduct the offset from Measured Temperature
# ----------------------------------------------------
def remove_offset(temp_value):

    temp_value -= pt100_offset
    return temp_value


# ----------------------------------------------------
# Function to write the measured readings to a File
# ----------------------------------------------------
def write_to_file(text_to_save):
    curr_time = datetime.datetime.now().strftime("%Y_%m_%d,%H:%M:%S")
    try:
        f = open(file_to_save_data, 'a')
        f.write(str(curr_time) + "," + text_to_save)
        f.close()

    except IOError:
        print "Unable to Open Data File!"
    print curr_time, '\n'



# ----------------------------------------------------
# Main Function
# ----------------------------------------------------
if __name__ == "__main__":

    # Infinite Loop for Continuous Operation
    while True:

        # Read data from the ADC Channels
        text_to_write_file = read_from_adc()

        # Save the measured data to a file
        write_to_file(text_to_write_file + '\n')

        # Sleep until wait duration passes.
        time.sleep(sleep_duration_sec)
