import network
import time
from secrets import secrets

def connect_wifi(led=None, max_retries=3, timeout=20):
    """
    Connect to WiFi using credentials from secrets.py
    
    Args:
        led: Optional LED pin for visual feedback
        max_retries: Number of connection attempts (default: 3)
        timeout: Seconds to wait for connection per attempt (default: 20)
    
    Returns:
        WLAN object if connected, None if failed
    """
    wlan = network.WLAN(network.STA_IF)
    
    # Ensure clean state
    try:
        if wlan.active():
            wlan.active(False)
            time.sleep(1)
        
        wlan.active(True)
        time.sleep(1)
        
    except OSError as e:
        print(f"WiFi activation error: {e}")
        print("Attempting reset...")
        try:
            wlan.deinit()
            time.sleep(2)
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            time.sleep(1)
        except Exception as e2:
            print(f"WiFi reset failed: {e2}")
            return None
    
    # Try connecting with retries
    for attempt in range(1, max_retries + 1):
        if wlan.isconnected():
            print(f"Already connected to WiFi")
            break
        
        print(f'Connecting to WiFi (attempt {attempt}/{max_retries})...')
        
        try:
            wlan.connect(secrets['ssid'], secrets['password'])
        except Exception as e:
            print(f"Connection attempt failed: {e}")
            if attempt < max_retries:
                print("Retrying in 3 seconds...")
                time.sleep(3)
            continue
        
        # Wait for connection with timeout
        wait_time = 0
        while wait_time < timeout:
            if wlan.isconnected():
                break
            
            if led:
                led.toggle()
            
            time.sleep(0.5)
            wait_time += 0.5
            
            # Print progress dots every 2 seconds
            if int(wait_time * 2) % 4 == 0:
                print('.', end='')
        
        print()  # New line after dots
        
        if wlan.isconnected():
            break
        
        print(f'Connection attempt {attempt} failed')
        if attempt < max_retries:
            print("Retrying in 3 seconds...")
            time.sleep(3)
    
    # Final connection check
    if not wlan.isconnected():
        print('WiFi connection failed after all attempts!')
        if led:
            led.off()
        return None
    
    # Success feedback
    if led:
        # Double pulse on successful connection
        for _ in range(2):
            led.on()
            time.sleep(0.2)
            led.off()
            time.sleep(0.2)
    
    print('Connected to WiFi successfully!')
    
    # Print connection details
    ifconfig = wlan.ifconfig()
    print(f"IP: {ifconfig[0]} | Gateway: {ifconfig[2]}")
    
    return wlan