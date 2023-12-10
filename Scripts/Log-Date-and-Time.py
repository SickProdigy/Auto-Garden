import machine
import utime

sensor_temp = machine.ADC(machine.ADC.CORE_TEMP)
conversion_factor = 3.3 / (65535)

led_onboard = machine.Pin(25, machine.Pin.OUT)
led_onboard.value(0)

rtc=machine.RTC()

file = open("temps.txt", "w")
#file = open("temps.txt", "a") # To append to log file rather than overwrite

while True:
    reading = sensor_temp.read_u16() * conversion_factor
    timestamp=rtc.datetime()
    temperature = 27 - (reading - 0.706)/0.001721

    timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] +
                                                timestamp[4:7])
    file.write(timestring + "," + str(temperature) + "\n")
    file.flush()
    led_onboard.value(1)
    utime.sleep(0.01)
    led_onboard.value(0)

    utime.sleep(30)

# Notes
# Given that space is at a premium when writing logs to files on the 
# internal Flash, one option may be produce timestamps and then deltas or 
# changes after that, forcing a full timestamp every so often to ensure 
# things are synchronised
