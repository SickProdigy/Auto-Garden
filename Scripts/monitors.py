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
        self.alert_high = alert_high  # Alert if temp goes above this
        self.alert_low = alert_low    # Alert if temp goes below this
    
    def run(self):
        """Read all sensors and report temperatures."""
        temps = self.sensor.read_all_temps(unit='F')
        if not temps:
            print("No temperature readings available")
            return
        
        # Format message
        temp_msg = "🌡️ Temperature readings:\n"
        alerts = []
        
        for rom, temp in temps.items():
            sensor_id = rom.hex()[:8]
            temp_msg += f"Sensor {sensor_id}: {temp:.1f}°F\n"
            
            # Check alerts
            if self.alert_high and temp > self.alert_high:
                alerts.append(f"⚠️ Sensor {sensor_id} HIGH: {temp:.1f}°F (threshold: {self.alert_high}°F)")
            if self.alert_low and temp < self.alert_low:
                alerts.append(f"⚠️ Sensor {sensor_id} LOW: {temp:.1f}°F (threshold: {self.alert_low}°F)")
        
        # Send regular update
        send_discord_message(temp_msg.strip())
        
        # Send alerts separately
        for alert in alerts:
            send_discord_message(alert)

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