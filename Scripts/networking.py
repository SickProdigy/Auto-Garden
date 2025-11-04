import network
import time
from secrets import secrets

RECONNECT_COOLDOWN_MS = 60000  # 60 seconds

def connect_wifi(led=None, timeout=10):
    """
    Connect to WiFi using secrets['ssid'] / secrets['password'].
    If `led` (machine.Pin) is provided, pulse it once on successful connect.
    Returns the WLAN object or None on failure.
    """
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    
    print("Connecting to WiFi...", end="")
    wifi.connect(secrets['ssid'], secrets['password'])
    
    # Wait for connection with timeout
    max_wait = timeout
    while max_wait > 0:
        if wifi.status() < 0 or wifi.status() >= 3:
            break
        max_wait -= 1
        print(".", end="")
        time.sleep(1)
        
    if wifi.isconnected():
        print("\nConnected! Network config:", wifi.ifconfig())
        if led:
            led.on()
            time.sleep(1)
            led.off()
        return wifi
    else:
        print("\nConnection failed!")
        return None

def monitor_connection(wifi, led, on_reconnect=None, on_loop=None, loop_interval=60):
    """
    Monitor WiFi connection and attempt reconnects with cooldown.
    Blinks LED fast when disconnected, slow when connected.
    Calls on_reconnect() callback when connection is restored.
    Calls on_loop() callback every loop_interval seconds when connected.
    Never returns (infinite loop).
    """
    last_attempt_ms = time.ticks_ms()
    last_loop_ms = time.ticks_ms()
    
    while True:
        if not wifi or not wifi.isconnected():
            # Fast blink when disconnected
            led.on()
            time.sleep(0.2)
            led.off()
            time.sleep(0.2)

            # Only try to reconnect after cooldown
            if time.ticks_diff(time.ticks_ms(), last_attempt_ms) >= RECONNECT_COOLDOWN_MS:
                last_attempt_ms = time.ticks_ms()
                wifi = connect_wifi(led)
                # Notify when connection is restored
                if wifi and wifi.isconnected() and on_reconnect:
                    on_reconnect()

        else:
            # Slow blink when connected
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(1)
            
            # Call loop callback at interval
            if on_loop and time.ticks_diff(time.ticks_ms(), last_loop_ms) >= (loop_interval * 1000):
                last_loop_ms = time.ticks_ms()
                try:
                    on_loop()
                except Exception as e:
                    print(f"Error in loop callback: {e}")
        
        time.sleep(0.1)