from machine import Pin
import time
from scripts.networking import connect_wifi
from scripts.discord_webhook import send_discord_message
from scripts.monitors import TemperatureMonitor, WiFiMonitor, run_monitors
from scripts.temperature_sensor import get_configured_sensors, SENSOR_CONFIG

# Initialize pins (LED light onboard)
led = Pin("LED", Pin.OUT)
led.low()

# Connect to WiFi
wifi = connect_wifi(led)

# Send startup message if connected
if wifi and wifi.isconnected():
    send_discord_message("Pico W online and connected ✅")

# Get configured sensors
sensors = get_configured_sensors()

# Set up monitors
monitors = [
    WiFiMonitor(wifi, led, interval=5, reconnect_cooldown=60),
]

# Add temperature monitors from config
for key, sensor in sensors.items():
    config = SENSOR_CONFIG[key]
    
    # Inside temp alerts go to separate channel
    send_to_alert_channel = (key == 'inside')
    
    monitors.append(
        TemperatureMonitor(
            sensor=sensor,
            label=config['label'],
            check_interval=10,      # Check temp every 10 seconds
            report_interval=30,     # Report/log every 30 seconds
            alert_high=config['alert_high'],
            alert_low=config['alert_low'],
            log_file="/temp_logs.csv",
            send_alerts_to_separate_channel=send_to_alert_channel
        )
    )

# Main monitoring loop
while True:
    run_monitors(monitors)
    time.sleep(0.1)