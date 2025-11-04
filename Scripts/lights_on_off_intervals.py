import machine
led = machine.Pin("LED", machine.Pin.OUT)
led.off() # Make sure off
led.on() # Turn on last command, stays on

contactorV12 = Pin(12, Pin.OUT)

contactorV12.off()
contactorV12.on()