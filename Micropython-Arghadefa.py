import network
import time
from machine import Pin
import dht
import urequests

# **1️⃣ Konfigurasi WiFi**
WIFI_SSID = "ZTE_AdRif_24Ghz"  # Ganti dengan WiFi Anda
WIFI_PASSWORD = "21604649"  # Ganti dengan password WiFi Anda

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Menghubungkan ke jaringan WiFi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print("Terhubung ke WiFi! IP:", wlan.ifconfig()[0])

connect_wifi(WIFI_SSID, WIFI_PASSWORD)

# **2️⃣ Konfigurasi URL API**
API_URL = "http://192.168.1.3:5000/sensor"  # Sesuaikan dengan Flask API

# **3️⃣ Konfigurasi Ubidots**
UBIDOTS_TOKEN = "BBUS-Pt4wOLLFAH6Jzc0bYcR2UD46AyUUFh"
DEVICE_LABEL = "arghadefa-device"
UBIDOTS_URL = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_LABEL
VARIABLE_TEMP = "Suhu"
VARIABLE_HUM = "Kelembapan"
VARIABLE_MOTION = "Jumlah_Pergerakan"

# **4️⃣ Inisialisasi Sensor**
dht_sensor = dht.DHT11(Pin(4))  
pir_sensor = Pin(5, Pin.IN)

motion_count = 0  
prev_motion = 0  

# **5️⃣ Fungsi untuk Mengirim ke MongoDB**
def send_to_mongodb(temp, hum, motion):
    payload = {
        "temperature": temp,
        "humidity": hum,
        "motion_count": motion
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = urequests.post(API_URL, json=payload, headers=headers)
        print("Data dikirim ke MongoDB:", response.text)
        response.close()
    except Exception as e:
        print("Gagal mengirim data ke MongoDB:", e)

# **6️⃣ Fungsi untuk Mengirim ke Ubidots**
def send_to_ubidots(temp, hum, motion):
    payload = {
        VARIABLE_TEMP: {"value": temp},
        VARIABLE_HUM: {"value": hum},
        VARIABLE_MOTION: {"value": motion}
    }
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": UBIDOTS_TOKEN
    }
    try:
        response = urequests.post(UBIDOTS_URL, json=payload, headers=headers)
        print("Data dikirim ke Ubidots:", response.text)
        response.close()
    except Exception as e:
        print("Gagal mengirim data ke Ubidots:", e)

# **7️⃣ Loop Utama**
while True:
    try:
        dht_sensor.measure()
        suhu = dht_sensor.temperature()
        kelembaban = dht_sensor.humidity()
        
        current_motion = pir_sensor.value()
        if current_motion == 1 and prev_motion == 0:
            motion_count += 1
        prev_motion = current_motion

        print(f"Suhu: {suhu}°C, Kelembaban: {kelembaban}%, Gerakan: {'Terdeteksi' if current_motion == 1 else 'Tidak ada'} (Total: {motion_count})")

        # **Kirim data ke MongoDB dan Ubidots**
        send_to_mongodb(suhu, kelembaban, motion_count)
        send_to_ubidots(suhu, kelembaban, motion_count)
        
    except OSError as e:
        print("Gagal membaca sensor:", e)
    
    time.sleep(3)  # Delay sebelum pembacaan berikutnya
