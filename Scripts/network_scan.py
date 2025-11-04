import network
import time

def scan_networks(timeout=10):
    """
    Scan for available WiFi networks and return formatted results.
    Returns list of dicts with network info.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Scanning for networks...")
    networks = wlan.scan()
    
    # Format results
    results = []
    for net in networks:
        ssid, bssid, channel, rssi, security, hidden = net
        
        # Decode SSID if bytes
        if isinstance(ssid, bytes):
            ssid = ssid.decode('utf-8')
        
        # Security type mapping
        security_types = {
            0: "Open",
            1: "WEP",
            2: "WPA-PSK",
            3: "WPA2-PSK",
            4: "WPA/WPA2-PSK"
        }
        
        results.append({
            "ssid": ssid,
            "bssid": ":".join(["%02X" % b for b in bssid]),
            "channel": channel,
            "rssi": rssi,
            "security": security_types.get(security, "Unknown"),
            "hidden": bool(hidden)
        })
    
    # Sort by signal strength (strongest first)
    results.sort(key=lambda x: x["rssi"], reverse=True)
    
    return results

def print_networks(networks):
    """Pretty print network scan results."""
    print("\n" + "="*70)
    print(f"Found {len(networks)} networks:")
    print("="*70)
    
    for i, net in enumerate(networks, 1):
        print(f"\n{i}. {net['ssid']}")
        print(f"   BSSID: {net['bssid']}")
        print(f"   Channel: {net['channel']}")
        print(f"   Signal: {net['rssi']} dBm")
        print(f"   Security: {net['security']}")
        if net['hidden']:
            print(f"   (Hidden Network)")
    
    print("\n" + "="*70)

def find_network(ssid):
    """Find a specific network by SSID."""
    networks = scan_networks()
    for net in networks:
        if net['ssid'] == ssid:
            return net
    return None

# Run scan if executed directly
if __name__ == "__main__":
    networks = scan_networks()
    print_networks(networks)
