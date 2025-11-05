import network
import time
from secrets import secrets

def connect_wifi(led=None):
    """Connect to WiFi using credentials from secrets.py"""
    try:
        wlan = network.WLAN(network.STA_IF)
        
        # Deactivate first if already active (fixes EPERM error)
        if wlan.active():
            wlan.active(False)
            time.sleep(1)
        
        wlan.active(True)
        time.sleep(1)  # Give it time to initialize
        
    except OSError as e:
        print(f"WiFi activation error: {e}")
        print("Attempting reset...")
        try:
            # Force deinit and reinit
            wlan.deinit()
            time.sleep(2)
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            time.sleep(1)
        except Exception as e2:
            print(f"WiFi reset failed: {e2}")
            return None
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        try:
            wlan.connect(secrets['ssid'], secrets['password'])
        except Exception as e:
            print(f"Connection attempt failed: {e}")
            return None
        
        # Wait for connection with timeout
        max_wait = 20
        while max_wait > 0:
            if wlan.isconnected():
                break
            if led:
                led.toggle()
            time.sleep(0.5)
            max_wait -= 1
            print('.', end='')
        
        print()
        
        if not wlan.isconnected():
            print('WiFi connection failed!')
            if led:
                led.off()
            return None
    
    if led:
        # Single pulse on successful connection
        led.on()
        time.sleep(0.5)
        led.off()
    
    print('Connected to WiFi')
    return wlan