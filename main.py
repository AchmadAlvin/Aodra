# Library
import time
import requests
import math
import random
import time
import RPi.GPIO as GPIO
import threading

# Ubidots Credentials
TOKEN = "BBFF-jtHMTHVhPvAKhjsDb83txH69EkD7S7"
DEVICE_LABEL = "aodra"
VARIABLE_LABEL_1 = "ultrasonik_1 sampah non Logam"
VARIABLE_LABEL_2 = "ultrasonik_2  sampah Logam"

GPIO.setmode(GPIO.BCM)

# Pinout
#ultrasonik1
PIN_TRIGGER_1 = 18
PIN_ECHO_1 = 24
#ultrasonik2
PIN_TRIGGER_2 = 27
PIN_ECHO_2 = 21
#Besi dan 3 servo
PIN_PROX = 25
PIN_SERVO_BESI = 17
PIN_SERVO_PALANG = 5
PIN_SERVO_PIR = 16
#pir
PIN_PIR = 23

interval = 1

# Frekuensi PWM Servo
GPIO.setup(PIN_SERVO_BESI, GPIO.OUT)
GPIO.setup(PIN_SERVO_PALANG, GPIO.OUT)
GPIO.setup(PIN_SERVO_PIR, GPIO.OUT)
pwm_besi = GPIO.PWM(PIN_SERVO_BESI, 50)
pwm_palang = GPIO.PWM(PIN_SERVO_PALANG, 50)
pwm_pir = GPIO.PWM(PIN_SERVO_PIR, 50)

def setup():
    GPIO.setmode(GPIO.BCM)  
    GPIO.setwarnings(False)
    # Setup Ultrasonik 1
    GPIO.setup(PIN_TRIGGER_1 ,GPIO.OUT)
    GPIO.setup(PIN_ECHO_1, GPIO.IN)  
    # Setup Ultrasonik 2
    GPIO.setup(PIN_TRIGGER_2 ,GPIO.OUT)
    GPIO.setup(PIN_ECHO_2, GPIO.IN)
    # Setup Proximity
    GPIO.setup(PIN_PROX, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # Setup Servo Besi dan palang
    GPIO.setup(PIN_SERVO_BESI, GPIO.OUT)
    pwm_besi.start(0)
    GPIO.setup(PIN_SERVO_PALANG, GPIO.OUT)
    pwm_palang.start(0)
    # Setup Servo PIR
    GPIO.setup(PIN_SERVO_PIR, GPIO.OUT)
    pwm_pir.start(0)
    # Setup PIR
    GPIO.setup(PIN_PIR, GPIO.IN)

def set_servo_besi(angle):
    duty_cycle = 2 + (angle / 18)
    pwm_besi.ChangeDutyCycle(duty_cycle)
    time.sleep(0.01)

def set_servo_palang(angle):
    duty_cycle = 2 + (angle / 18)
    pwm_palang.ChangeDutyCycle(duty_cycle)
    time.sleep(0.01)

def set_servo_pir(angle):
    duty_cycle = 2 + (angle / 18)
    pwm_pir.ChangeDutyCycle(duty_cycle)
    time.sleep(0.01)

#ultrasonik_1
def distance_1():
    GPIO.output(PIN_TRIGGER_1, GPIO.LOW)
    time.sleep(0.01)
    print ("Calculating distance 1")
    GPIO.output(PIN_TRIGGER_1, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(PIN_TRIGGER_1, GPIO.LOW)

    pulse_start_time = time.time()

    while GPIO.input(PIN_ECHO_1)==0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO_1)==1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    jarak = round(pulse_duration * 13150, 2)
    print(jarak)

    jarak_maksimal = 16.0  # Jarak maksimal dalam cm (saat kosong berapa)
    jarak_minimal = 3.0     # Jarak minimal dalam cm (saat penuh berapa)
    persentase = max(0, min(100, 100 - ((jarak - jarak_minimal) / (jarak_maksimal - jarak_minimal)) * 100))

    print(f"Jarak 1 dalam persentase: {persentase}%")  # Menampilkan persentase jarak
    
    return persentase


#ultrasonik_2
def distance_2():
    GPIO.output(PIN_TRIGGER_2, GPIO.LOW)
    time.sleep(0.01)
    print ("Calculating distance 2")
    GPIO.output(PIN_TRIGGER_2, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(PIN_TRIGGER_2, GPIO.LOW)

    pulse_start_time = time.time()

    while GPIO.input(PIN_ECHO_2)==0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO_2)==1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    jarak = round(pulse_duration * 13150, 2)
    print(jarak)

    jarak_maksimal = 16.0  # Jarak maksimal dalam cm
    jarak_minimal = 3.0     # Jarak minimal dalam cm
    persentase = max(0, min(100, 100 - ((jarak - jarak_minimal) / (jarak_maksimal - jarak_minimal)) * 100))

    print(f"Jarak 2 dalam persentase: {persentase}%")  # Menampilkan persentase jarak
    
    return persentase

def build_payload(variable_1, variable_2):
    value_1 = distance_1()
    value_2 = distance_2()
    payload = {variable_1: value_1, variable_2: value_2}
    return payload

    return payload

def post_request(payload):
    
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    return True

    # Kirim data ultrasonik
def send_data():
    payload = build_payload(VARIABLE_LABEL_1, VARIABLE_LABEL_2)
    post_request(payload)

def startTimer():
    threading.Timer(interval, startTimer).start()
    send_data()

def start_sending_data():
    while True:
        send_data()
        time.sleep(interval)

    # Deteksi logam
def detect_prox():
    while True:
        if GPIO.input(PIN_PROX) == 1:
            print("Besi tidak terdeteksi")
            time.sleep(1)
            set_servo_besi(65)
            time.sleep(0.1)
            GPIO.output(PIN_TRIGGER_1, GPIO.LOW)
            GPIO.output(PIN_TRIGGER_2, GPIO.LOW)

        else:
            set_servo_besi(130)
            time.sleep(3)
            print("Besi terdeteksi")
            GPIO.output(PIN_TRIGGER_1, GPIO.HIGH)
            GPIO.output(PIN_TRIGGER_2, GPIO.HIGH)

# Fungsi untuk deteksi PIN_PIR
def detect_pir():
    while True:
        if GPIO.input(PIN_PIR) == 1:

            GPIO.output(PIN_TRIGGER_1, GPIO.LOW)
            GPIO.output(PIN_TRIGGER_2, GPIO.LOW)

            print("Tangan terdeteksi")
            set_servo_pir(160)
            time.sleep(4)
            set_servo_pir(60)
            time.sleep(0.1)
            print("Opening door finished. Rotating non-metal servo...")
            set_servo_palang(0)
            time.sleep(2)
            set_servo_palang(60)
            print("Non-metal servo rotation finished.")
            time.sleep(2)
            GPIO.output(PIN_TRIGGER_1, GPIO.HIGH)
            GPIO.output(PIN_TRIGGER_2, GPIO.HIGH)
            
        else:
            print("Sepi")

if __name__ == '__main__':
    try:
        setup()

        data_thread = threading.Thread(target=start_sending_data)
        data_thread.start()

        # Buat thread-thread baru untuk deteksi
        prox_thread = threading.Thread(target=detect_prox)
        pir_thread = threading.Thread(target=detect_pir)
        ultrasonic_thread_1 = threading.Thread(target=distance_1, args=("Ultrasonic 1", PIN_ECHO_1, PIN_TRIGGER_1))
        ultrasonic_thread_2 = threading.Thread(target=distance_2, args=("Ultrasonic 2", PIN_ECHO_2, PIN_TRIGGER_2))
        
        # Mulai kedua thread
        prox_thread.start()
        pir_thread.start()
        ultrasonic_thread_1.start()
        ultrasonic_thread_2.start()

        # Tunggu thread-thread selesai sebelum keluar
        prox_thread.join()
        pir_thread.join()
        ultrasonic_thread_1.join()
        ultrasonic_thread_2.join()
        
    except KeyboardInterrupt:
        pass
    finally:
        # Berhenti dan bersihkan GPIO serta PWM
        pwm_besi.stop()
        pwm_palang.stop()
        pwm_pir.stop()
        data_thread.join() 
        GPIO.cleanup()
