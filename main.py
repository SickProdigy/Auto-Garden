from machine import Pin
import time
from scripts.networking import connect_wifi
from scripts.discord_webhook import send_discord_message
from scripts.monitors import TemperatureMonitor, WiFiMonitor, run_monitors

# Initialize pins (LED light onboard)
led = Pin("LED", Pin.OUT)
led.low()

# Connect to WiFi
wifi = connect_wifi(led)

# Send startup message if connected
if wifi and wifi.isconnected():
    send_discord_message("Pico W online and connected ✅")

# Set up monitors
monitors = [
    WiFiMonitor(wifi, led, interval=5, reconnect_cooldown=60),
    TemperatureMonitor(pin=10, interval=300, alert_high=85.0, alert_low=32.0),
    # Add more monitors here later:
    # SoilMoistureMonitor(pin=26, interval=600),
    # LightLevelMonitor(pin=27, interval=900),
]

# Main monitoring loop
while True:
    run_monitors(monitors)
    time.sleep(0.1)