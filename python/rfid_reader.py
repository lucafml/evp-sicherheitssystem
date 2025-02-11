import mysql.connector
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import time
import threading
from buzzer import activated_sound, deactivated_sound, error_sound
from leds import blink_status_led, start_status_blink, stop_status_blink, update_led_state, error_blink, only_green, only_red
from db import check_user_in_db, security_state_change

sys_state = False


# GPIO-Pins für die LEDs
RED = 17
YELLOW = 27
GREEN = 22

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(RED, GPIO.OUT)
GPIO.setup(YELLOW, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)


reader = SimpleMFRC522()

blink_thread = None
stop_blinking = False

def sys_activate():
    global sys_state
    sys_state = True
    activated_sound()
    print("Sicherheitssystem wurde aktiviert")
    only_green()
    time.sleep(2)

def sys_deactivate():
    global sys_state
    sys_state = False
    deactivated_sound()
    print("Sicherheitssystem wurde deaktiviert")
    only_red()
    time.sleep(2)
      
def readChip():
    print("Bitte halte die RFID-Karte an den Scanner...")
    update_led_state(sys_state)
    
    try:
        # Warte auf Karte
        id, user = reader.read()

        # Überprüfen auf leere oder ungültige Daten
        if not user or len(user.strip()) == 0:
            print("Ungültige Kartendaten")
            stop_status_blink()
            error_sound()
            error_blink()
            return

        # Benutzer in der Datenbank überprüfen
        DBuser = check_user_in_db(user)
        if DBuser:
            print(f"Zugriff gewährt für {DBuser[1]}")
            stop_status_blink()
            try:
                if sys_state:
                    sys_deactivate()
                    security_state_change(DBuser[1], "deaktiviert")
                else:
                    sys_activate()
                    security_state_change(DBuser[1], "aktiviert")
            except Exception as e:
                print(f"Fehler bei Statusänderung: {e}")
                error_blink()
        else:
            print(f"Benutzer nicht gefunden! Zugriff verweigert")
            stop_status_blink()
            error_sound()
            error_blink()
            
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        stop_status_blink()
        error_sound()
        error_blink()

def writeChip():
    try:
        user = input("Bitte username eingeben, der auf dem Chip gespeichert werden soll: ")

        print("Bitte halte den Chip an den Scanner")
        reader.write(user)
        print("Chip wurde erfolgreich beschrieben")
        
        # Optional: Überprüfen der geschriebenen Daten
        print("Überprüfe geschriebene Daten...")
        id, user = reader.read()
        print(f"Gespeicherte Daten: {user}")
        
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
    finally:
        GPIO.cleanup()


def main():
    # Signal-Handler für sauberes Beenden
    import signal
    def signal_handler(signum, frame):
        print("\nProgramm wird beendet...")
        stop_status_blink()
        GPIO.cleanup()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # GPIO-Modus am Anfang setzen
        GPIO.setmode(GPIO.BCM)
        # Pins als Ausgang konfigurieren
        GPIO.setup(RED, GPIO.OUT)
        GPIO.setup(YELLOW, GPIO.OUT)
        GPIO.setup(GREEN, GPIO.OUT)
        
        # Initialer LED-Status
        update_led_state(sys_state)
        
        print("RFID-Reader gestartet. Drücken Sie Strg+C zum Beenden.")
        
        while True:
            try:
                readChip()
                time.sleep(2)
            except Exception as e:
                print(f"Fehler beim Lesen: {e}")
                time.sleep(1)
    except Exception as e:
        print(f"Kritischer Fehler: {e}")
    finally:
        stop_status_blink()
        GPIO.cleanup()

main()