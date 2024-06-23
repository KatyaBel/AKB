import datetime
import json
import random
from sqlalchemy import Boolean, Enum, and_, Float, insert, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, DateTime

engine = create_engine("postgresql+psycopg2://postgres:kata2000@localhost/AKB", pool_size=10, max_overflow=-1)
Base = MetaData()

limit_min_abs_v = 0
limit_max_abs_v = 16
limit_min_abs_t = -30
limit_max_abs_t = 120
interval = 30

states = {
    '1': 'charge',
    '2': 'charge',
    '3': 'charge',
    '4': 'charge',
    '5': 'charge',
    '6': 'charge',
    '7': 'charge',
    '8': 'charge',
    '9': 'charge',
    '10': 'charge',
    '11': 'charge',
    '12': 'charge'
}

last_v = {
    '1': -1,
    '2': -1,
    '3': -1,
    '4': -1,
    '5': -1,
    '6': -1,
    '7': -1,
    '8': -1,
    '9': -1,
    '10': -1,
    '11': -1,
    '12': -1
}

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
Modules = Table\
    ('module', Base,
        Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
        Column('name', String(), nullable=False),
        Column('object_id', Integer, ForeignKey('object.id'), nullable=False),
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


def start(cur_time):
    global states
    session = Session(bind=engine)
    #date_now = datetime.datetime.now()
    #cur_time = str(date_now.date())+' '+str(date_now.hour)+':'+str(date_now.minute)+':'+str(date_now.second)
    modules = session.query(Modules).order_by(Modules.c.id)
    session.close()
    mod_json = [row._asdict() for row in modules]
    data = []
    for row in mod_json:
        devices = session.query(Devices).filter(and_(Devices.c.module_id == row['id'], Devices.c.enabled == True)).order_by(Devices.c.connector_num)
        session.close()
        dev_json = [row._asdict() for row in devices]
        if len(dev_json) != 0:
            V = ['null', 'null', 'null', 'null', 'null']
            T = ['null', 'null', 'null', 'null', 'null']
            for row1 in dev_json:
                session = Session(bind=engine)
                limits = session.query(Devices.c.min_v, Devices.c.max_v, Devices.c.min_t, Devices.c.max_t).where(
                    Devices.c.id == row1['id'])
                session.close()
                lim_json = [row._asdict() for row in limits]
                limit_min_v = -1
                limit_max_v = -1
                for row2 in lim_json:
                    limit_min_v = row2['min_v']
                    limit_max_v = row2['max_v']
                    limit_max_t = row2['max_t']
                signal_type_id = session.query(Signal_types.c.id).where(Signal_types.c.title == 'Напряжение')
                sig_json = [row._asdict() for row in signal_type_id]
                signal_type = sig_json[0]['id']
                values = session.query(Signals.c.value).\
                    filter(and_(Signals.c.device_id == row1['id'], Signals.c.signal_type_id == signal_type)).order_by(Signals.c.time.desc())
                val_json = [row._asdict() for row in values]
                if len(val_json) == 0:
                    V[int(row1['connector_num']) - 1] = limit_min_v
                else:
                    if (last_v[str(row1['id'])] < limit_min_v):
                        states[str(row1['id'])] = 'charge'
                        if last_v[str(row1['id'])] > limit_min_abs_v:
                            V[int(row1['connector_num']) - 1] = round(random.uniform(last_v[str(row1['id'])]-0.01, last_v[str(row1['id'])]+0.1), 2)
                        else:
                            V[int(row1['connector_num']) - 1] = round(random.uniform(limit_min_abs_v, last_v[str(row1['id'])]+0.1), 2)
                    elif (last_v[str(row1['id'])] > limit_max_v):
                        states[str(row1['id'])] = 'discharge'
                        if last_v[str(row1['id'])] < limit_max_abs_v:
                            V[int(row1['connector_num']) - 1] = round(random.uniform(last_v[str(row1['id'])]-0.1, last_v[str(row1['id'])]+0.01), 2)
                        else:
                            V[int(row1['connector_num']) - 1] = round(random.uniform(last_v[str(row1['id'])]-0.1, limit_max_abs_v), 2)
                    elif states[str(row1['id'])] == 'charge':
                        #заряд
                        if last_v[str(row1['id'])] <= limit_min_v+2/3*(limit_max_v-limit_min_v):
                            V[int(row1['connector_num']) - 1] = round(random.uniform(last_v[str(row1['id'])], last_v[str(row1['id'])]+0.45), 2)
                        else:
                            V[int(row1['connector_num']) - 1] = round(random.uniform(last_v[str(row1['id'])], last_v[str(row1['id'])]+0.05), 2)
                    else:
                        #разряд
                        if last_v[str(row1['id'])] <= limit_min_v+2/3*(limit_max_v-limit_min_v):
                            V[int(row1['connector_num']) - 1] = round(random.uniform(last_v[str(row1['id'])], last_v[str(row1['id'])]-0.4), 2)
                        else:
                            V[int(row1['connector_num']) - 1] = round(random.uniform(last_v[str(row1['id'])], last_v[str(row1['id'])]-0.03), 2)
                last_v[str(row1['id'])] = V[int(row1['connector_num']) - 1]

                #signal_type_id = session.query(Signal_types.c.id).where(Signal_types.c.title == 'Температура')
                #sig_json = [row._asdict() for row in signal_type_id]
                #signal_type = sig_json[0]['id']
                #values = session.query(Signals.c.value).filter(and_(Signals.c.device_id == row1['id'], Signals.c.signal_type_id == signal_type)).order_by(Signals.c.time.desc())
                #val_json = [row._asdict() for row in values]
                #if len(val_json) == 0:
                    #T[int(row1['connector_num']) - 1] = limit_max_t
                #else:
                    #last2 = val_json[0]['value']
                    #if (last1 <= limit_min_v):
                       # if last1 > limit_min_abs_v:
                           # T[int(row1['connector_num']) - 1] = round(random.uniform(last2-0.1*dist_t, last2+0.9*dist_t), 2)
                        #else:
                           # T[int(row1['connector_num']) - 1] = round(random.uniform(last2, last2 +0.9*dist_t), 2)
                    #elif (last1 >= limit_max_v):
                       # if last1 < limit_max_abs_v:
                           # T[int(row1['connector_num']) - 1] = round(random.uniform(last2-0.9*dist_t, last2+0.1*dist_t), 2)
                        #else:
                           # T[int(row1['connector_num']) - 1] = round(random.uniform(last2-0.9*dist_t, last2), 2)
                   # elif states[str(row1['id'])] == 'charge':
                        #заряд
                        #T[int(row1['connector_num']) - 1] = round(random.uniform(last2-0.9*dist_t, last2+0.1*dist_t), 2)
                    #else:
                        #разряд
                        #T[int(row1['connector_num']) - 1] = round(random.uniform(last2-0.1*dist_t, last2+0.9*dist_t), 2)
        moduleData = {
            'module_id': str(row['id']),
            'time': cur_time,
            'values': [
                {
                    'V1': str(V[0]),
                    'T1': str(T[0]),
                    'V2': str(V[1]),
                    'T2': str(T[1]),
                    'V3': str(V[2]),
                    'T3': str(T[2]),
                    'V4': str(V[3]),
                    'T4': str(T[3]),
                    'V5': str(V[4]),
                    'T5': str(T[4])
                }
            ]
        }
        data.append(moduleData)
    session.close()
    print('\nПоказания:')
    print(json.dumps(data, indent=4, sort_keys=True, default=str))
    add_to_base(data)
    #threading.Timer(interval*60, start).start()


def add_to_base(data):
    for i in range(0, len(data)):
        module_id = data[i]['module_id']
        time = data[i]['time']
        values = data[i]['values'][0]
        for key in values:
            value = values[key]
            if value != 'null':
                session = Session(bind=engine)
                if key[0] == 'V':
                    signal_type_id = session.query(Signal_types).where(Signal_types.c.title == 'Напряжение')
                    sig_json = [row._asdict() for row in signal_type_id]
                    signal_type = sig_json[0]['id']
                else:
                    signal_type_id = session.query(Signal_types).where(Signal_types.c.title == 'Температура')
                    sig_json = [row._asdict() for row in signal_type_id]
                    signal_type = sig_json[0]['id']
                devices = session.query(Devices).where(
                    and_(Devices.c.module_id == module_id, Devices.c.connector_num == key[1]))
                dev_json = [row._asdict() for row in devices]
                device_id = dev_json[0]['id']
                session.close()
                stmt = insert(Signals).values(time=time, value=value, signal_type_id=signal_type, device_id=device_id)
                with engine.begin() as conn:
                    conn.execute(stmt)


if __name__ == '__main__':
    cur_time = datetime.datetime(2024, 6, 1, 0, 0, 0)
    for i in range(1000):
        start(cur_time)
        cur_time += datetime.timedelta(minutes=interval)