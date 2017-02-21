from umqtt.simple import MQTTClient
MQclient=MQTTClient('imptest123','broker.hivemq.com')
MQclient.connect()
topic='/TRUMPEEE'
from machine import Pin, I2C, ADC
import time
import machine
import math
import utime
ledpin = machine.Pin(2, machine.Pin.OUT) #define led output
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000) #initialise i2c bus
acceladdress=24 #set address of accelerometer
adc = machine.ADC(0) #initialise adc for microphone


def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('SSID', 'PASSWORD') #removed for security
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())


    # construct an I2C bus
    #normal grav value is about 259
def _recv_msg_callback(topic, msg): #set up callback
    if msg.decode("utf-8")=='on': #turn led on if commanded to 
        ledpin.low()
    elif msg.decode("utf-8")=='off':
        ledpin.high()
MQclient.set_callback(_recv_msg_callback) 
MQclient.subscribe('/TRUMPEEE/rec') #set up subscribe

    
def getregval(address, register):
    getregval_minibuf=bytearray([register]) 
    getregval_rubbish=i2c.writeto(address, getregval_minibuf) #write requested address
    getregval_retval=i2c.readfrom(address, 1) #read data at that address
    return getregval_retval; #return data



def allreadCont():
    allreadcount2=0
    buf = bytearray([0x20,0x77])    # 50Hz mode, all axis enabled 400HZ
    rubbish=i2c.writeto(acceladdress, buf)
    buf = bytearray([0x23,0x80])    # block data update
    rubbish=i2c.writeto(acceladdress, buf)
    cumulativeacc=0
    clear = "\n" * 100 #clear terminal if active
    maxadc=0
    lastacc=0
    adccount=0
    maxacc=0
    timeoffset=0
    while(1):  #to iterate between 10 to 20
        lowx=getregval(acceladdress, 0x28) #get low 2 bits
        highx=getregval(acceladdress, 0x29) #get high 6 bits
        highx=highx[0] #convert to integer values
        lowx=lowx[0]
        
        lowy=getregval(acceladdress, 0x2A)
        highy=getregval(acceladdress, 0x2B)
        highy=highy[0]
        lowy=lowy[0]
        
        lowz=getregval(acceladdress, 0x2C)
        highz=getregval(acceladdress, 0x2D)
        highz=highz[0] 
        lowz=lowz[0]
        totalx=(highx*4) + (lowx>>6) #convert from 16 bit to 10 bit
        totaly=(highy*4) + (lowy>>6)
        totalz=(highz*4) + (lowz>>6)
        if totalx>512: #roll over negative values
            totalx-=1024
        if totaly>512:
            totaly-=1024
        if totalz>512:
            totalz-=1024
        totalacc=totalx*totalx+totaly*totaly+totalz*totalz 
        totalacc=math.sqrt(totalacc) #get the total acceleration
        adjustedacc=abs(atotalacc-lastacc) #get the jerk

        
       # adjustedacc=abs(adjustedacc-259) #gravity correction
        if adjustedacc>10: #if jerk above threshold then record it
            cumulativeacc+=adjustedacc
            if adjustedacc>maxacc:
                maxacc=adjustedacc #record maximum jerk
        adcres=adc.read() #read microphone value
        if adcres>400: #if microphone above threshold
            adccount+=1
            if adcres>maxadc:
                maxadc=adcres
        allreadcount2+=1
        if allreadcount2>100:
            data1='{"avgacc":"' + str(cumulativeacc/256) + '", "ticks(ms)":"' + str(utime.ticks_ms()) + '", "maxacc":"'  + str(maxacc*100/256) + '", "Volume":"' + str(maxadc*100/1024) + '", "adccount":"' + str(adccount) + '"}'
            MQclient.publish(topic,bytes(data1,'utf-8')) #send data to mqtt
            allreadcount2=0
            cumulativeacc=0
            adccount=0
            maxadc=0
            maxacc=0
            MQclient.check_msg()
        lastacc=totalacc;
        time.sleep(0.01)


def adctest():
    adccheck=0;
    while(adccheck<700):
        adccheck=adc.read()
        time.sleep(0.01)
    print("test")
