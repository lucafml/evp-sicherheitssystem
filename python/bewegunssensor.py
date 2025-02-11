import RPi.GPIO as GPIO
import time
import mysql.connector

class BewegungsSensor:
    def __init__(self, pin=18, cooldown_time=10):
        self.SENSOR_PIN = pin
        self.COOLDOWN_TIME = cooldown_time
        self.last_motion = 0
        self.is_active = False
        
        GPIO.setup(self.SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    def start_detection(self):
        """Startet die Bewegungserkennung"""
        self.is_active = True
        
    def stop_detection(self):
        """Stoppt die Bewegungserkennung"""
        self.is_active = False
    
    def check_motion(self):
        """Überprüft ob eine Bewegung erkannt wurde"""
        if not self.is_active:
            return False
            
        current_time = time.time()
        sensor_status = GPIO.input(self.SENSOR_PIN)
        
        if sensor_status == 1 and (current_time - self.last_motion > self.COOLDOWN_TIME):
            self.last_motion = current_time
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="evp_vre_db"
                )
                cursor = connection.cursor()
                sql = "INSERT INTO bewegungen (status) VALUES ('Bewegung erkannt')"
                cursor.execute(sql)
                connection.commit()
                cursor.close()
                connection.close()
                print("Bewegung registriert. Eintrag in DB gespeichert!")
                return True
            except Exception as e:
                print(f"Fehler beim Speichern der Bewegung: {e}")
        return False
    
    def cleanup(self):
        """Räumt die GPIO-Ressourcen auf"""
        self.stop_detection()