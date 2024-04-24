import datetime
import json
from flask import Flask, render_template, request
from sqlalchemy import Boolean, Enum, and_, Float, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, DateTime

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


@app.route('/charts')
def ret_main_page():
    return render_template('index.html')


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


@app.route('/get_limits/<device_id>', methods=['GET'])
def mmm11(device_id):
    session = Session(bind=engine)
    limits = session.query(Devices.c.min_v, Devices.c.max_v, Devices.c.min_t, Devices.c.max_t).where(Devices.c.id == device_id)
    lim_json = [row._asdict() for row in limits]
    session.close()
    return json.dumps(lim_json)


@app.route('/get_signals_v/<device_id>/<start_date>/<end_date>', methods=['GET'])
def mmm(device_id, start_date, end_date):
    session = Session(bind=engine)
    signal_type_id = session.query(Signal_types).where(Signal_types.c.title == 'Напряжение')
    sig_json = [row._asdict() for row in signal_type_id]
    signal_type = sig_json[0]['id']
    signals = session.query(Signals).\
        where(and_(Signals.c.signal_type_id == signal_type, Signals.c.device_id == device_id, Signals.c.time >= start_date, Signals.c.time <= end_date))
    sig_json = [row._asdict() for row in signals]
    session.close()
    return json.dumps(sig_json, default=datetime_handler)


@app.route('/get_signals_t/<device_id>/<start_date>/<end_date>', methods=['GET'])
def mmm1(device_id, start_date, end_date):
    session = Session(bind=engine)
    signal_type_id = session.query(Signal_types).where(Signal_types.c.title == 'Температура')
    sig_json = [row._asdict() for row in signal_type_id]
    signal_type = sig_json[0]['id']
    signals = session.query(Signals).\
        where(and_(Signals.c.signal_type_id == signal_type, Signals.c.device_id == device_id, Signals.c.time >= start_date, Signals.c.time <= end_date))
    sig_json = [row._asdict() for row in signals]
    session.close()
    return json.dumps(sig_json, default=datetime_handler)


@app.route('/get_devices/<object_id>', methods=['GET'])
def func2(object_id):
    session = Session(bind=engine)
    devices = session.query(Devices).filter(Devices.c.object_id == object_id).all()
    dev_json = [row._asdict() for row in devices]
    session.close()
    return json.dumps(dev_json)






@app.route('/objects')
def ret_list1():
    return render_template('objects.html')


@app.route('/get_objects', methods=['GET'])
def func1():
    session = Session(bind=engine)
    objects = session.query(Objects).all()
    obj_json = [row._asdict() for row in objects]
    session.close()
    return json.dumps(obj_json)


@app.route('/create_object', methods=['POST'])
def get_and_cremg():
    data = request.json
    print(data['name'])#имя объекта
    return json.dumps({'id': 5, 'name': 'new-name'})


@app.route('/edit_object/<object_id>')
def home_func67(object_id):
    return render_template("editObject.html", object_id=object_id)


@app.route('/delete_object/<object_id>', methods=['DELETE'])
def get_anuik(object_id):
    print(object_id)#id объекта
    return json.dumps(7)




if __name__ == '__main__':
    app.run()