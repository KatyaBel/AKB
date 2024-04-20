import datetime
import json
import random
import threading
from sqlalchemy import Boolean, Enum, and_, Float, insert, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, DateTime

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

def start():
    date_now = datetime.datetime.now()
    cur_time = str(date_now.date())+' '+str(date_now.hour)+':'+str(date_now.minute)+':'+str(date_now.second)
    session = Session(bind=engine)
    modules = session.query(Modules).order_by(Modules.c.id)
    session.close()
    mod_json = [row._asdict() for row in modules]
    data = []
    for row in mod_json:
        session = Session(bind=engine)
        devices = session.query(Devices).filter(and_(Devices.c.module_id == row['id'], Devices.c.enabled == True)).order_by(Devices.c.connector_num)
        session.close()
        dev_json = [row._asdict() for row in devices]
        if len(dev_json) != 0:
            V = ['null', 'null', 'null', 'null', 'null']
            T = ['null', 'null', 'null', 'null', 'null']
            for row1 in dev_json:
                #row1['max_v']
                V[int(row1['connector_num']) - 1] = round(random.uniform(9.8, 13.1), 2)
                T[int(row1['connector_num']) - 1] = round(random.uniform(15, 33), 2)
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
    print('\nПоказания:')
    print(json.dumps(data, indent=4))
    add_to_base(data)
    threading.Timer(10, start).start()


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

                stmt = insert(Signals).values(time=time, value=value, signal_type_id=signal_type, device_id=device_id)
                conn = session.connection()
                with engine.begin() as conn:
                    conn.execute(stmt)
                conn.close()
                session.close()


if __name__ == '__main__':
    start()