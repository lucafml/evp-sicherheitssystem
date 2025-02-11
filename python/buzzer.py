import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

buzzer = 23
GPIO.setup(buzzer, GPIO.OUT)

pwm = GPIO.PWM(buzzer, 440)
pwm.start(0)

def activated_sound():
    pwm.ChangeFrequency(440)
    pwm.ChangeDutyCycle(50)
    time.sleep(1)
    pwm.ChangeDutyCycle(0)

def deactivated_sound():
    for _ in range(2):
        pwm.ChangeFrequency(440)
        pwm.ChangeDutyCycle(50)
        time.sleep(0.1)
        pwm.ChangeDutyCycle(0)
        time.sleep(0.1)

def error_sound():
    for _ in range(5):
        pwm.ChangeFrequency(440)
        pwm.ChangeDutyCycle(50) 
        time.sleep(0.1)
        pwm.ChangeDutyCycle(0)
        time.sleep(0.1)
