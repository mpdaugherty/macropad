import time
import board  # microcontroller pins definitions
import keypad  # library for scanning microcontroller pins for keypresses
import alarm  # alarm for putting the microcontroller to sleep to save power

# bluetooth libraries
import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.advertising import Advertisement
from adafruit_ble.services.standard.hid import HIDService

# keyboard driver libraries
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# Keycode character code documentation is at
# https://docs.circuitpython.org/projects/hid/en/latest/_modules/adafruit_hid/keycode.html

# Default to app-switching layer
current_layer = 4

def handle_vs(event, keyboard):
    layout = KeyboardLayoutUS(keyboard)

    if event.pressed:
        if event.key_number == 0:
            layout.write("# This is Visual Studio Mode")
        elif event.key_number == 1:
            return  # Do nothing; the button is not working
            # keyboard.press(Keycode.COMMAND, Keycode.SPACE)
        elif event.key_number == 2:
            # Toggle comments in Visual Studio Code
            keyboard.press(Keycode.COMMAND, Keycode.FORWARD_SLASH)
        elif event.key_number == 3:
            # Re-format code in Visual Studio Code
            keyboard.press(Keycode.SHIFT, Keycode.OPTION, Keycode.F)
        elif event.key_number == 4:
            set_app_switching(keyboard)
        elif event.key_number == 8:
            # Toggle Full Screen
            keyboard.press(Keycode.CONTROL, Keycode.COMMAND, Keycode.F)
        else:
            keyboard.press(KEYMAP[event.key_number])
    else:
        keyboard.release_all()


def handle_superhuman(event, keyboard):
    layout = KeyboardLayoutUS(keyboard)

    if event.pressed:
        if event.key_number == 0:
            layout.write("\n\nCheers,\nMichael Daugherty")
        elif event.key_number == 1:
            return  # Do nothing; the button is not working
            # keyboard.press(Keycode.COMMAND, Keycode.SPACE)
        elif event.key_number == 2:
            # Create a new email and refer to the previous email
            keyboard.press(Keycode.C)
            keyboard.release(Keycode.C)
            keyboard.press(Keycode.COMMAND, Keycode.SHIFT, Keycode.P)
        elif event.key_number == 3:
            layout.write("Hello!")
        elif event.key_number == 4:
            set_app_switching(keyboard)
        elif event.key_number == 8:
            # Toggle Full Screen
            keyboard.press(Keycode.CONTROL, Keycode.COMMAND, Keycode.F)
        else:
            keyboard.press(KEYMAP[event.key_number])
    else:
        keyboard.release_all()

def handle_roam(event, keyboard):
    layout = KeyboardLayoutUS(keyboard)

    if event.pressed:
        if event.key_number == 0:
            # Toggle sidebar
            keyboard.press(Keycode.COMMAND, Keycode.FORWARD_SLASH)
        elif event.key_number == 1:
            return  # Do nothing; the button is not working
        elif event.key_number == 2:
            # Go to current day, open a new block, and zoom into it for a blank editing experience
            keyboard.press(Keycode.CONTROL, Keycode.SHIFT, Keycode.D)
            keyboard.release_all()
            keyboard.press(Keycode.COMMAND, Keycode.SHIFT, Keycode.ENTER)
            keyboard.release_all()
            keyboard.press(Keycode.CONTROL, Keycode.E)
            keyboard.release_all()
            keyboard.press(Keycode.ENTER)
            keyboard.release_all()
            keyboard.press(Keycode.COMMAND, Keycode.PERIOD)
        elif event.key_number == 3:
            # Open link under cursor in sidebar
            keyboard.press(Keycode.CONTROL, Keycode.SHIFT, Keycode.O)
        elif event.key_number == 4:
            set_app_switching(keyboard)
        elif event.key_number == 8:
            # Toggle Full Screen
            keyboard.press(Keycode.CONTROL, Keycode.COMMAND, Keycode.F)
        else:
            keyboard.press(KEYMAP[event.key_number])
    else:
        keyboard.release_all()


def handle_app_switching(event, keyboard):
    global current_layer
    layout = KeyboardLayoutUS(keyboard)
    if event.pressed:
        if event.key_number == 0:
            layout.write("Visual Studio Code")
            keyboard.press(Keycode.ENTER)

        if event.key_number == 2:
            layout.write("Superhuman")
            keyboard.press(Keycode.ENTER)

        if event.key_number == 3:
            layout.write("Roam Research")
            keyboard.press(Keycode.ENTER)

        if event.key_number == 4:
            set_app_switching(keyboard)

        current_layer = event.key_number
    else:
        keyboard.release_all()

def set_app_switching(keyboard):
    global current_layer
    keyboard.press(Keycode.COMMAND, Keycode.SPACE)
    keyboard.release(Keycode.COMMAND, Keycode.SPACE)
    current_layer = 4

LAYERS = [
  handle_vs, None, handle_superhuman,
  handle_roam, handle_app_switching, None,
  None, None, None
]

def process_keypress(event, keyboard):
    global current_layer

    """Handle each key press/release event. Add your custom macro pad behavior here.

    event.key_number is the index of the key that was pressed (0-8 top to bottom, left to right)
    """
    print(event)
    print(current_layer)

    # by default we just look up a key from the keymap and send its keycode
    # see what you can do with Keyboard module here: https://learn.adafruit.com/circuitpython-essentials/circuitpython-hid-keyboard-and-mouse

    # What would you like your macro pad to do?
    #
    # Have a button send an entire string of text?
    # Send combinations of keycodes like Ctrl+C/Ctrl+V?
    # Send a keycode every second for 10 seconds?
    # Send custom key codes when a combination of keys are pressed?
    # Send a keycode when a key is pressed and immediately released, and a different keycode when the key is held down?

    layout = KeyboardLayoutUS(keyboard)

    if event.key_number == 4:
        if event.pressed:
            set_app_switching(keyboard)
        else:
            keyboard.release_all()
    else:
        if LAYERS[current_layer]:
            LAYERS[current_layer](event, keyboard)
        else:
            if not event.pressed:
                keyboard.release_all()
            current_layer = 4

# -------------------------------------------------------------------------------
# You don't need to change anything below this line, but its fun to follow along!
# -------------------------------------------------------------------------------


SLEEP_TIMEOUT = 5          # sleep after 5 seconds of inactivity
SLEEP_DURATION = 0.05      # sleep 50ms at a time to not miss any keypresses
RECONNECT_EVERY_T = 30*60  # try reconnecting every 30 minutes if not connected
BLE_SCAN_TIMEOUT = 10      # advertise Bluetooth for 10 seconds before giving up
BLE_NAME = "MPD MacroPad"  # device name advertised over Bluetooth


def macro_main():
    """ Main loop for the macro pad """
    scanner = setup_scanner()
    keyboard = setup_keyboard()
    last_event_t = time.monotonic()

    while True:
        event = scanner.events.get()

        # regularly check if BLE is connected. If a button is pressed while BLE
        # disconnected, force reconnect attempt immediately
        if ble_reconnect_if_needed(force_reconnect=event):
            # reconnect attempt happened, reset the keyboard, and clear the event queue
            keyboard = setup_keyboard()
            scanner.events.clear()
            continue

        if event:
            last_event_t = time.monotonic()
            process_keypress(event, keyboard)

        if time.monotonic() - last_event_t > SLEEP_TIMEOUT:
            scanner = sleep(scanner)


def setup_scanner():
    """ Setup keypad switch scanner
    https://learn.adafruit.com/key-pad-matrix-scanning-in-circuitpython/keys-one-key-per-pin
    """
    # microcontroller pins corresponding to the buttons on the macropad
    pins = [
        board.D0, board.D1, board.D2,
        board.D3, board.D4, board.D5,
        board.D6, board.D7, board.D8
    ]

    return keypad.Keys(pins, value_when_pressed=False, pull=True)


def setup_keyboard():
    hid = get_ble_hid()
    if hid:
        return Keyboard(hid)


def sleep(scanner):
    """ Put the microcontroller to sleep to save power
     https://learn.adafruit.com/deep-sleep-with-circuitpython/alarms-and-sleep
    """
    scanner.deinit()  # disable the keypad scanner to save power
    time_alarm = alarm.time.TimeAlarm(
        monotonic_time=time.monotonic() + SLEEP_DURATION)
    alarm.light_sleep_until_alarms(time_alarm)
    return setup_scanner()


last_reconnect_attempt_t = time.monotonic()


def ble_reconnect_if_needed(force_reconnect=False):
    global last_reconnect_attempt_t
    if force_reconnect or (time.monotonic() - last_reconnect_attempt_t > RECONNECT_EVERY_T):
        last_reconnect_attempt_t = time.monotonic()
        ble = adafruit_ble.BLERadio()
        if not ble.connected:
            get_ble_hid()
            return True


def get_ble_hid(timeout=BLE_SCAN_TIMEOUT):
    """ Connect to the computer via Bluetooth HID
    https://learn.adafruit.com/ble-hid-keyboard-buttons-with-circuitpython/ble-keyboard-buttons-libraries-and-code
    """
    ble = adafruit_ble.BLERadio()

    ble.name = BLE_NAME

    hid = HIDService()
    advertisement = ProvideServicesAdvertisement(hid)
    advertisement.appearance = 961
    scan_response = Advertisement()
    scan_response.complete_name = BLE_NAME
    ble.start_advertising(advertisement, scan_response)

    start_t = time.monotonic()
    while not ble.connected:
        if time.monotonic() - start_t > timeout:
            print("Timed out waiting for connection.")
            ble.stop_advertising()
            return None
        time.sleep(1)
        print("advertising BLE HID...")

    print("BLE HID connected!")
    return hid.devices


macro_main()
