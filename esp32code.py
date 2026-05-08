import dht
import machine
import network
import urequests
import time

# ================== CONFIGURACIÓN DE RED ==================
SSID = "SSID" 
PASSWORD = "PASSWORD"

# IP de la computadora
SERVER_URL = "http://192.168.137.1:5000/data"

sensor_pin = 4
led_pin = 2

sensor = dht.DHT11(machine.Pin(sensor_pin))
led = machine.Pin(led_pin, machine.Pin.OUT)

INTERVALO_SEGUNDOS = 15
# ===================================================

def blink_led(times=2, delay=0.2):
    """Parpadea el LED para indicar actividad"""
    for _ in range(times):
        led.value(1)
        time.sleep(delay)
        led.value(0)
        time.sleep(delay)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        return True
    
    print("Conectando a WiFi:", SSID)
    wlan.connect(SSID, PASSWORD)
    
    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        print(".", end="")
    
    if wlan.isconnected():
        print("\n¡Conectado! IP:", wlan.ifconfig()[0])
        blink_led(3, 0.1)        # Parpadeo rápido = conectado
        return True
    else:
        print("\nNo se pudo conectar")
        return False

def send_data(temp, hum):
    try:
        payload = {"temp": temp, "hum": hum}
        response = urequests.post(SERVER_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("Enviado correctamente")
            blink_led(2, 0.1)      # Parpadeo = datos enviados OK
            response.close()
            return True
        else:
            print("Error HTTP:", response.status_code)
            response.close()
            return False
            
    except Exception as e:
        print("Error enviando datos:", e)
        blink_led(1, 0.5)          # Parpadeo lento = error
        return False

# ====================== INICIO ======================
print("Iniciando ESP32-S3 + DHT11 + LED...")

# Primer intento de conexión
if not connect_wifi():
    print("Intentando reconectar más tarde...")

print("Iniciando bucle principal...")

while True:
    # Verificar y reconectar WiFi si es necesario
    if not network.WLAN(network.STA_IF).isconnected():
        print("WiFi perdido. Reconectando...")
        connect_wifi()
    
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        
        print(f"Lectura → {temp:.1f}°C | {hum:.1f}%")
        send_data(temp, hum)
        
    except OSError as e:
        print("Error sensor:", e)
        blink_led(1, 0.8)   # Parpadeo largo = error sensor
    except Exception as e:
        print("Error inesperado:", e)
    
    time.sleep(INTERVALO_SEGUNDOS)
