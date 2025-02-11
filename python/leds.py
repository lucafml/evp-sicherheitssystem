import RPi.GPIO as GPIO
import time
import threading

# Pins für LEDs (diese müssen vorher in main.py gesetzt werden!)
RED = 17
YELLOW = 27
GREEN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(YELLOW, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)

blink_thread = None
stop_blinking = False

def only_green():
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(YELLOW, GPIO.LOW)
    GPIO.output(GREEN, GPIO.HIGH)

def only_red():
    GPIO.output(RED, GPIO.HIGH)
    GPIO.output(YELLOW, GPIO.LOW)
    GPIO.output(GREEN, GPIO.LOW)

def blink_status_led(sys_state):
    global stop_blinking
    while not stop_blinking:
        if sys_state:
            GPIO.output(GREEN, GPIO.HIGH)
            GPIO.output(RED, GPIO.LOW)
            time.sleep(1.0)
            GPIO.output(GREEN, GPIO.LOW)
            time.sleep(1.0)
        else:
            GPIO.output(RED, GPIO.HIGH)
            GPIO.output(GREEN, GPIO.LOW)
            time.sleep(1.0)
            GPIO.output(RED, GPIO.LOW)
            time.sleep(1.0)

def start_status_blink(sys_state):
    global blink_thread, stop_blinking
    stop_blinking = False
    blink_thread = threading.Thread(target=blink_status_led, args=(sys_state,))
    blink_thread.daemon = True
    blink_thread.start()

def stop_status_blink():
    global stop_blinking
    stop_blinking = True
    if blink_thread and blink_thread.is_alive():
        blink_thread.join(timeout=1.0)

def update_led_state(sys_state):
    GPIO.output(YELLOW, GPIO.HIGH)
    start_status_blink(sys_state)

def error_blink():
    for _ in range(5):
        GPIO.output(YELLOW, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(YELLOW, GPIO.LOW)
        time.sleep(0.2)
