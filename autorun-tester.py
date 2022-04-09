# CSS CV

import spidev

import os
import sys
import json
import time
import datetime
import threading
import cv2 as cv
import numpy as np
from openalpr import Alpr

def file_check():
    debug_file = open("debug.txt", 'a+')

    for lines in debug_file:
        print(lines)

    debug_file.write("Autorun check 5\n")

    debug_file.close()

def generate_txt_file():
    log_file = open("log.txt", 'a')
    debug_file = open("debug.txt", 'a')

    log_file.close()
    debug_file.close()



def development():
    generate_txt_file()
    file_check()

if __name__ == '__main__':
    # main()
    development()
