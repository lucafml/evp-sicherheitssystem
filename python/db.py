# database.py
import mysql.connector

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="evp_vre_db",
            connection_timeout=5
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Datenbankverbindungsfehler: {e}")
        return None

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