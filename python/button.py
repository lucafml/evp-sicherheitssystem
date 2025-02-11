import RPi.GPIO as GPIO
import time
import mysql.connector

class Button:
    def __init__(self, pin: int = 20, cooldown_time: int = 10):
        self.pin = pin
        self.is_active = False
        self.COOLDOWN_TIME = cooldown_time
        self.last_trigger = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
    def start_detection(self):
        """Aktiviert die Button-Überwachung"""
        self.is_active = True
        
    def check_button(self):
        """Überprüft den Button-Status und löst bei Bedarf den Alarm aus"""
        current_time = time.time()
        
        if (self.is_active and 
            GPIO.input(self.pin) == GPIO.LOW and 
            (current_time - self.last_trigger > self.COOLDOWN_TIME)):
            
            self.last_trigger = current_time
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="evp_vre_db"
                )
                cursor = connection.cursor()
                sql = "INSERT INTO lichtschranke (status) VALUES ('Lichtschranke ausgelöst')"
                cursor.execute(sql)
                connection.commit()
                cursor.close()
                connection.close()
                print("Lichtschranke wurde ausgelöst. Eintrag in DB gespeichert!")
            except Exception as e:
                print(f"Fehler beim DB-Eintrag für Button-Alarm: {e}")
            time.sleep(0.2)  # Entprellen
            
    def cleanup(self):
        """Beendet die Button-Überwachung"""
        self.is_active = False