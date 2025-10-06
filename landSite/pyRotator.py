from flask import Flask, request, render_template, Response, jsonify
from flask_table import Table, Col, ButtonCol
from pyorbital.orbital import Orbital
from pyorbital import tlefile
from datetime import datetime, timezone, timedelta
import sys
import glob
import serial
import threading
import time
import requests
from math import asin, sin, cos, atan2, pi, degrees, radians
from typing import Tuple

step = 1       # шаг в ручном сопровождении
XYmode = True  # вид ОПУ
connectToCom=False # подключение к com порту
baudrate = 115200  # скорость com порта
tle='tle.txt'      # место сохранения tle

global lat, lon, alt, horizon, Mh, length
lon=49.207387
lat=55.927041
alt=165
length=24
az=0
el=0
curAz=0
curEl=0
# h=0
sats=['METEOR M2-2', 'METEOR M2-3', 'METEOR M2-4', 'NOAA-18', 'NOAA-19', 'NOAA-15', 'METOP-B', 'METOP-C']
sat=sats[0]
tracking=False

try:
    p = requests.get('http://r4uab.ru/satonline.txt')
    out = open(tle, "wb")
    out.write(p.content)
    out.close()
    print('TLE loaded')
except:
    print('TLE can`t be loaded')

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def AE2XY(azimuth: float, elevation: float) -> Tuple[float, float]:
    x = asin(sin(azimuth) * cos(elevation))
    y = -atan2(cos(azimuth) * cos(elevation), sin(elevation))
    
    return (x, y)

def XY2AE(x: float, y: float) -> Tuple[float, float]:
    x0 = sin(x)
    y0 = -sin(y)*cos(x)
    z0 = cos(y)*cos(x)
    
    el = asin(z0)
    az = - atan2(y0, x0)    
    
    return pi/2 + az, el

def getPosition():
    ser.write(b"AZ EL")
    try:
        resp=ser.readline().decode('ascii')
        space=resp.find(' ') # format: AZ XX.xxx EL XX.xxx
        x=float(resp[2:space])
        y=float(resp[space+3:len(resp)-1])

        if XYmode:
            x = radians(x)
            y = radians(y)
            az, el = XY2AE(x, y)

            az = degrees(az)
            el = degrees(el)
        else:
            az=x
            el=y
    except:
        pass

    if az<0: az=az+360
    return (az, el)

def setPosition(az, el):
    if XYmode:
        az = radians(az)
        el = radians(el)
        x, y = AE2XY(az, el)

        x = degrees(x)
        y = degrees(y)
    else:
        x=az
        y=el

    resp = 'AZ'+'{:.3f}'.format(round(x,3))+' EL'+'{:.3f}'.format(round(y,3))+'\n'
    ser.write(resp.encode('ascii'))

def search(ports):
    global ser
    for port in ports:
        ser = serial.Serial(port)
        ser.baudrate = baudrate
        ser.timeout = 2
        time.sleep(2)
        print('trying',port)
        ser.write(b"AZ EL")

        try:
            resp=ser.readline().decode('ascii')
            print('ans:',resp[:len(resp)-1])
        except:
            resp=''

        if resp.rfind('AZ')!=-1:
            print('connected to',port)
            ser.timeout = 5
            break
        ser.close()

def comm():
    global ser, sat, tracking, curAz, curEl, az, el
    while True:
        curAz, curEl = getPosition()
        if tracking==True and el>=0:
            now = datetime.now()
            utc = now-timedelta(hours=3)
            orbital = Orbital(sat, tle_file=tle)
            az, el=orbital.get_observer_look(utc, lon, lat, alt)
            setPosition(az, el)
            # print(az,el)
        elif tracking =='home':
            az, el = (0,90)
            setPosition(az, el)
        elif tracking =='man':
            setPosition(az, el)
        elif tracking =='cal':
            tracking=False
            ser.write('calibration'.encode('ascii'))


        time.sleep(0.5)


def raschot(utc_time, lon, lat, alt, horizon, mH, length):
    i=0
    n=0
    a=[]
    sats=['METEOR M2-3', 'METEOR M2-4', 'NOAA-18', 'NOAA-19', 'METOP-B', 'METOP-C']
    orbital = Orbital('METEOR M2-3', tle_file=tle)
    passTimes=orbital.get_next_passes(utc_time, length, lon, lat, alt, tol=0.0001, horizon=horizon)
    while i<len(sats):
        sat=sats[i]
        orbital = Orbital(sat, tle_file=tle)
        passTimes=orbital.get_next_passes(utc_time, length, lon, lat, alt, tol=0.0001, horizon=horizon)
        print(sat,i)
        while n<len(passTimes):
            if len(passTimes)!=0:
                time = passTimes[n][0]
                time1 = passTimes[n][1]
                time2 = passTimes[n][2]
                az,h=orbital.get_observer_look(time, lon, lat, alt)
                az,h1=orbital.get_observer_look(time1, lon, lat, alt)
                az,h2=orbital.get_observer_look(time2, lon, lat, alt)
                print(sat, passTimes[n][0].strftime('%Y.%m.%d %H:%M'))
                h=str('{:.2f}'.format(round(h,2)))
                h1=str('{:.2f}'.format(round(h1,2)))
                h2=str('{:.2f}'.format(round(h2,2)))
                a.append(dict(name=sat, timeUp=passTimes[n][0].strftime('%Y.%m.%d %H:%M:%S'), hUp=h, timeMax=passTimes[n][2].strftime('%Y.%m.%d %H:%M:%S'), hMax=h2, timeSet=passTimes[n][1].strftime('%Y.%m.%d %H:%M:%S'), hSet=h, lon=lon, lat=lat, alt=alt, horizon=horizon, button='button', button1='button1'))
            n+=1
        n=0
        i+=1
    n=0
    passes = sortByDate(a)
    # passes = crossPass(passes, lon, lat, alt, horizon)
    passes = clealMaxEl(passes, mH)
    return passes

def clealMaxEl(passlist, maxEl):
    n=0
    while n<len(passlist):
        h=float(passlist[n].get('hMax'))
        if h<maxEl:
            # print('pop',passlist[n],h,'<',maxEl,n)
            passlist.pop(n)
            # print()
            n-=1
        else:
            pass# print(passlist[n],h,maxEl,n)
        n+=1
    return passlist

def crossPass(passlist, lon, lat, alt, horizon):
    for i in range(len(passlist)):  
        if passlist[i].get('timeUp')<passlist[i-1].get('timeSet') and i>0:
            time=passlist[i-1].get('timeSet')
            time = datetime.strptime(time, '%Y.%m.%d %H:%M:%S')
            # time+=timedelta(seconds=1)
            sat=passlist[i].get('name')
            timeUp=passlist[i].get('timeUp')
            timeMax=passlist[i].get('timeMax')
            h2=passlist[i].get('hMax')
            timeSet=passlist[i].get('timeSet')
            h1=passlist[i].get('hSet')
            orbital = Orbital(sat, tle_file=tle)
            az,h=orbital.get_observer_look(time, lon, lat, alt)
            h=str('{:.2f}'.format(round(h,2)))
            passlist[i]=(dict(name=sat, timeUp=time.strftime('%Y.%m.%d %H:%M:%S'), hUp=h, timeMax=timeMax, hMax=h2, timeSet=timeSet, hSet=h1, lon=lon, lat=lat, alt=alt, horizon=horizon, button='button'))
            print('пересекаются',time,timeUp,sat,h)
    return passlist

def tra(sat, time, lon, lat, alt, horizon, isjson):
    i=0
    str=''
    orbital = Orbital(sat, tle_file=tle)
    az,h=orbital.get_observer_look(time, lon, lat, alt)
    if h<horizon:
        while h<horizon:
            time+=timedelta(seconds=1)
            az,h=orbital.get_observer_look(time, lon, lat, alt)
            # print(sat, time, lon, lat, alt, horizon, h)
    if isjson:
        trajectory=[]
        while h>=horizon:
            time+=timedelta(seconds=1)
            az,h=orbital.get_observer_look(time, lon, lat, alt)
            trajectory.append(dict(x=round(az,1), y=round(h,1)))
        return trajectory
    else:
        if h>=horizon:
            str+='Satellite '+sat
            str+='Start date & time '+time.strftime('%Y.%m.%d %H:%M:%S')
            str+='\n\r'
            str+='Time (UTC) Azimuth Elevation'
            str+='\n\r'
            az,h=orbital.get_observer_look(time, lon, lat, alt)
            print('Satellite ', sat, time.strftime('%H:%M:%S'), round(az,2), round(h,2))
            str+=time.strftime('%H:%M:%S')+' '+'{:.2f}'.format(round(az,2))+' '+'{:.2f}'.format(round(h,2))+'\n'    
        while h>=horizon:
            time+=timedelta(seconds=1)
            az,h=orbital.get_observer_look(time, lon, lat, alt)
            str+=time.strftime('%H:%M:%S')+' '+'{:.2f}'.format(round(az,2))+' '+'{:.2f}'.format(round(h,2))+'\n'
            # print('az', round(az,3), 'el', round(h,3))
        return str

def sortByDate(a):
    def strToDate(dstring):
        date_string=dstring.get('timeUp')
        return datetime.strptime(date_string, '%Y.%m.%d %H:%M:%S')
    return sorted(a, key=strToDate)

if connectToCom:
    ports=serial_ports()
    print(ports)

    search(ports)

    while ports==[] or ser.isOpen() == False:
        print('Connnect rotator!!!')
        ports=serial_ports()
        print(ports)
        search(ports)
        time.sleep(1)
        # raise Error

t1 = threading.Thread(target=comm)
t1.start()

class ItemTable(Table):
    name = Col('Спутник')
    timeUp = Col('AOS')
    timeSet = Col('LOS')
    hMax = Col('El')
    # button=ButtonCol('Скачать', endpoint='download', url_kwargs=dict(name='name',timeUp='timeUp',lon='lon',lat='lat',alt='alt',horizon='horizon'))
    button1=ButtonCol('Траектория', endpoint='view', url_kwargs=dict(name='name',timeUp='timeUp',lon='lon',lat='lat',alt='alt',horizon='horizon'))

    def get_tr_attrs(self, item):
        return {'class': 'trclass'}

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def main():
    return render_template('main.html')

@app.route('/control/', methods=['GET','POST'])
def ctrl():
    global sats
    return render_template('control.html',sats=sats)

@app.route('/track/', methods=['GET','POST'])
def track():
    global sat, tracking, az, el
    if request.method == 'POST':
        if request.json.get('sat')!=None: 
            sat = request.json.get('sat')

        if request.json.get('track')!=None:
            tracking = request.json.get('track')

        if tracking=='man':
            if request.json.get('dir')=='AZincr':
                az=az+step
            elif request.json.get('dir')=='AZdecr':
                az=az-step
            elif request.json.get('dir')=='ELincr':
                el=el+step
            elif request.json.get('dir')=='ELdecr' and el>0:
                el=el-step
        print(tracking)
        
        return '200'

@app.route('/nextsat/', methods=['GET','POST'])
def predict():
    now = datetime.now()
    utc=now-timedelta(hours=3)

    satlist=raschot(utc, lon, lat, alt, 0, 10, 5)
    if len(satlist)!=0:
        global ifnsat
        global nextsat
        nextsat=satlist[0].get('name')
        sat=nextsat

        nexttime=satlist[0].get('timeUp')
        nexttime=datetime.strptime(nexttime, '%Y.%m.%d %H:%M:%S')
        strnexttime=nexttime+timedelta(hours=3)
        strnexttime=strnexttime.strftime('%H:%M:%S')
        ifnsat=True
        print(strnexttime,sat)
    else:
        # global ifnsat
        ifnsat=False
        print('no passes for 5 hours')

    pos={'nextsat':nextsat,'nexttime':strnexttime}
    return jsonify({'pos': pos})

@app.route('/json/', methods=['GET','POST'])
def json():
    global tracking, az, el
    now = datetime.now()
    utc=now-timedelta(hours=3)

    pos={'sat':sat,'az':'{:.3f}'.format(round(az,3)),'el':'{:.3f}'.format(round(el,3)),'time':utc.strftime('%Y.%m.%d %H:%M:%S'),
         'curAz':'{:.3f}'.format(round(curAz,3)),
         'curEl':'{:.3f}'.format(round(curEl,3))}
    return jsonify({'pos': pos})

@app.route('/save/', methods=['POST'])
def save():
    global lat, lon, alt, horizon, Mh
    if request.json.get('lat')!='': lat = float(request.json.get('lat')) 
    if request.json.get('lon')!='': lon = float(request.json.get('lon'))

    if request.json.get('alt')!='': alt = float(request.json.get('alt'))
    if request.json.get('hor')!='': horizon = float(request.json.get('hor'))
    if request.json.get('Mh')!='': Mh = float(request.json.get('Mh'))
    return '200'

@app.route('/view/', methods=['GET', 'POST'])
def view():
    if request.method == 'POST':
        global trajectory
        args = request.args
        sat=args.get('name')
        time=args.get('timeUp')

        lon=float(args.get('lon'))
        lat=float(args.get('lat'))
        alt=float(args.get('alt'))

        horizon=float(args.get('horizon'))

        time = datetime.strptime(time, '%Y.%m.%d %H:%M:%S')
        trajectory=tra(sat, time, lon, lat, alt, horizon, True)
        return render_template('index3.html', title='trajectory', info=sat)
    else:
        return jsonify(trajectory)

@app.route("/forward/", methods=['GET','POST'])
def forward():
    global lat, lon, alt, horizon, Mh
    now = datetime.now()
    timeStart = now-timedelta(hours=3)

    sorted_a = raschot(timeStart, lon, lat, alt, horizon, Mh, 24)
    table = ItemTable(sorted_a)

    # return table.__html__()
    table = ItemTable(sorted_a, classes=['table'])
    return render_template('index2.html', title='schedule', tableData=table)

app.run(host="0.0.0.0")