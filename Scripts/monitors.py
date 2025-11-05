import time
from scripts.discord_webhook import send_discord_message
from scripts.temperature_sensor import TemperatureSensor

class Monitor:
    """Base class for all monitoring tasks."""
    def __init__(self, interval=300):
        """
        interval: seconds between checks
        """
        self.interval = interval
        self.last_check_ms = 0
    
    def should_run(self):
        """Check if enough time has passed to run again."""
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_check_ms) >= (self.interval * 1000):
            self.last_check_ms = now
            return True
        return False
    
    def run(self):
        """Override this in subclasses to implement monitoring logic."""
        pass

class TemperatureMonitor(Monitor):
    """Monitor temperature sensors and report to Discord."""
    def __init__(self, pin=10, interval=300, alert_high=None, alert_low=None):
        super().__init__(interval)
        self.sensor = TemperatureSensor(pin=pin)
        self.alert_high = alert_high
        self.alert_low = alert_low
    
    def run(self):
        """Read all sensors and report temperatures."""
        temps = self.sensor.read_all_temps(unit='F')
        if not temps:
            print("No temperature readings available")
            return
        
        temp_msg = "🌡️ Temperature readings:\n"
        alerts = []
        
        for rom, temp in temps.items():
            sensor_id = rom.hex()[:8]
            temp_msg += f"Sensor {sensor_id}: {temp:.1f}°F\n"
            
            if self.alert_high and temp > self.alert_high:
                alerts.append(f"⚠️ Sensor {sensor_id} HIGH: {temp:.1f}°F (threshold: {self.alert_high}°F)")
            if self.alert_low and temp < self.alert_low:
                alerts.append(f"⚠️ Sensor {sensor_id} LOW: {temp:.1f}°F (threshold: {self.alert_low}°F)")
        
        send_discord_message(temp_msg.strip())
        
        for alert in alerts:
            send_discord_message(alert)

class WiFiMonitor(Monitor):
    """Monitor WiFi connection and handle reconnection."""
    def __init__(self, wifi, led, interval=5, reconnect_cooldown=60):
        super().__init__(interval)
        self.wifi = wifi
        self.led = led
        self.reconnect_cooldown = reconnect_cooldown
        self.last_reconnect_attempt = 0
        self.was_connected = wifi.isconnected() if wifi else False
    
    def run(self):
        """Check WiFi status, blink LED, attempt reconnect if needed."""
        import network
        from scripts.networking import connect_wifi
        
        is_connected = self.wifi.isconnected() if self.wifi else False
        
        if not is_connected:
            # Fast blink when disconnected
            self.led.on()
            time.sleep(0.2)
            self.led.off()
            
            # Try reconnect if cooldown passed
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_reconnect_attempt) >= (self.reconnect_cooldown * 1000):
                self.last_reconnect_attempt = now
                print("Attempting WiFi reconnect...")
                self.wifi = connect_wifi(self.led)
                
                if self.wifi and self.wifi.isconnected():
                    send_discord_message("WiFi connection restored 🔄")
                    self.was_connected = True
        else:
            # Slow blink when connected
            self.led.on()
            time.sleep(1)
            self.led.off()
            
            # Notify if connection was just restored
            if not self.was_connected:
                send_discord_message("WiFi connection restored 🔄")
                self.was_connected = True

def run_monitors(monitors):
    """
    Run all monitors in the list, checking if each should run based on interval.
    Call this in your main loop.
    """
    for monitor in monitors:
        if monitor.should_run():
            try:
                monitor.run()
            except Exception as e:
                print(f"Error running monitor {monitor.__class__.__name__}: {e}")