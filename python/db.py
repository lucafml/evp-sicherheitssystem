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
    with connect_db() as conn:
        if not conn:
            return None
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s", (username.strip(),))
                user = cursor.fetchone()
                return user
        except mysql.connector.Error as e:
            print(f"Datenbankabfragefehler: {e}")
            return None

def security_state_change(username, state):
    with connect_db() as conn:
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO security_state_changes (username, event_type) VALUES (%s, %s)",
                        (username, state)
                    )
                    conn.commit()
                    print(f"Sicherheitsstatus-Änderung wurde erfolgreich protokolliert: {username}, {state}")
            except Exception as e:
                print(f"Ein Fehler ist aufgetreten: {e}")
        else:
            print("Fehler bei der Datenbankverbindung.")