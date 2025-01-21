import RPi.GPIO as GPIO
import time

# GPIO-Pins für die LEDs
RED = 17
YELLOW = 27
GREEN = 22

# GPIO-Modus festlegen
GPIO.setmode(GPIO.BCM)

# Pins als Ausgang konfigurieren
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(YELLOW, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)

################################

try:
    while True:
        # Rot an, andere aus
        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(YELLOW, GPIO.LOW)
        GPIO.output(GREEN, GPIO.LOW)
        time.sleep(2)

        # Gelb an, andere aus
        GPIO.output(RED, GPIO.LOW)
        GPIO.output(YELLOW, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.LOW)
        time.sleep(1)

        # Grün an, andere aus
        GPIO.output(RED, GPIO.LOW)
        GPIO.output(YELLOW, GPIO.LOW)
        GPIO.output(GREEN, GPIO.HIGH)
        time.sleep(2)

except KeyboardInterrupt:
    print("Beendet vom Benutzer")

finally:
    # GPIO-Pins zurücksetzen
    GPIO.cleanup()
