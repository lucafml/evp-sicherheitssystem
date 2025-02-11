import mysql.connector
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import time
import threading
from buzzer import activated_sound, deactivated_sound, error_sound
from leds import blink_status_led, start_status_blink, stop_status_blink, update_led_state, error_blink, only_green, only_red
from db import check_user_in_db, security_state_change
from bewegunssensor import BewegungsSensor
from button import Button
from flask import Flask, jsonify
from flask_cors import CORS
import logging

sys_state = False
bewegungssensor = None
button = None
bewegungssensor_thread = None
button_thread = None

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

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/system-state')
def get_system_state():
    return jsonify({'state': 'aktiviert' if sys_state else 'deaktiviert'})

def bewegungssensor_loop():
    global bewegungssensor
    while sys_state:
        if bewegungssensor and bewegungssensor.is_active:
            bewegungssensor.check_motion()
        time.sleep(0.1)

def button_loop():
    global button
    while sys_state:
        if button and button.is_active:
            button.check_button()
        time.sleep(0.1)

def sys_activate():
    global sys_state, bewegungssensor, button, bewegungssensor_thread, button_thread
    sys_state = True
    activated_sound()
    
    if not bewegungssensor:
        bewegungssensor = BewegungsSensor()
    bewegungssensor.start_detection()
    
    if not button:
        button = Button()
    button.start_detection()
    
    if not bewegungssensor_thread or not bewegungssensor_thread.is_alive():
        bewegungssensor_thread = threading.Thread(target=bewegungssensor_loop)
        bewegungssensor_thread.daemon = True
        bewegungssensor_thread.start()
        
    if not button_thread or not button_thread.is_alive():
        button_thread = threading.Thread(target=button_loop)
        button_thread.daemon = True
        button_thread.start()
    
    only_green()
    print("Sicherheitssystem wurde aktiviert")
    time.sleep(2)

def sys_deactivate():
    global sys_state, bewegungssensor, button
    sys_state = False
    deactivated_sound()
    print("Sicherheitssystem wurde deaktiviert")
    only_red()
    
    if bewegungssensor:
        bewegungssensor.cleanup()
        bewegungssensor = None
    
    if button:
        button.cleanup()
        button = None
    
    time.sleep(2)
      
def readChip():
    print("Bitte halte die RFID-Karte an den Scanner...")
    update_led_state(sys_state)
    
    try:
        id, user = reader.read()

        if not user or len(user.strip()) == 0:
            print("Ungültige Kartendaten")
            stop_status_blink()
            error_sound()
            error_blink()
            return

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

# Temporäre Funktion zum Schreiben von Chips - wird nicht aktiv genutzt
def writeChip():
    try:
        user = input("Bitte username eingeben, der auf dem Chip gespeichert werden soll: ")

        print("Bitte halte den Chip an den Scanner")
        reader.write(user)
        print("Chip wurde erfolgreich beschrieben")
        
        print("Überprüfe geschriebene Daten...")
        id, user = reader.read()
        print(f"Gespeicherte Daten: {user}")
        
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
    finally:
        GPIO.cleanup()

def start_flask():
    log = logging.getLogger('werkzeug')
    log.disabled = True
    
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, app, use_reloader=False, use_debugger=False, threaded=True)

def main():
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    import signal
    def signal_handler(signum, frame):
        print("\nProgramm wird beendet...")
        stop_status_blink()
        GPIO.cleanup()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RED, GPIO.OUT)
        GPIO.setup(YELLOW, GPIO.OUT)
        GPIO.setup(GREEN, GPIO.OUT)
        
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