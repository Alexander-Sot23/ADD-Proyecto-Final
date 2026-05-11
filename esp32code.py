import dht
import machine
import network
import urequests
import time

SSID     = "Desktop-HP A"
PASSWORD = "CIDGAR23"

SERVER_URL = "http://10.225.231.122:5000/data"
CONFIG_URL = "http://10.225.231.122:5000/api/config"

sensor_pin = 4
led_pin    = 2

sensor = dht.DHT11(machine.Pin(sensor_pin))
led    = machine.Pin(led_pin, machine.Pin.OUT)

INTERVALO_SEGUNDOS = 30


def blink_led(times=2, delay=0.2):
    for _ in range(times):
        led.value(1)
        time.sleep(delay)
        led.value(0)
        time.sleep(delay)


def reset_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    time.sleep(0.5)
    return wlan


def connect_wifi():
    wlan = reset_wifi()

    if wlan.isconnected():
        print("Ya conectado. IP:", wlan.ifconfig()[0])
        return True

    print("Conectando a WiFi:", SSID)
    wlan.connect(SSID, PASSWORD)

    timeout = 25
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        print(".", end="")

    if wlan.isconnected():
        print("\n¡Conectado! IP:", wlan.ifconfig()[0])
        blink_led(3, 0.15)
        return True
    else:
        print("\nFallo en la conexión")
        blink_led(1, 0.8)
        return False


def send_data(temp, hum):
    try:
        payload  = {"temp": temp, "hum": hum}
        response = urequests.post(SERVER_URL, json=payload, timeout=10)

        if response.status_code == 200:
            print("Datos enviados correctamente")
            blink_led(2, 0.1)
            response.close()
            return True
        else:
            print("Error HTTP:", response.status_code)
            response.close()
            return False

    except Exception as e:
        print("Error enviando datos:", e)
        blink_led(1, 0.6)
        return False


def get_intervalo():
    try:
        r   = urequests.get(CONFIG_URL, timeout=5)
        cfg = r.json()
        r.close()
        return cfg.get('intervalo_segundos', INTERVALO_SEGUNDOS)
    except Exception as e:
        print("Error consultando config:", e)
        return INTERVALO_SEGUNDOS


def smart_sleep(segundos):
    elapsed = 0
    while elapsed < segundos:
        time.sleep(3)
        elapsed += 3
        nuevo = get_intervalo()
        if nuevo != segundos:
            print("Intervalo actualizado a", nuevo, "s")
            return


print("Iniciando ESP32 + DHT11 + LED...")
connect_wifi()
print("Iniciando bucle principal...")

while True:
    if not network.WLAN(network.STA_IF).isconnected():
        print("WiFi desconectado → Reconectando...")
        connect_wifi()

    try:
        sensor.measure()
        temp = sensor.temperature()
        hum  = sensor.humidity()

        print("Lectura → {:.1f}°C | {:.1f}%".format(temp, hum))
        send_data(temp, hum)

    except OSError as e:
        print("Error sensor:", e)
        blink_led(1, 0.8)
    except Exception as e:
        print("Error inesperado:", e)

    smart_sleep(get_intervalo())