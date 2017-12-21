#!/usr/bin/python

# Libraries to Include
import os
import os.path
import time
import paramiko
import datetime
from time import mktime
#from datetime import datetime
from multiprocessing import Process
import threading

import matplotlib
from matplotlib import dates
import matplotlib.pyplot as plt


# ----------------------------------------------------
# Global Variables
# ----------------------------------------------------
# Raspberry Pi Access Information
r_pi_ip = "192.168.100.150"
r_pi_user = "pi"
r_pi_pass = "raspberry"

sleep_interval = 10

# Data File access information
path_remote_data = "/home/pi/Desktop/RPi_Proj/Readings/"
file_remote_data = path_remote_data + "ADC_Data.txt"
path_local_data = ""
file_local_data = ""
file_compiled_data = ""


# ----------------------------------------------------
# Function to create Local Paths
# ----------------------------------------------------
def create_paths():
    global path_local_data, file_local_data, file_compiled_data
    global path_remote_data, file_remote_data

    path_local_data = str(os.getcwd()) + "\\Readings\\"
    if not os.path.exists(path_local_data):
        os.makedirs(path_local_data)

    time_str = time.strftime("%Y%m%d_%H%M%S")
    file_local_data = path_local_data + "ADC_Data_" + time_str + ".txt"
    file_compiled_data = path_local_data + "ADC_Compiled_Data.csv"

    print "Readings Local Path:", file_local_data
    print "Readings Remote Path on R-Pi @", str(r_pi_ip), ":", file_remote_data

    return


# ----------------------------------------------------
# Function to Open a connection with Raspberry Pi
# ----------------------------------------------------
def open_connection(get_data=True):

    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Establish an SSH Connection with Remote Raspberry Pi
        print "Connecting to remote R-Pi..."
        ssh.connect(r_pi_ip, username=r_pi_user, password=r_pi_pass)
        sftp = ssh.open_sftp()

        # Download the File from the Remote Raspberry Pi
        if get_data is True:
            try:
                print "Reading saved ADC data..."
                sftp.get(file_remote_data, file_local_data)

            except IOError:
                os.remove(file_local_data)
                print "No Data Found on Remote R-Pi!!!"

        sftp.close()
        ssh.close()

    except paramiko.SSHException:
        print("\nConnection Error!!!\n")

    return


# ----------------------------------------------------
# Function to compile freshly downloaded data with old data
# ----------------------------------------------------
def compile_data(delete_old_file=False):
    print "Compiling new downloaded data..."

    # Open New data file and previously compiled data file
    try:
        fresh_file = open(file_local_data)
        compiled_file = open(file_compiled_data, "a+")
    except:
        print "Error Opening Files!"
        return

    # Compare both files and add data to 'Compiled Data' file
    fresh_lines = fresh_file.readlines()
    compiled_lines = compiled_file.readlines()
    for each_line in fresh_lines:
        if each_line not in compiled_lines:
            compiled_file.write(each_line)

    # Close file object
    compiled_file.close()
    fresh_file.close()

    if delete_old_file is True:
        os.remove(file_local_data)

    return


# ----------------------------------------------------
# Function to Plot the downloaded data (using 'matplotlob')
# ----------------------------------------------------
def plot_data():
    print "Plotting Data..."

    compiled_file = open(file_compiled_data, "r")
    compiled_lines = compiled_file.readlines()
    data_inst = []
    for each_compiled_line in compiled_lines:
        line = each_compiled_line.split("\n")

        if line[0] != "":
            line_s = line[0].split(",")
            line_s[0] = datetime.datetime.strptime(line_s[0]+','+line_s[1], "%Y_%m_%d,%H:%M:%S")
            data_inst.append(line_s)

    data_inst = zip(*data_inst)

    plt.figure(figsize=(12, 14))
    ax = plt.subplot(111)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.ylim(0, 100)
    plt.yticks(range(0, 100, 10), [str(x) + "Celsius" for x in range(0, 91, 10)], fontsize=14)
    plt.xticks(fontsize=13)

    data_inst[1] = matplotlib.dates.date2num( data_inst[0])
    plt.plot_date( data_inst[1], data_inst[3], '-r')
    plt.draw()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter( matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.show()

    return


# ----------------------------------------------------
# Function to Wait for mentioned time
# ----------------------------------------------------
def wait_for_next(sleep_int):

    print "Process Successful!"
    print datetime.datetime.now().strftime("%Y_%m_%d, %H:%M:%S"), \
        ". In idle mode for next", str(sleep_int), "Seconds..."
    time.sleep(sleep_int)
    return


# ----------------------------------------------------
# Main Function
# ----------------------------------------------------
if __name__ == "__main__":

    print "Initiated Program."
    while True:
        print "\nChecking for Data..."
        create_paths()
        open_connection(get_data=True)
        compile_data(delete_old_file=True)
        #p = Process(target=plot_data())
        #t1= threading.Thread(plot_data())
        #t1.start()
        plot_data()
        wait_for_next(sleep_interval)
        #p.terminate()


