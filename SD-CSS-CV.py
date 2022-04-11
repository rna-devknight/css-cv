# CSS CV
# Development of the computer vision program for
# CSS (The Car Sentry System)

import spidev
import os
import sys
import json
import time
import logging
import datetime
import threading
import cv2 as cv
import numpy as np
from openalpr import Alpr

def easy_spi_test(message):
    failed = False

    # Convert messge froms tring to btyes
    msg = message.encode('utf-8')

    # SPI settings
    bus = 0
    device = 0
    speed = 8000000

    # Enables SPI Communication
    spi = spidev.SpiDev()

    print("--------------------")
    print("Message received ({0})".format(message))
    print("Converting to bytes...")
    print("Message in bytes ({0})".format(msg))
    print("--------------------")

    # SPI Setup
    try:
        print("Attempting to open SPI port {0}, device {1}...".format(bus, device))
        spi.open(bus, device)
        print("Connection established")
        print("Applying settings...")
        spi.max_speed_hz = speed
        spi.lsbfirst = False
        spi.loop = True
        print("Settings applied successfully!")
    except Exception as e:
        print("Failed to apply settings")
        print(e)
        failed = True

    if not failed:
        print("Attempting transmission...")
        msg_len = len(message)
        spi.writebytes2(msg)

        while True:
            print(spi.readbytes(msg_len))
            
        print("Transmission complete")

    
    if spi:
        spi.close()

def spi_write(message):
    spi = spi_start()

    logging.info("Begin transmission......")

    if spi is not None:
        msg_in_bytes = message.encode('utf-8')
        writebytes2(msg_in_bytes)

        # spi.xfer()
    
    logging.info("End transmission......")

    spi.close()

def spi_start():
    # SPI settings
    bus = 0
    device = 0
    speed = 8000000

    logging.info("Beginning SPI connection......")

    spi_settings_log = "Port: {bus}\n Device: {device}\n Max_Speed = {speed}\n".format()
    logging.info(spi_settings_log)

    # Enables SPI communication
    spi = spidev.SpiDev()

    logging.info("Establishing connection......")
    
    # SPI setup
    try:
        # Opens SPI port 0, device (CS) 1
        spi.open(bus, device)
        logging.info("Connection established")
        spi.max_speed_hz = speed
        logging.info("Speed set")
        spi.mode = 0b10
        logging.info("Mode set")
        spi.lsbfirst = False
        logging.info("Settings applied")
    except Exception as e:
        logging.critical("{e}".format())

        if spi:
            spi.close()
            return None

    return spi

# Redundant module
def file_check():
    debug_file = open("debug.txt", 'a+')

    for lines in debug_file:
        print(lines)

    debug_file.write("Ready check\n")

    debug_file.close()

# Redundant module, DELETE
def write_debug(message_string):
    debug_file = open("debug.txt", 'a')

    debug_file.write(message_string + "\n")

def generate_txt_file():
    log_file = open("log.txt", 'a')
    debug_file = open("debug.txt", 'a')

    log_file.close()
    debug_file.close()

# def gstreamer_pipeline(capture_width=1920, capture_height=1080, display_width=720, display_height=480, framerate=30, flip_method=0):
def gstreamer_pipeline(capture_width, capture_height, display_width, display_height, framerate, flip_method):
    return (
		'nvarguscamerasrc ! ' 
		'video/x-raw(memory:NVMM), '
		'width=(int)%d, height=(int)%d, '
		'format=(string)NV12, framerate=(fraction)%d/1 ! '
		'nvvidconv flip-method=%d ! '
		'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
		'videoconvert ! '
		'video/x-raw, format=(string)BGR ! appsink'  % (capture_width,capture_height,framerate,flip_method,display_width,display_height)
    )

def capture_plate(coordinates, image_frame):
    i = 0

    image_path = "/captures"

    logging.info("Beginning image capture.......")
    logging.info("Verifying directory.......")

    try:
        os.mkdir(image_path, exist_ok = True)
        logging.info("Directory created")
    except OSError as error:
        logging.warning("{0}".format(error))

    logging.info("Obtaining coordinates.......")
    x = int(min(coordinates['coordinates'], key=lambda ev: ev['x'])['x'])
    y = int(min(coordinates['coordinates'], key=lambda ev: ev['y'])['y'])

    w = int(max(coordinates['coordinates'], key=lambda ev: ev['x'])['x'])
    h = int(max(coordinates['coordinates'], key=lambda ev: ev['y'])['y'])

    logging.info("Cropping image......")
    localized_img = img[x:w, y:h]

    while os.path.exists("car_plate_{i}.jpg".format(i)):
        i += 1

    img_name = "car_plate_{i}".format(i)
    og_img_name = f"{img_name}_full_capture"

    logging.info("Storing {img_name}".format())
    cv.imwrite(img_name, localized_img)
    cv.imwrite(og_img_name, image_frame)

    logging.info("Image capture success")

    # cv.rectangle(image_frame,(x,y),(w,h),(255,0,0),2)
    # cv.imshow('Plate Detected', image_frame)

def CSS_CV(alpr, frameArray):
    results = alpr.recognize_ndarray(frameArray)

    if results['results'] != []:
        max_c = max(results['results'], key=lambda ev: ev['confidence'])

        # If the confidence is greater than 90
        if int(max_c['confidence']) > 90:
            info_obtained = "Plate obtained: {0} Confidence of: {1}".format(max_c['plate'], max_c['confidence'])

            vehicle_plate = "{0}".format(max_c['plate'])

            print(info_obtained)
            print("Ignore this: {0}", vehicle_plate)
            logging.info(info_obtained)

            # Draws a rectangle around the license plate
            capture_plate(max_c, frameArray)

def main(debug):
    # Camera configuration
    # Possible configurations 3264x2464@21FPS, 1920x1080@30FPS, 720x480@60FPS
    capture_width = 1920
    capture_height = 1080
    
    # Viewing display configuration
    display_width = 720
    display_height = 480

    # Capture frame rate
    # Possible configrations 21, 30, and 60
    framerate =  29 # 30

    flip_method = 0

    logging.info("INITIALIZING......")
    logging.debug("DEBUG MODE ENABLED")
    logging.debug("RUNNING IN DEBUG MODE")

    # Refer to: https://github.com/openalpr/openalpr?msclkid=a9d97cf7a67e11ecb2347f01f212ea51
    alpr = Alpr("us", "/etc/openalpr/openalpr.conf", "../openalpr/runtime_data/")
    
    if not alpr.is_loaded():
        logging.critical("Failed to load OpenALPR")
        sys.exit(1)

    alpr.set_top_n(2)
    
    # Calling the gstreamer_pipeline to obtain the CSI camera feed
    camera_feed = cv.VideoCapture(gstreamer_pipeline(capture_width, capture_height, display_width, display_height, framerate, flip_method), cv.CAP_GSTREAMER)

    # If successfully able to connect to the camera
    if camera_feed.isOpened():
        logging.info("Feed open")

        # For debugging purposes
        if debug:
            cv.namedWindow('Debugger', cv.WINDOW_AUTOSIZE)

        frame = 0
        
        # while cv.getWindowProperty('Debugger', 0) >= 0:
        while True:
            # Grabs, decodes, and returns the next video frame
            obtainedFrames, theFrames = camera_feed.read()

            if obtainedFrames:
                frame += 1
                try:
                    # print("Initial Frame")
                    # If the first frame, start a new thread
                    if str(frame)[-1] == "0":
                        initialThread = threading.Thread(target = CSS_CV, args=(alpr, theFrames))
                        initialThread.start()
                except Exception as e:
                    logging.error("Error: {0}".format(e))

                if debug:
                    cv.imshow('Debugger', theFrames)

                # Waits 10ms to see if Esc key pressed
                # .waitkey returns a integer value for ASCII
                exit_key = cv.waitKey(50) & 0xff

                if exit_key == 27:
                    logging.info("Escape key pressed, shutting down")
                    break

        camera_feed.release()
        cv.destroyAllWindows()
        alpr.unload()
    else:
        logging.critical("UNABLE TO CONNECT TO CAMERA")

# DELETE
# Old module, most likely no longer needed
def development():
    generate_txt_file()
    file_check()

if __name__ == '__main__':
    testing_module = 1

    # Do not enable debug if in headless mode
    debug = True

    if debug:
        logging.basicConfig(filename = "debug.log", filemode="w", level = logging.DEBUG)

    if testing_module:
        easy_spi_test("Bingo")
    else:
        main(debug)