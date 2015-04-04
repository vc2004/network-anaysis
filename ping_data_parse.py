# -*- coding: utf-8 -*-
#
# Author:   Liang Dong
# Email:    vc2004@gmail.com
# Date:     2015-03-23
#

"""
This script parse ping output and subtract seq and RTT in csv format
for further processing.

Example:

ping 8.8.8.8 > ping_data
python ping_data_parse.py ping_data ping_csv

"""

import os
import sys
import re
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def get_time(time_string):
    """This function read the RTT time from the string

    :param time_string: The string contains the time
    :return time: return the RTT time:
    """
    time_equal = 'time='

    time = None
    if time_equal in time_string:
        time = re.search('time=(.+?) ms', time_string).group(1)

    return time

def get_seq(seq_string):
    """This function read the seq from the string

    :param seq_string: The string contains the seq
    :return seq: return the seq:
    """
    time_equal = 'time='

    seq = None
    if time_equal in seq_string:
        seq = re.search('req=(.+?) ttl', seq_string).group(1)

    return seq

def generate_csv(ping_path, csv_path):
    """This function read the data in the ping data and generate the
       csv format output file

    :param file_path: The ping data input
    :param csv_path: The csv data output
    """
    time_equal = 'time='
    comma = ','

    try:
        with open(ping_path, 'r') as inputfile:
            file_content = inputfile.readlines()
    except IOError:
        LOGGER.critical('input file does not exist')
        sys.exit(1)

    time = [get_seq(line) + comma + get_time(line) + '\r\n' \
            for line in file_content if time_equal in line]

    # insert row names
    time.insert(0,'seq,rtt\r\n')

    with open(csv_path, 'w') as outputfile:
        outputfile.writelines(time)

    inputfile.closed
    outputfile.closed

if __name__ == '__main__':
    generate_csv(sys.argv[1], sys.argv[2])
