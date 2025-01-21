import mysql.connector
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)

reader = SimpleMFRC522()

sys_state = False;

def sys_activate():
    global sys_state
    sys_state = True
    print("Sicherheitssystem wurde aktiviert")

def sys_deactivate():
    global sys_state
    sys_state = False
    print("Sicherheitssystem wurde deaktiviert")

def connect_db():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="evp_vre_db"
    )
    return conn

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
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

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

def readChip():
    try:
        print("Bitte halte die RFID-Karte an den Scanner...")
        id, user = reader.read()

        # Benutzer in der Datenbank überprüfen
        DBuser = check_user_in_db(user)
        if DBuser:
            print(f"Zugriff gewährt für {DBuser[1]}")
            if sys_state == True:
                sys_deactivate()
                security_state_change(DBuser[1], "deaktiviert")
            elif sys_state == False:
                sys_activate()
                security_state_change(DBuser[1], "aktiviert")
        else:
            print(f"Benutzer nicht gefunden! Zugriff verweigert")
    except Exception as e:
        # Allgemeine Fehlerbehandlung
        print(f"Ein Fehler ist aufgetreten: {e}")
    finally:
        GPIO.cleanup()


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
    try:
        while True:
            try:
                readChip()
                time.sleep(5)
            except Exception as e:
                print(f"Fehler beim Lesen: {e}")
                time.sleep(1)
    finally:
        GPIO.cleanup()

main()