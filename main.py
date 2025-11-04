from machine import Pin
from scripts.networking import connect_wifi, monitor_connection
from scripts.discord_webhook import send_discord_message

# Initialize pins (LED light onboard)
led = Pin("LED", Pin.OUT)
led.low()

# Connect to WiFi
wifi = connect_wifi(led)

# Send startup message if connected
if wifi and wifi.isconnected():
    send_discord_message("Pico W online and connected ✅")

# Define reconnect callback
def on_wifi_restored():
    send_discord_message("WiFi connection restored 🔄")

# Start connection monitoring loop (never returns)
monitor_connection(wifi, led, on_reconnect=on_wifi_restored)