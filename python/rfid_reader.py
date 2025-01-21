from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

reader = SimpleMFRC522()

def readChip():
	try:
		print("Bitte halte die RFID-Karte an den Scanner...")
		id, text = reader.read()
		print(f"ID: {id}")
		print(f"Text: {text}")
	finally:
		GPIO.cleanup()

def writeChip():
	try:
		text = input("Bitte Text eingeben, der auf dem Chip gespeichert werden soll: ")
		print("Bitte halte den Chip an den Scanner")
		reader.write(text)
		print("Chip wurde erfolgreich beschrieben")
	finally:
		GPIO.cleanup()

writeChip()
readChip()
