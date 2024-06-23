import ast
import datetime
import json
import math
import random

import matplotlib.pyplot as plt

import numpy as np
from flask import Flask, render_template, request
from sqlalchemy import Boolean, Enum, and_, Float, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, DateTime
from sympy import symbols
import predict
from imitData import interval

x = symbols('x')

app = Flask(__name__)

engine = create_engine("postgresql+psycopg2://postgres:kata2000@localhost/AKB")
Base = MetaData()

Objects = Table\
    ('object', Base,
       Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
       Column('name', String(), nullable=False)
    )
Devices = Table\
    ('device', Base,
        Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
        Column('name', String(), nullable=False),
        Column('enabled', Boolean, nullable=False),
        Column('min_v', Float, nullable=False),
        Column('max_v', Float, nullable=False),
        Column('min_t', Float, nullable=False),
        Column('max_t', Float, nullable=False),
        Column('object_id', Integer, ForeignKey('object.id'), nullable=False),
        Column('module_id', Integer, ForeignKey('module.id')),
        Column('connector_num', Enum('1', '2', '3', '4', '5'))
    )
Signals = Table\
    ('signal', Base,
        Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
        Column('time', DateTime(), nullable=False),
        Column('value', Float, nullable=False),
        Column('signal_type_id', Integer, ForeignKey('signal_type.id'), nullable=False),
        Column('device_id', Integer, ForeignKey('device.id'), nullable=False)
    )
Signal_types = Table\
    ('signal_type', Base,
        Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
        Column('title', String(), unique=True, nullable=False),
    )


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


@app.route('/')
def get_main_page():
    return render_template('index.html')


@app.route('/get_objects', methods=['GET'])
def get_objects():
    session = Session(bind=engine)
    objects = session.query(Objects).all()
    obj_json = [row._asdict() for row in objects]
    session.close()
    return json.dumps(obj_json)


@app.route('/create_object', methods=['POST'])
def create_object():
    data = request.json
    print(data['name'])#имя объекта
    return json.dumps({'id': 5, 'name': 'new-name'})


@app.route('/edit_object/<object_id>')
def edit_object(object_id):
    return render_template("editObject.html", object_id=object_id)


@app.route('/delete_object/<object_id>', methods=['DELETE'])
def delete_object(object_id):
    print(object_id)#id объекта
    return json.dumps(7)


@app.route('/charts')
def get_charts_page():
    return render_template('charts.html')


@app.route('/get_devices/<object_id>', methods=['GET'])
def get_devices(object_id):
    session = Session(bind=engine)
    devices = session.query(Devices).filter(Devices.c.object_id == object_id).all()
    dev_json = [row._asdict() for row in devices]
    session.close()
    return json.dumps(dev_json)


@app.route('/get_limits/<device_id>', methods=['GET'])
def get_limits(device_id):
    session = Session(bind=engine)
    limits = session.query(Devices.c.min_v, Devices.c.max_v, Devices.c.min_t, Devices.c.max_t).where(
        Devices.c.id == device_id)
    lim_json = [row._asdict() for row in limits]
    session.close()
    return json.dumps(lim_json)


@app.route('/get_signals_v/<device_id>/<start_date>/<end_date>', methods=['GET'])
def get_signals_v(device_id, start_date, end_date):
    session = Session(bind=engine)
    signal_type_id = session.query(Signal_types).where(Signal_types.c.title == 'Напряжение')
    sig_json = [row._asdict() for row in signal_type_id]
    signal_type = sig_json[0]['id']
    signals = session.query(Signals).\
        where(and_(Signals.c.signal_type_id == signal_type, Signals.c.device_id == device_id, Signals.c.time >= start_date, Signals.c.time <= end_date)).order_by(Signals.c.time.asc())
    sig_json = [row._asdict() for row in signals]
    session.close()
    return json.dumps(sig_json, default=datetime_handler)


@app.route('/get_signals_t/<device_id>/<start_date>/<end_date>', methods=['GET'])
def get_signals_t(device_id, start_date, end_date):
    session = Session(bind=engine)
    signal_type_id = session.query(Signal_types).where(Signal_types.c.title == 'Температура')
    sig_json = [row._asdict() for row in signal_type_id]
    signal_type = sig_json[0]['id']
    signals = session.query(Signals).\
        where(and_(Signals.c.signal_type_id == signal_type, Signals.c.device_id == device_id, Signals.c.time >= start_date, Signals.c.time <= end_date)).order_by(Signals.c.time.asc())
    sig_json = [row._asdict() for row in signals]
    session.close()
    return json.dumps(sig_json, default=datetime_handler)


@app.route('/predict')
def get_predict_page():
    return render_template('predict.html')


@app.route('/get_last_signal/<device_id>', methods=['GET'])
def get_last_signal(device_id):
    session = Session(bind=engine)
    signals = session.query(Signals).where(Signals.c.device_id == device_id).order_by(Signals.c.time)
    session.close()
    sig_json = [row._asdict() for row in signals]
    last_signal = sig_json[len(sig_json) - 1]['time']
    return json.dumps(last_signal, default=datetime_handler)


@app.route('/get_predict_v/<device_id>/<period>', methods=['GET'])
def get_predict_v(device_id, period):
    session = Session(bind=engine)
    limits = session.query(Devices.c.min_v, Devices.c.max_v, Devices.c.min_t, Devices.c.max_t).where(
        Devices.c.id == device_id)
    session.close()
    lim_json = [row._asdict() for row in limits]
    min_v = -1
    max_v = -1
    for row in lim_json:
        min_v = row['min_v']
        max_v = row['max_v']
    signal_type_id = session.query(Signal_types).where(Signal_types.c.title == 'Напряжение')
    sig_json = [row._asdict() for row in signal_type_id]
    signal_type = sig_json[0]['id']
    signals = session.query(Signals).\
        where(and_(Signals.c.signal_type_id == signal_type, Signals.c.device_id == device_id)).order_by(Signals.c.time)
    session.close()
    sig_json = [row._asdict() for row in signals]
    start_signal_date = sig_json[0]['time']
    xi = []
    xi_calc = []
    for i in range(len(sig_json)):
        xi_calc.append((sig_json[i]['time'] - start_signal_date).total_seconds()/60)
        xi.append(sig_json[i]['time'])
    yi = []
    for i in range(len(sig_json)):
        yi.append(sig_json[i]['value'])
    charge_koef = []
    discharge_koef = []
    start = [0]
    i = 0
    time1 = 0
    time2 = 0
    while i < len(xi_calc)-1:
        charge_loop_x = []
        charge_loop_y = []
        index = -1
        while yi[i] <= max_v:
            if i >= len(xi_calc)-1:
                index = -1
                break
            charge_loop_x.append(xi_calc[i])
            charge_loop_y.append(yi[i])
            index = i
            i += 1
        if index == -1:
            break
        else:
            middle_loop_x = []
            middle_loop_y = []
            index = -1
            while yi[i] > max_v:
                if i >= len(xi_calc)-1:
                    index = -1
                    break
                middle_loop_x.append(xi_calc[i])
                middle_loop_y.append(yi[i])
                index = i
                i += 1
            if index == -1:
                break
            else:
                discharge_loop_x = []
                discharge_loop_y = []
                if len(middle_loop_x) % 2 == 0:
                    for j in range(len(middle_loop_x)):
                        if j < len(middle_loop_x)//2:
                            charge_loop_x.append(middle_loop_x[j])
                            charge_loop_y.append(middle_loop_y[j])
                        else:
                            discharge_loop_x.append(middle_loop_x[j])
                            discharge_loop_y.append(middle_loop_y[j])
                    start.append(i-len(middle_loop_x)//2-2)
                else:
                    for j in range(len(middle_loop_x)):
                        if j <= len(middle_loop_x)//2:
                            charge_loop_x.append(middle_loop_x[j])
                            charge_loop_y.append(middle_loop_y[j])
                        else:
                            discharge_loop_x.append(middle_loop_x[j])
                            discharge_loop_y.append(middle_loop_y[j])
                    start.append(i-len(middle_loop_x)//2-1)
                charge_loop_x_calc = []
                for j in range(len(charge_loop_x)):
                    charge_loop_x_calc.append(charge_loop_x[j]-charge_loop_x[0])
                time1 += len(charge_loop_x_calc)
                charge_koef.append(predict.MNK(charge_loop_x_calc, charge_loop_y, 3))
                while yi[i] >= min_v:
                    if i >= len(xi_calc)-1:
                        index = -1
                        break
                    discharge_loop_x.append(xi_calc[i])
                    discharge_loop_y.append(yi[i])
                    index = i
                    i += 1
                if index == -1:
                    break
                else:
                    middle_loop_x = []
                    middle_loop_y = []
                    while yi[i] < min_v:
                        if i >= len(xi_calc):
                            index = -1
                            break
                        middle_loop_x.append(xi_calc[i])
                        middle_loop_y.append(yi[i])
                        i += 1
                    if index == -1:
                        break
                    else:
                        if len(middle_loop_x) % 2 == 0:
                            for j in range(len(middle_loop_x)//2):
                                discharge_loop_x.append(middle_loop_x[j])
                                discharge_loop_y.append(middle_loop_y[j])
                        else:
                            for j in range(len(middle_loop_x)//2):
                                discharge_loop_x.append(middle_loop_x[j])
                                discharge_loop_y.append(middle_loop_y[j])
                        discharge_loop_x_calc = []
                        for j in range(len(discharge_loop_x)):
                            discharge_loop_x_calc.append(discharge_loop_x[j]-discharge_loop_x[0])
                        time2 += len(discharge_loop_x_calc)
                        discharge_koef.append(predict.MNK(discharge_loop_x_calc, discharge_loop_y, 3))
                        i -= len(middle_loop_x)//2
                        start.append(i)
    charge_k = [0, 0, 0, 0]
    for i in range(len(charge_koef)):
        for j in range(len(charge_k)):
            charge_k[j] += charge_koef[i][j]
    for i in range(len(charge_k)):
        charge_k[i] /= len(charge_koef)
    discharge_k = [0, 0, 0, 0]
    for i in range(len(discharge_koef)):
        for j in range(len(discharge_k)):
            discharge_k[j] += discharge_koef[i][j]
    for i in range(len(discharge_k)):
        discharge_k[i] /= len(discharge_koef)
    time1 /= len(charge_koef)
    time2 /= len(discharge_koef)
    charge_f = charge_k[0]*x**3+charge_k[1]*x**2+charge_k[2]*x+charge_k[3]
    discharge_f = discharge_k[0]*x**3+discharge_k[1]*x**2+discharge_k[2]*x+discharge_k[3]
    charge_koef = charge_koef[len(charge_koef)-3:]
    discharge_koef = discharge_koef[len(discharge_koef)-3:]
    start = start[len(start)-7:]
    xi = xi[start[0]+1:]
    yi = yi[start[0]+1:]
    for i in range(1, len(start)):
        start[i] = start[i]-start[0]
    start[0] = 0
    k = 0
    f = []
    for i in range(1, len(start)-1, 2):
        for j in range(start[i-1], start[i]):
            j -= start[i-1]
            f.append(charge_koef[k][0]*math.pow(xi_calc[j], 3)+charge_koef[k][1]*math.pow(xi_calc[j], 2)+charge_koef[k][2]*xi_calc[j]+charge_koef[k][3])
        for j in range(start[i], start[i+1]):
            j -= start[i]
            f.append(discharge_koef[k][0]*math.pow(xi_calc[j], 3)+discharge_koef[k][1]*math.pow(xi_calc[j], 2)+discharge_koef[k][2]*xi_calc[j]+discharge_koef[k][3])
        k += 1
    for i in range(start[len(start)-1], len(xi)-1):
        f.append(charge_f.subs(x, xi_calc[i]-xi_calc[start[len(start)-1]]))
    period_date = period.split(':')
    period = int(period_date[0])*1440+int(period_date[1])*60+int(period_date[2])
    x_predict = []
    x_predict.append(sig_json[len(sig_json)-1]['time'])
    x_predict_calc = [0]
    i = 1
    while period > 0:
        x_predict.append(x_predict[i-1]+datetime.timedelta(minutes=interval))
        x_predict_calc.append(x_predict_calc[i-1]+interval)
        period = period - interval
        i += 1
    time1 = round(time1)
    time2 = round(time2)
    y_predict = []
    i = 0
    for j in range(len(xi)-start[len(start)-1], time1):
        y_predict.append(charge_f.subs(x, x_predict_calc[j]))
        i += 1
    while i < len(x_predict_calc):
        for j in range(0, time2):
            if i >= len(x_predict_calc):
                break
            y_predict.append(discharge_f.subs(x, x_predict_calc[j]))
            i += 1
        for j in range(0, time1):
            if i >= len(x_predict_calc):
                break
            y_predict.append(charge_f.subs(x, x_predict_calc[j]))
            i += 1
    data = {
        'f1_title': str(charge_f),
        'f2_title': str(discharge_f),
        'x': xi,
        'y': str(yi),
        'f': str(f),
        'x_p': x_predict,
        'y_p': str(y_predict)
    }
    return json.dumps(data, default=datetime_handler)


@app.route('/get_predict_t/<device_id>/<x_predict_v>/<y_predict_v>', methods=['GET'])
def get_predict_t(device_id, x_predict_v, y_predict_v):
    y_predict_v = ast.literal_eval(y_predict_v)
    session = Session(bind=engine)
    signal_type_id = session.query(Signal_types).where(Signal_types.c.title == 'Температура')
    sig_json = [row._asdict() for row in signal_type_id]
    signal_type = sig_json[0]['id']
    signals = session.query(Signals).\
        where(and_(Signals.c.signal_type_id == signal_type, Signals.c.device_id == device_id)).order_by(Signals.c.time)
    session.close()
    sig_json = [row._asdict() for row in signals]
    xi = []
    for i in range(len(sig_json)):
        xi.append(sig_json[i]['time'])
    yi = []
    for i in range(len(sig_json)):
        yi.append(sig_json[i]['value'])
    y_predict = []
    y_predict.append(yi[len(yi)-1])
    for i in range(1, len(y_predict_v)):
        if y_predict_v[i] > y_predict_v[i-1]:
            y_predict.append(y_predict[i-1]-(y_predict_v[i]-y_predict_v[i-1])*4)
        else:
            y_predict.append(y_predict[i-1]+(y_predict_v[i-1]-y_predict_v[i])*4)
    data = {
        'x': xi,
        'y': str(yi),
        'y_p': str(y_predict)
    }
    return json.dumps(data, default=datetime_handler)


if __name__ == '__main__':
    app.run()