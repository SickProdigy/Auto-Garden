import gc

class MemoryMonitor:
    """Monitor and display Pico W memory usage."""
    
    def __init__(self, interval=300):
        """
        Initialize memory monitor.
        
        Args:
            interval: Seconds between memory checks (default: 300 = 5 minutes)
        """
        self.interval = interval
        self.last_check = 0
        self.initial_free = None  # Track initial free memory
    
    def should_run(self, current_time):
        """Check if it's time to run memory check."""
        if current_time - self.last_check >= self.interval:
            self.last_check = current_time
            return True
        return False
    
    def run(self):
        """Check and display memory usage."""
        # Force garbage collection before checking
        gc.collect()
        
        # Get memory stats
        free = gc.mem_free()
        allocated = gc.mem_alloc()
        total = free + allocated
        
        # Store initial free memory on first run
        if self.initial_free is None:
            self.initial_free = free
        
        # Calculate memory leak (if any)
        leaked = self.initial_free - free if self.initial_free else 0
        
        # Print memory report
        print("\n" + "="*50)
        print("Pico W Memory (RAM):")
        print("="*50)
        print("Total:      {:.1f} KB".format(total / 1024))
        print("Used:       {:.1f} KB ({:.1f}%)".format(
            allocated / 1024, 
            (allocated/total)*100
        ))
        print("Free:       {:.1f} KB ({:.1f}%)".format(
            free / 1024,
            (free/total)*100
        ))
        
        # Show memory leak warning if detected
        if leaked > 5120:  # More than 5 KB leaked
            print("⚠️  Leaked:    {:.1f} KB since startup".format(leaked / 1024))
        
        print("="*50 + "\n")
        
        # Return memory info for other uses (like web server)
        return {
            'total_kb': total / 1024,
            'used_kb': allocated / 1024,
            'free_kb': free / 1024,
            'usage_percent': (allocated/total)*100,
            'leaked_kb': leaked / 1024 if leaked > 0 else 0
        }

def check_memory_once():
    """One-time memory check (for startup diagnostics)."""
    gc.collect()
    free = gc.mem_free()
    allocated = gc.mem_alloc()
    total = free + allocated
    
    print("\n" + "="*50)
    print("Startup Memory Check:")
    print("="*50)
    print("Total:      {:.1f} KB".format(total / 1024))
    print("Used:       {:.1f} KB ({:.1f}%)".format(
        allocated / 1024, 
        (allocated/total)*100
    ))
    print("Free:       {:.1f} KB ({:.1f}%)".format(
        free / 1024,
        (free/total)*100
    ))
    print("="*50 + "\n")
    
    return {
        'total_kb': total / 1024,
        'used_kb': allocated / 1024,
        'free_kb': free / 1024,
        'usage_percent': (allocated/total)*100
    }