# -*- coding: utf-8 -*-
#
# Author:   Liang Dong
# Email:    vc2004@gmail.com
# Date:     2015-03-23
#

"""
This script parse ovs stats and subtract timestamp and common stats
 in csv format for further processing.

Example:

1) Collect raw data:

ovsdb-client -f csv --timestamp monitor Open_vSwitch \
        Open_vSwitch statistics > ovs_stats

2) Clean raw data and get sorted data
python ovs_data_parse.py ovs_stats sorted_ovs_stats

3) Process cleaned data and visualize data in R

"""

import os
import sys
import re
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def subtract_timestamp(time_string):
    """This function subtract the timestamp

    :param time_string: The string contains the timestamp
    :return time: return the timestamp:
    """
    time_prefix = '2015-'

    time = None
    if time_prefix in time_string:
        time = re.search('2015-(.+?)\.', time_string).group(1)

    return time

def subtract_stats(stats_string):
    """This function subtract the stats

    :param stats_string: The string contains the ovs stats
    :return stats: return the stats substring:
    """
    stats_prefix = 'new,"'

    stats = None
    if stats_prefix in stats_string:
        stats = re.search('new,"{(.+?)}"', stats_string).group(1)

    return stats

def clean_stats(stats):
    """This function cleaned the raw stats from a stats string
       list.

    :param stats: the raw ovs stats string string
    :return cleaned_stats: the string contain the csv format stats
    """
    comma = ','

    load_average = re.search('load_average=""(.+?)"",', stats).group(1)
    memory = re.search('memory=""(.+?)"",', stats).group(1)
    switchd = re.search('process_ovs-vswitchd=""(.+?)"",', stats).group(1)
    ovsdb = re.search('process_ovsdb-server=""(.+?)""', stats).group(1)
    cleaned_stats = comma.join([load_average, memory, switchd, ovsdb])

    return cleaned_stats

def generate_csv(raw_data_path, csv_path):
    """This function clean the raw data and generate the output as the csv format

    :param raw_data_path: raw data from openvswitch stats
    :param csv_path: The csv data output
    """
    comma = ','
    time_prefix = '2015-'
    rowname = 'time,load average 1min,load average 5min,load average 15min,' +\
              'total mem,used mem,flushable mem,total swap,used swap,' +\
              'switchd mem,switchd size,switchd cpu time,switchd restarted,' +\
              'switchd started duration,switchd running duration,ovsdb mem,' +\
              'ovsdb size,ovsdb cpu time,ovsdb restarted,' +\
              'ovsdb started duration,ovsdb running duration'

    try:
        with open(raw_data_path, 'r') as inputfile:
            file_content = inputfile.readlines()
    except IOError:
        LOGGER.critical('input file does not exist')
        sys.exit(1)

    time = [time_prefix + subtract_timestamp(line) for line in file_content \
            if subtract_timestamp(line) is not None]

    # subtract the initial timestamp from time list
    time = time[:-1]

    stats = [subtract_stats(line) for line in file_content \
            if subtract_stats(line) is not None]

    cleaned_stats = [clean_stats(element) for element in stats]

    if len(time) == len(cleaned_stats):
        csv = [time[x] + comma + cleaned_stats[x] + '\r\n' \
                for x in range(len(time))]
        print csv
    else:
        LOGGER.critical('incorrect timestamp and ovs stats')
        sys.exit(1)

    # insert a row of rownames
    csv.insert(0, rowname + '\r\n')
    print csv

    with open(csv_path, 'w') as outputfile:
        outputfile.writelines(csv)

    inputfile.closed
    outputfile.closed

if __name__ == '__main__':
    generate_csv(sys.argv[1], sys.argv[2])
