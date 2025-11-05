from machine import Pin
import time
import network

# Initialize pins (LED light onboard)
led = Pin("LED", Pin.OUT)
led.low()

# Hard reset WiFi interface before connecting
print("Initializing WiFi...")
try:
    wlan = network.WLAN(network.STA_IF)
    wlan.deinit()
    time.sleep(2)
    print("WiFi interface reset complete")
except Exception as e:
    print(f"WiFi reset warning: {e}")

# Import after WiFi reset
from scripts.networking import connect_wifi
from scripts.discord_webhook import send_discord_message
from scripts.monitors import TemperatureMonitor, WiFiMonitor, ACMonitor, HeaterMonitor, run_monitors
from scripts.temperature_sensor import TemperatureSensor
from scripts.air_conditioning import ACController
from scripts.heating import HeaterController
from scripts.web_server import TempWebServer

# Connect to WiFi
wifi = connect_wifi(led)

# Print WiFi details
if wifi and wifi.isconnected():
    ifconfig = wifi.ifconfig()
    print("\n" + "="*50)
    print("WiFi Connected Successfully!")
    print("="*50)
    print(f"IP Address:     {ifconfig[0]}")
    print(f"Subnet Mask:    {ifconfig[1]}")
    print(f"Gateway:        {ifconfig[2]}")
    print(f"DNS Server:     {ifconfig[3]}")
    print(f"Web Interface:  http://{ifconfig[0]}")
    print("="*50 + "\n")
    
    # Send startup message
    send_discord_message("Pico W online and connected ✅")
else:
    print("\n" + "="*50)
    print("WiFi Connection Failed!")
    print("="*50 + "\n")

# Start web server
web_server = TempWebServer(port=80)
web_server.start()

# Sensor configuration registry (moved from temperature_sensor.py)
SENSOR_CONFIG = {
    'inside': {
        'pin': 10,
        'label': 'Inside',
        'alert_high': 80.0,
        'alert_low': 70.0
    },
    'outside': {
        'pin': 11,
        'label': 'Outside',
        'alert_high': 85.0,
        'alert_low': 68.0
    }
}

# Initialize sensors based on configuration
def get_configured_sensors():
    """Return dictionary of configured sensor instances."""
    sensors = {}
    for key, config in SENSOR_CONFIG.items():
        sensors[key] = TemperatureSensor(pin=config['pin'], label=config['label'])
    return sensors

# Get configured sensors
sensors = get_configured_sensors()

# AC Controller options
ac_controller = ACController(
    relay_pin=15,
    min_run_time=30,   # min run time in seconds
    min_off_time=5     # min off time in seconds
)

ac_monitor = ACMonitor(
    ac_controller=ac_controller,
    temp_sensor=sensors['inside'],
    target_temp=77.0,   # target temperature in Fahrenheit
    temp_swing=1.0,     # temp swing target_temp-temp_swing to target_temp+temp_swing
    interval=30         # check temp every x seconds
)

# Heater Controller options
heater_controller = HeaterController(
    relay_pin=16,
    min_run_time=30,   # min run time in seconds
    min_off_time=5     # min off time in seconds
)

heater_monitor = HeaterMonitor(
    heater_controller=heater_controller,
    temp_sensor=sensors['inside'],
    target_temp=80.0,   # target temperature in Fahrenheit
    temp_swing=2.0,     # temp swing
    interval=30         # check temp every x seconds
)

# Set up monitors
monitors = [
    WiFiMonitor(wifi, led, interval=5, reconnect_cooldown=60), # Wifi monitor, Check WiFi every 5s
    ac_monitor, # AC monitor
    heater_monitor, # Heater monitor
    TemperatureMonitor( # Inside temperature monitor
        sensor=sensors['inside'],
        label=SENSOR_CONFIG['inside']['label'],
        check_interval=10,      # Check temp every 10 seconds
        report_interval=30,     # Report/log every 30 seconds
        alert_high=SENSOR_CONFIG['inside']['alert_high'],
        alert_low=SENSOR_CONFIG['inside']['alert_low'],
        log_file="/temp_logs.csv",
        send_alerts_to_separate_channel=True
    ),
    TemperatureMonitor( # Outside temperature monitor
        sensor=sensors['outside'],
        label=SENSOR_CONFIG['outside']['label'],
        check_interval=10,      # Check temp every 10 seconds
        report_interval=30,     # Report/log every 30 seconds
        alert_high=SENSOR_CONFIG['outside']['alert_high'],
        alert_low=SENSOR_CONFIG['outside']['alert_low'],
        log_file="/temp_logs.csv",
        send_alerts_to_separate_channel=False
    ),
]

print("Starting monitoring loop...")
print("Press Ctrl+C to stop\n")

# Main monitoring loop
while True:
    run_monitors(monitors)
    web_server.check_requests(sensors, ac_monitor, heater_monitor)
    time.sleep(0.1)