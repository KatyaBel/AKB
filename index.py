import datetime
import json
import time

from flask import Flask, render_template, request
from sqlalchemy import Boolean, Enum, and_, Float, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, DateTime
from sympy import symbols
import predict

x = symbols('x')
K = 5 #степень многочлена

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
        xi_calc.append((sig_json[i]['time'] - start_signal_date).total_seconds())
        xi.append(sig_json[i]['time'])
    yi = []
    for i in range(len(sig_json)):
        yi.append(sig_json[i]['value'])
    charge_koef = []
    discharge_koef = []
    i = 0
    last = -1
    time1 = 0
    time2 = 0
    while i < len(xi_calc)-1:
        charge_loop_x = []
        charge_loop_y = []
        index = -1
        while yi[i] <= 14.5:
            if i >= len(xi)-1:
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
            while yi[i] > 14.5:
                if i >= len(xi)-1:
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
                else:
                    for j in range(len(middle_loop_x)):
                        if j <= len(middle_loop_x)//2:
                            charge_loop_x.append(middle_loop_x[j])
                            charge_loop_y.append(middle_loop_y[j])
                        else:
                            discharge_loop_x.append(middle_loop_x[j])
                            discharge_loop_y.append(middle_loop_y[j])
                charge_loop_x_calc = []
                for j in range(len(charge_loop_x)):
                    charge_loop_x_calc.append(charge_loop_x[j]-charge_loop_x[0])
                time1 += len(charge_loop_x_calc)
                charge_koef.append(predict.MNK(charge_loop_x_calc, charge_loop_y, 3))
                while yi[i] >= 11:
                    if i >= len(xi)-1:
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
                    while yi[i] < 11:
                        if i >= len(xi):
                            index = -1
                            break
                        middle_loop_x.append(xi_calc[i])
                        middle_loop_y.append(yi[i])
                        i += 1
                    if index == -1:
                        break
                    else:
                        if len(middle_loop_x) % 2 == 0:
                            for j in range(len(middle_loop_x) // 2):
                                discharge_loop_x.append(middle_loop_x[j])
                                discharge_loop_y.append(middle_loop_y[j])
                        else:
                            for j in range(len(middle_loop_x) // 2):
                                discharge_loop_x.append(middle_loop_x[j])
                                discharge_loop_y.append(middle_loop_y[j])
                        discharge_loop_x_calc = []
                        for j in range(len(discharge_loop_x)):
                            discharge_loop_x_calc.append(discharge_loop_x[j] - discharge_loop_x[0])
                        time2 += len(discharge_loop_x_calc)
                        discharge_koef.append(predict.MNK(discharge_loop_x_calc, discharge_loop_y, 3))
                        i -= len(middle_loop_x) // 2
                        last = i
    charge_k1 = 0
    charge_k2 = 0
    charge_k3 = 0
    charge_k4 = 0
    for i in range(len(charge_koef)):
        charge_k1 += charge_koef[i][0]
        charge_k2 += charge_koef[i][1]
        charge_k3 += charge_koef[i][2]
        charge_k4 += charge_koef[i][3]
    charge_k1 /= len(charge_koef)
    charge_k2 /= len(charge_koef)
    charge_k3 /= len(charge_koef)
    charge_k4 /= len(charge_koef)
    discharge_k1 = 0
    discharge_k2 = 0
    discharge_k3 = 0
    discharge_k4 = 0
    for i in range(len(discharge_koef)):
        discharge_k1 += discharge_koef[i][0]
        discharge_k2 += discharge_koef[i][1]
        discharge_k3 += discharge_koef[i][2]
        discharge_k4 += discharge_koef[i][3]
    discharge_k1 /= len(discharge_koef)
    discharge_k2 /= len(discharge_koef)
    discharge_k3 /= len(discharge_koef)
    discharge_k4 /= len(discharge_koef)
    time1 /= len(charge_koef)
    time2 /= len(discharge_koef)
    charge_f = charge_k1*x**3+charge_k2*x**2+charge_k3*x+charge_k4
    discharge_f = discharge_k1*x**3+discharge_k2*x**2+discharge_k3*x+discharge_k4
    f = []
    while i <= len(xi_calc):
        for j in range(0, int(time1)-1):
            f.append(charge_f.subs(x, xi_calc[j]))
            i += 1
        for j in range(0, int(time2)-1):
            f.append(discharge_f.subs(x, xi_calc[j]))
            i += 1
    period = time.strptime(period, '%H:%M:%S')
    period = datetime.timedelta(hours=period.tm_hour, minutes=period.tm_min, seconds=period.tm_sec).total_seconds()
    x_predict = []
    x_predict_calc = []
    for i in range(last, len(sig_json)):
        x_predict.append(xi[i])
        x_predict_calc.append(xi_calc[i])
    i = len(x_predict)
    while period > 0:
        x_predict.append(x_predict[i-1] + datetime.timedelta(seconds=10))
        x_predict_calc.append(x_predict_calc[i-1]+10)
        period = period - 10
        i = i + 1
    y_predict = []
    i = 0
    while i <= len(x_predict_calc):
        for j in range(0, int(time1) - 1):
            y_predict.append(charge_f.subs(x, x_predict_calc[j]-x_predict_calc[0]))
            i += 1
        for j in range(0, int(time2) - 1):
            y_predict.append(discharge_f.subs(x, x_predict_calc[j]-x_predict_calc[0]))
            i += 1
    x_predict[:len(sig_json)-last] = []
    x_predict_calc[:len(sig_json)-last] = []
    y_predict[:len(sig_json)-last] = []
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


@app.route('/get_predict_t/<device_id>/<start_date>/<period>', methods=['GET'])
def get_predict_t(device_id, start_date, period):
    session = Session(bind=engine)
    signal_type_id = session.query(Signal_types).where(Signal_types.c.title == 'Температура')
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
        xi_calc.append((sig_json[i]['time'] - start_signal_date).total_seconds())
        xi.append(sig_json[i]['time'])
    yi = []
    for i in range(len(sig_json)):
        yi.append(sig_json[i]['value'])
    func = predict.MNK(xi_calc, yi, K)
    f = [func.subs(x, a) for a in xi_calc]

    x_predict = []
    x_predict_calc = []
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    x_predict.append(start_date)
    x_predict_calc.append((start_date - start_signal_date).total_seconds())
    period = time.strptime(period, '%H:%M:%S')
    period = datetime.timedelta(hours=period.tm_hour, minutes=period.tm_min, seconds=period.tm_sec).total_seconds()
    i = 1
    while period > 0:
        x_predict.append(x_predict[i - 1] + datetime.timedelta(seconds=10))
        x_predict_calc.append(x_predict_calc[i - 1] + 10)
        period = period - 10
        i = i + 1
    y_predict = [func.subs(x, a) for a in x_predict_calc]
    for i in range(len(y_predict)):
        if y_predict[i] > 110:
            y_predict[i] = 110
        if y_predict[i] < -30:
            y_predict[i] = -30
    data = {
        'f_title': str(func),
        'x': xi,
        'y': str(yi),
        'f': str(f),
        'x_p': x_predict,
        'y_p': str(y_predict)
    }
    return json.dumps(data, default=datetime_handler)


if __name__ == '__main__':
    app.run()