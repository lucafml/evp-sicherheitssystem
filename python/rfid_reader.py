import mysql.connector
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import time
import threading

######## Ampel Config #########

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

GPIO.setwarnings(False)

reader = SimpleMFRC522()

sys_state = False

# Globale Variable für den Blink-Thread
blink_thread = None
stop_blinking = False

def sys_activate():
    global sys_state
    sys_state = True
    print("Sicherheitssystem wurde aktiviert")
    # Grün an, andere aus
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(YELLOW, GPIO.LOW)
    GPIO.output(GREEN, GPIO.HIGH)
    time.sleep(2)

def sys_deactivate():
    global sys_state
    sys_state = False
    print("Sicherheitssystem wurde deaktiviert")
    # Rot an, andere aus
    GPIO.output(RED, GPIO.HIGH)
    GPIO.output(YELLOW, GPIO.LOW)
    GPIO.output(GREEN, GPIO.LOW)
    time.sleep(2)

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="evp_vre_db",
            connection_timeout=5  # Timeout hinzugefügt
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Datenbankverbindungsfehler: {e}")
        return None

def add_user_to_db(username):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
        conn.commit()
        print("Benutzer erfolgreich hinzugefügt")
    except mysql.connector.IntegrityError:
        print("Benutzer existiert bereits")
    finally:
        conn.close()

def check_user_in_db(username):
    conn = connect_db()
    if not conn:
        return None
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username.strip(),))
        user = cursor.fetchone()
        return user
    except mysql.connector.Error as e:
        print(f"Datenbankabfragefehler: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        conn.close()

def security_state_change(username, state):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO security_state_changes (username, event_type) VALUES (%s, %s)",
            (username, state)
        )
        conn.commit()
        print(f"Sicherheitsstatus-Änderung wurde erfolgreich protokolliert: {username}, {state}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
    finally:
        conn.close()

def blink_status_led():
    global stop_blinking
    while not stop_blinking:
        if sys_state:
            # System aktiv: Grün blinkt
            GPIO.output(GREEN, GPIO.HIGH)
            GPIO.output(RED, GPIO.LOW)
            time.sleep(1.0)
            GPIO.output(GREEN, GPIO.LOW)
            time.sleep(1.0)
        else:
            # System inaktiv: Rot blinkt
            GPIO.output(RED, GPIO.HIGH)
            GPIO.output(GREEN, GPIO.LOW)
            time.sleep(1.0)
            GPIO.output(RED, GPIO.LOW)
            time.sleep(1.0)

def start_status_blink():
    global blink_thread, stop_blinking
    stop_blinking = False
    blink_thread = threading.Thread(target=blink_status_led)
    blink_thread.daemon = True
    blink_thread.start()

def stop_status_blink():
    global stop_blinking
    stop_blinking = True
    if blink_thread:
        blink_thread.join(timeout=1.0)

def update_led_state():
    # Gelb dauerhaft an für Bereitschaft
    GPIO.output(YELLOW, GPIO.HIGH)
    # Starte Blink-Effekt für aktuellen Status
    start_status_blink()

def error_blink():
    # Schnelles Blinken für Fehlersignal
    for _ in range(5):  # 5 mal blinken
        GPIO.output(YELLOW, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(YELLOW, GPIO.LOW)
        time.sleep(0.2)

def readChip():
    print("Bitte halte die RFID-Karte an den Scanner...")
    update_led_state()
    
    try:
        # Warte auf Karte
        id, user = reader.read()

        # Überprüfen auf leere oder ungültige Daten
        if not user or len(user.strip()) == 0:
            print("Ungültige Kartendaten")
            stop_status_blink()
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
            error_blink()
            
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        stop_status_blink()
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
        update_led_state()
        
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