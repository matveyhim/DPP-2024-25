from flask import Flask, request, render_template, Response, jsonify
from flask_table import Table, Col, ButtonCol
from pyorbital.orbital import Orbital
from pyorbital import tlefile
from datetime import datetime, timezone, timedelta, time
import requests
# utc_time = datetime(2023, 10, 16, 0, 0)
global tle
tle='tle.txt'
def raschot(utc_time, lon, lat, alt, horizon, mH, length):
    i=0
    az=0
    h=0 #Высота спутника (град)
    n=0
    a=[]
    sats=['METEOR M2-3', 'METEOR M2-4', 'NOAA-15', 'NOAA-18', 'NOAA-19', 'METOP-B', 'METOP-C']
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

print('get TLE')
p = requests.get('http://r4uab.ru/satonline.txt')
out = open(tle, "wb")
out.write(p.content)
out.close()

@app.route('/')
def login():
    return render_template('index1.html')

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
    lon = float(request.form['lon'])
    lat = float(request.form['lat'])
    alt = float(request.form['h'])   #Высота станции (м)

    horizon = float(request.form['hor'])
    Mh = float(request.form['Mh'])

    timeStart = request.form['time']
    timeEnd = request.form['time_end']

    print('timeStart:',timeStart)
    print('timeEnd:',timeEnd)

    utc_time = datetime.strptime(timeStart, '%Y-%m-%dT%H:%M')
    length = datetime.strptime(timeEnd, '%Y-%m-%dT%H:%M')-utc_time
    length = (length.days*24)+(length.seconds//3600)
    print(length)
    sorted_a = raschot(utc_time, lon, lat, alt, horizon, Mh, length)
    table = ItemTable(sorted_a)

    # return table.__html__()
    table = ItemTable(sorted_a, classes=['table'])
    return render_template('index2.html', title='schedule', tableData=table)

@app.route('/download/', methods=['GET','POST'])
def download():
    args = request.args
    sat=args.get('name')
    time=args.get('timeUp')

    lon=float(args.get('lon'))
    lat=float(args.get('lat'))
    alt=float(args.get('alt'))

    horizon=float(args.get('horizon'))

    time = datetime.strptime(time, '%Y.%m.%d %H:%M:%S')
    s=tra(sat, time, lon, lat, alt, horizon, False)

    return Response(s,mimetype="text/txt",headers={"Content-disposition":"attachment; filename="+sat+".txt"})

if __name__ == '__main__':
    app.run()