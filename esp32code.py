import dht
import machine
import network
import urequests
import time

# ================== CONFIGURACIÓN DE RED ==================
SSID = "SSID_WIFI" 
PASSWORD = "CONTRASEÑA"

# IP de la computadora
SERVER_URL = "http://192.168.1.XXX:5000/data"

# Configuracion del sensor DHT11
sensor_pin = 4
sensor = dht.DHT11(machine.Pin(sensor_pin))

# Tiempo entre lecturas
INTERVALO_SEGUNDOS = 30

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Ya conectado. IP:", wlan.ifconfig()[0])
        return True
    
    print("Conectando a WiFi...")
    wlan.connect(SSID, PASSWORD)
    
    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        print(".", end="")
    
    if wlan.isconnected():
        print("\n¡Conectado! IP:", wlan.ifconfig()[0])
        return True
    else:
        print("\nNo se pudo conectar al WiFi")
        return False

def send_data(temp, hum):
    try:
        payload = {"temp": temp, "hum": hum}
        response = urequests.post(
            SERVER_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print("Datos enviados → {:.1f}°C | {:.1f}% → Código: {}".format(
            temp, hum, response.status_code))
        response.close()
        return True
    except Exception as e:
        print("Error al enviar datos:", e)
        return False
    

# ====================== INICIO ======================
print("Iniciando sistema con DHT11...")

if connect_wifi():
    print("Iniciando bucle de lecturas cada {} segundos...".format(INTERVALO_SEGUNDOS))
    
    while True:
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            
            print("Lectura exitosa → Temp: {:.1f}°C | Hum: {:.1f}%".format(temp, hum))
            send_data(temp, hum)
            
        except OSError as e:
            print("Error leyendo el sensor DHT11 (intento en próximo ciclo):", e)
        except Exception as e:
            print("Error inesperado:", e)
        
        time.sleep(INTERVALO_SEGUNDOS)
else:
    print("Sin conexión WiFi. Reinicia la ESP32.")