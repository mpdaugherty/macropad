import os
import glob
import time

# find all tty devices under /dev/tty.* that have "usbmodem" in the name
# and return the first one


def find_tty():
    for tty in glob.glob("/dev/tty.*"):
        if "usbmodem" in tty:
            return tty
    return None


while True:
    tty = find_tty()
    if tty:
        # execute shell command to screen into the tty
        os.system("screen " + tty + " 115200")

    time.sleep(3)
