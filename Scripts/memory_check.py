import gc

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