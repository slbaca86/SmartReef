# Web application for Autonomous Reef Aquarium Web application

from flask import Flask, render_template
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import os
import glob
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

app = Flask(__name__)

# set up ds18b20 probe
os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string)/1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return round(temp_f, 2)
# end temp probe setup


inpins = {
    22: {"name": "input1", "state": "LOW"},
    23: {"name": "input2", "state": "LOW"},
    24: {"name": "input3", "state": "LOW"},
    25: {"name": "input4", "state": "LOW"},
}

outpins = {
    6: {"name": "output1", "state": "LOW"},
    12: {"name": "output2", "state": "LOW"},
    13: {"name": "output3", "state": "LOW"},
    16: {"name": "output4", "state": "LOW"},
    19: {"name": "motor1", "state": "LOW"},
    20: {"name": "motor2", "state": "LOW"},
    21: {"name": "motor3", "state": "LOW"},
    26: {"name": "motor4", "state": "LOW"},
}


for pin in inpins:
    GPIO.setup(pin, GPIO.IN)

for pin in outpins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


def checkpinstate():
    for pin in inpins:
        inpins[pin]["state"] = GPIO.input(pin)
    for pin in outpins:
        outpins[pin]['state'] = GPIO.input(pin)

def setchangedate():
    setdate = date.today() + relativedelta(days=-4)
    setdate
    return setdate

def waterlev():
    waterlevel = 2 - GPIO.input(22) - GPIO.input(23)
    waterlevel = [waterlevel]
    return waterlevel


def tillWater():
    setdate = setchangedate()
    twoweeks = setdate + relativedelta(days=+14)
    tilltime = abs(twoweeks - (setdate))
    percentleft = (tilltime.days/float(14))*100
    return int(percentleft)

@app.route('/')
def initial():

    checkpinstate()


    if GPIO.input(19):
        checklights = "unchecked"
        light = "OFF"
    else:
        checklights = "checked"
        light = "ON"

    if outpins[16]['state'] == 1:
        mainpumpstat = "ON"
        checkpumpmain = "checked"
    else:
        mainpumpstat = "OFF"
        checkpumpmain = 'unchecked'

    if outpins[12]['state'] == 1:
        inpumpstat = "ON"
        checkpumpin = "checked"
    else:
        inpumpstat = "OFF"
        checkpumpin = 'unchecked'

    if outpins[13]['state'] == 1:
        atopumpstat = "ON"
        checkpumpato = "checked"
    else:
        atopumpstat = "OFF"
        checkpumpato = 'unchecked'

    if outpins[6]['state'] == 1:
        outpumpstat = "ON"
        checkpumpout = "checked"
    else:
        outpumpstat = "OFF"
        checkpumpout = 'unchecked'

    


    tillwater = tillWater()
    temp = read_temp()
    waterLevel = waterlev()
    templateData = {
        'pumpstatmain': mainpumpstat,
        'pumpstatin': inpumpstat,
        'pumpstatout': outpumpstat,
        'pumpstatato': atopumpstat,
        'buttonstate': 'OFF',
        'temp': temp,
        'lights': light,
        'waterchange': tillwater,
        'time': '12:30',
        'checklights': checklights,
        'labels': ["waterLevel"],
        'values': waterLevel,
        'checkpumpmain': checkpumpmain,
        'checkpumpin': checkpumpin,
        'checkpumpato': checkpumpato,
        'checkpumpout': checkpumpout,
        'tests': ["Ammonia", "Nitrite", "Nitrate", 'PH'],
        'testvalues': [.25, .5, 5, 8.1],
        }

    return render_template('testpage.html', **templateData)


@app.route('/toggle/<pin>')
def togglepin(pin):
    pin = int(pin)
    GPIO.output(pin, not GPIO.input(pin))

    templateData = {
    'testvalues': [.5, 3, 0, 7.8],
    }

    return render_template('testpage.html', **templateData)


@app.route('/pinstatus')
def statuscheck():
    checkpinstate()
    templateData = {
        'outpins': outpins,
        'inpins' : inpins
    }

    return render_template('pinstatus.html', **templateData)



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
