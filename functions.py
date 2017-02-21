def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('BTHub6-FZ7Z', 'UbLqLCeUT7JE')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

from umqtt.simple import MQTTClient
MQclient=MQTTClient('imptest123','broker.hivemq.com')
MQclient.connect()
topic='/TRUMPEEE'
from machine import Pin, I2C, ADC
import time
import machine
import math
import utime
ledpin = machine.Pin(2, machine.Pin.OUT)
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
acceladdress=24
adc = machine.ADC(0)
    # construct an I2C bus
    #normal grav value is about 259
def _recv_msg_callback(topic, msg):
    if msg.decode("utf-8")=='on':
        ledpin.low()
    elif msg.decode("utf-8")=='off':
        ledpin.high()
MQclient.set_callback(_recv_msg_callback)
MQclient.subscribe('/TRUMPEEE/rec')

    
def getregval(address, register):
    getregval_minibuf=bytearray([register])
    getregval_rubbish=i2c.writeto(address, getregval_minibuf) #get low x
    getregval_retval=i2c.readfrom(address, 1)
    return getregval_retval;



def allreadCont():
    allreadcount2=0
    buf = bytearray([0x20,0x77])    # 50Hz mode, all axis enabled 0x7X 400HZ
    rubbish=i2c.writeto(acceladdress, buf)
    buf = bytearray([0x23,0x80])    # block data update
    rubbish=i2c.writeto(acceladdress, buf)
    cumulativeacc=0
    clear = "\n" * 100
    maxadc=0
    lastacc=0
    adccount=0
    maxacc=0
    while(1):  #to iterate between 10 to 20
        lowx=getregval(acceladdress, 0x28)
        highx=getregval(acceladdress, 0x29)
        highx=highx[0]
        lowx=lowx[0]
        
        lowy=getregval(acceladdress, 0x2A)
        highy=getregval(acceladdress, 0x2B)
        highy=highy[0]
        lowy=lowy[0]
        
        lowz=getregval(acceladdress, 0x2C)
        highz=getregval(acceladdress, 0x2D)
        highz=highz[0]
        lowz=lowz[0]
        totalx=(highx*4) + (lowx>>6)
        totaly=(highy*4) + (lowy>>6)
        totalz=(highz*4) + (lowz>>6)
        if totalx>512:
            totalx-=1024
        if totaly>512:
            totaly-=1024
        if totalz>512:
            totalz-=1024
        adjx=totalx
        adjy=totaly
        adjz=totalz
        totalacc=adjx*adjx+adjy*adjy+adjz*adjz 
        totalacc=math.sqrt(totalacc)
        adjustedacc=totalacc-lastacc
        #lastx=totalx
       #lasty=totaly
        #lastz=totalz

        
        adjustedacc=abs(adjustedacc)#-259)
        if adjustedacc>10:
            cumulativeacc+=adjustedacc
            if adjustedacc>maxacc:
                maxacc=adjustedacc
        adcres=adc.read()
        if adcres>400:
            adccount+=1
            if adcres>maxadc:
                maxadc=adcres
        allreadcount2+=1
        if allreadcount2>100:
            data1='{"avgacc":"' + str(cumulativeacc/256) + '", "ticks(ms)":"' + str(utime.ticks_ms()) + '", "maxacc":"'  + str(maxacc*100/256) + '", "Volume":"' + str(maxadc*100/1024) + '", "adccount":"' + str(adccount) + '"}'
            MQclient.publish(topic,bytes(data1,'utf-8'))
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
    print("plap")
