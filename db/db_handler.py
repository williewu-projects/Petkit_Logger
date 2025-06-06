#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
#from db.models import Base, Device, DeviceLog
#from config import DB_URL

import psycopg2
import json
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
import os
from config import POOPING_THRESHOLD
from utils.logger import setup_logger

logger = setup_logger(__name__)

#engine = create_engine(DB_URL)
#Session = sessionmaker(bind=engine)

load_dotenv()


def init_db(conn):
    #Create database here    
    #Base.metadata.create_all(engine)

    cur = conn.cursor()
    cur.execute("SELECT version();")

    #Create feeder events 
    create_table_query = """
    CREATE TABLE IF NOT EXISTS feeder_events (
        id SERIAL PRIMARY KEY,
        aes_key TEXT,
        aes_key1 TEXT,
        aes_key2 TEXT,
        amount NUMERIC,
        amount1 NUMERIC,
        amount2 NUMERIC,
        completed_at TIMESTAMP,
        content TEXT,
        description TEXT,
        device_id TEXT,
        duration NUMERIC,
        eat_end_time TIMESTAMP,
        eat_start_time TIMESTAMP,
        eat_video TEXT,
        eat_weight NUMERIC,
        empty BOOLEAN,
        end_time TIMESTAMP,
        enum_event_type TEXT,
        event TEXT,
        event_id TEXT UNIQUE NOT NULL,
        event_type TEXT,
        expire TIMESTAMP,
        expire1 TIMESTAMP,
        expire2 TIMESTAMP,
        is_executed BOOLEAN,
        is_need_upload_video BOOLEAN,
        left_weight NUMERIC,
        mark TEXT,
        media_api TEXT,
        media_list TEXT,
        name TEXT,
        pet_id TEXT,
        preview TEXT,
        preview1 TEXT,
        preview2 TEXT,
        record_type TEXT,
        src TEXT,
        start_time TIMESTAMP,
        state TEXT,
        status TEXT,
        storage_space NUMERIC,
        time TIMESTAMP,
        timestamp TIMESTAMP,
        insertion_time TIMESTAMP
    );
    """

    create_litterbox_table_query = """
    CREATE TABLE IF NOT EXISTS litterbox_events (
        id SERIAL PRIMARY KEY,
        aes_key TEXT,
        avatar TEXT,
        device_id BIGINT,
        duration INTEGER,
        enum_event_type TEXT,
        event_id BIGINT UNIQUE,
        event_type INTEGER,
        expire TIMESTAMP,
        is_need_upload_video BOOLEAN,
        mark TEXT,
        media TEXT,
        media_api TEXT,
        pet_id BIGINT,
        pet_name TEXT,
        preview TEXT,
        related_event TEXT,
        shit_pictures TEXT,
        storage_space TEXT,
        timestamp TIMESTAMP,
        toilet_detection TEXT,
        upload TEXT,
        user_id BIGINT,        
        content_area TEXT,
        content_auto_clear BOOLEAN,
        content_clear_over_tips TEXT,
        content_count INTEGER,
        content_interval INTEGER,
        content_mark TEXT,
        content_media TEXT,
        content_pet_out_tips TEXT,
        content_pet_weight_g NUMERIC,
        content_pet_weight_lb NUMERIC,
        content_start_time TIMESTAMP,
        content_time_in TIMESTAMP,
        content_time_out TIMESTAMP,
        content_toilet_duration INTEGER,
        content_toilet_usage_type TEXT,
        content_toilet_detection TEXT,
        content_upload TEXT,
        content_error TEXT,
        insertion_time TIMESTAMP
    );
    """

    cur = conn.cursor()
    cur.execute(create_table_query)
    cur.execute(create_litterbox_table_query)
    conn.commit()
    cur.close()

# def insert_device_log(device_id, status):
#     with Session() as session:
#         log = DeviceLog(device_id=device_id, status_json=str(status))
#         session.add(log)
#         session.commit()

def prepare_record_for_insert(record: dict) -> dict:
    """
    Prepares a Petkit record for PostgreSQL insert by converting
    dicts and lists into JSON strings.
    """
    def convert(value):
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return value

    return {k: convert(v) for k, v in record.items()}

def seconds_since_midnight_to_datetime(seconds: int, reference_date: date = None) -> datetime:
    """
    Converts seconds since midnight into a full datetime object.

    Args:
        seconds (int): Seconds since midnight (e.g. 41445).
        reference_date (datetime.date, optional): The date to anchor the time to.
                                                  Defaults to today's date.

    Returns:
        datetime: Combined date and time, e.g. 2025-05-26 11:30:45
    """
    if seconds is None:
        return None

    if reference_date is None:
        reference_date = datetime.today().date()

    return datetime.combine(reference_date, datetime.min.time()) + timedelta(seconds=seconds)

def insert_petfeed_event(conn, record):

    record = prepare_record_for_insert(record)

    #convert TIMESTAMP fields to datetime objects
    if 'completed_at' in record and record['completed_at']:
        record['completed_at'] = datetime.fromtimestamp(record['completed_at'])    
    if 'eat_end_time' in record and record['eat_end_time']:        
        record['eat_end_time'] = datetime.fromtimestamp(record['eat_end_time'])
    if 'eat_start_time' in record and record['eat_start_time']:
        record['eat_start_time'] = datetime.fromtimestamp(record['eat_start_time'])    
    if 'expire' in record and record['expire']:
        record['expire'] = datetime.fromtimestamp(record['expire'])    
    if 'expire1' in record and record['expire1']:
        record['expire1'] = datetime.fromtimestamp(record['expire1'])
    if 'expire2' in record and record['expire2']:
        record['expire2'] = datetime.fromtimestamp(record['expire2'])    
    #if 'time' in record and record['time']:
    #    record['time'] = datetime.fromtimestamp(record['time'])
    if 'timestamp' in record and record['timestamp']:
        record['timestamp'] = datetime.fromtimestamp(record['timestamp'])

    # start_time and end_time are time since midnight, convert to datetime
    if 'start_time' in record and record['start_time']:        
        # if Record_type is 'pet', calculates seconds to midnight, otherwise use datetime.fromtimestamp
        if record['record_type'] == 'eat':
            record['start_time'] = seconds_since_midnight_to_datetime(record['start_time'], reference_date=datetime.today())
        else:
            record['start_time'] = datetime.fromtimestamp(record['start_time'])
    if 'end_time' in record and record['end_time']:
        # if Record_type is 'pet', calculates seconds to midnight, otherwise use datetime.fromtimestamp
        if record['record_type'] == 'eat':
            record['end_time'] = seconds_since_midnight_to_datetime(record['end_time'], reference_date=datetime.today())
        else:
            record['end_time'] = datetime.fromtimestamp(record['end_time'])

    if 'time' in record and record['time']:
        # if Record_type is 'feed', calculates seconds to midnight, otherwise use datetime.fromtimestamp
        if record['record_type'] == 'feed':
            record['time'] = seconds_since_midnight_to_datetime(record['time'], reference_date=datetime.today())
        else:
            record['time'] = datetime.fromtimestamp(record['time'])

    # Custom logic for aligning time and timestamps
    if record['record_type'] == 'pet':
        # populate time using timestamp field
        if 'timestamp' in record and record['timestamp']:
            record['time'] = record['timestamp']

    if record['record_type'] == 'feed':      
        # populate the timestamp field using time field
        if 'time' in record and record['time']:
            record['timestamp'] = record['time']
        pass

    if record['record_type'] == 'eat':
        # take start_time and put it in time and timestamp field
        if 'start_time' in record and record['start_time']:
            record['time'] = record['start_time']
            record['timestamp'] = record['start_time']

    # Convert boolean fields to Python boolean     
    record['empty'] = bool(record.get('empty', False))
    record['is_executed'] = bool(record.get('is_executed', False))
    record['is_need_upload_video'] = bool(record.get('is_need_upload_video', False))
    
    record['insertion_time'] = datetime.now()

    insert_query = """
        INSERT INTO feeder_events (
            aes_key, aes_key1, aes_key2, amount, amount1, amount2, completed_at,
            content, description, device_id, duration, eat_end_time, eat_start_time,
            eat_video, eat_weight, empty, end_time, enum_event_type, event,
            event_id, event_type, expire, expire1, expire2, is_executed,
            is_need_upload_video, left_weight, mark, media_api, media_list,
            name, pet_id, preview, preview1, preview2, record_type, src, start_time, state,
            status, storage_space, time, timestamp, insertion_time
        ) VALUES (
            %(aes_key)s, %(aes_key1)s, %(aes_key2)s, %(amount)s, %(amount1)s, %(amount2)s, %(completed_at)s,
            %(content)s, %(desc)s, %(device_id)s, %(duration)s, %(eat_end_time)s, %(eat_start_time)s,
            %(eat_video)s, %(eat_weight)s, %(empty)s, %(end_time)s, %(enum_event_type)s, %(event)s,
            %(event_id)s, %(event_type)s, %(expire)s, %(expire1)s, %(expire2)s, %(is_executed)s,
            %(is_need_upload_video)s, %(left_weight)s, %(mark)s, %(media_api)s, %(media_list)s,
            %(name)s, %(pet_id)s, %(preview)s, %(preview1)s, %(preview2)s, %(record_type)s, %(src)s, %(start_time)s, %(state)s,
            %(status)s, %(storage_space)s, %(time)s, %(timestamp)s, %(insertion_time)s
        )
        ON CONFLICT DO NOTHING;
    """
    try:   
        with conn.cursor() as cur:
            cur.execute(insert_query, record)
        conn.commit()
        cur.close()

    except Exception as e:
        conn.rollback()
        print("❌ Error inserting record:", e)
        logger.error(f"Error inserting record: {e}")

def insert_litter_event(conn, record):
    
    record['event_id'] = record.get('timestamp', None)  #TEXT
    if record['event_id'] is None:
        return  # If event_id is None, do not insert the record

    # Flatten content record 
    record['content_area'] = record['content'].get('area', None)                         #TEXT
    record['content_auto_clear'] = bool(record['content'].get('auto_clear', None))       #BOOLEAN
    record['content_clear_over_tips'] = record['content'].get('clear_over_tips', None)   #TEXT

    value = record['content'].get('count')
    record['content_count'] = int(value) if value is not None else 0                     #INTEGER
    
    value = record['content'].get('interval')
    record['content_interval'] = int(value) if value is not None else 0                  #INTEGER 

    record['content_mark'] = record['content'].get('mark', None)                         #TEXT
    record['content_media'] = record['content'].get('media', None)                       #TEXT
    record['content_pet_out_tips'] = record['content'].get('pet_out_tips', None)         #TEXT
    
    value = record['content'].get('pet_weight')    
    record['content_pet_weight_g'] = int(value) if value is not None else 0                #NUMERIC        
    # Convert pet weight to lbs
    if record['content_pet_weight_g'] is not None:
        record['content_pet_weight_lb'] = record['content_pet_weight_g'] * 0.00220462
    else:
        record['content_pet_weight_lb'] = None

    start_time_raw = record['content'].get('start_time', None)
    record['content_start_time'] = datetime.fromtimestamp(start_time_raw) if start_time_raw is not None else None
    
    time_in_raw = record['content'].get('time_in', None)
    record['content_time_in'] = datetime.fromtimestamp(time_in_raw) if time_in_raw is not None else None

    time_out_raw = record['content'].get('time_out', None)
    record['content_time_out'] = datetime.fromtimestamp(time_out_raw) if time_out_raw is not None else None

    # Calculate time between time_out_raw and time_in_raw
    if time_in_raw is not None and time_out_raw is not None:
        record['content_toilet_duration'] = (time_out_raw - time_in_raw)
    else:
        record['content_toilet_duration'] = None

    # If the content_toilet_duration is greater than the threshold specified in config.py, set content_toilet_usage_type to 'poo', otherwise 'pee'
    if record['content_toilet_duration'] is not None:
        record['content_toilet_usage_type'] = 'poo' if record['content_toilet_duration'] > POOPING_THRESHOLD else 'pee'
    else:
        record['content_toilet_usage_type'] = None

    record['content_toilet_detection'] = record['content'].get('toilet_detection', None)                     #TEXT
    record['content_upload'] = record['content'].get('upload', None)                     #TEXT
    record['content_error'] = record['content'].get('error', None)                       #TEXT

    # Convert TIMESTAMP fields to datetime objects
    if 'expire' in record and record['expire']:
        record['expire'] = datetime.fromtimestamp(record['expire'])  
    if 'timestamp' in record and record['timestamp']:
        record['timestamp'] = datetime.fromtimestamp(record['timestamp'])

    record['insertion_time'] = datetime.now()  # Add insertion time for logging

    insert_query = """
        INSERT INTO litterbox_events (
            aes_key,avatar,device_id,duration,enum_event_type,event_id,event_type,expire,
            is_need_upload_video,mark,media,media_api,pet_id,pet_name,preview,related_event,
            shit_pictures,storage_space,timestamp,toilet_detection,upload,user_id,content_area,
            content_auto_clear,content_clear_over_tips,content_count,content_interval,content_mark,
            content_media,content_pet_out_tips,content_pet_weight_g,content_pet_weight_lb,content_start_time,content_time_in,
            content_time_out,content_toilet_duration,content_toilet_usage_type,content_toilet_detection,content_upload,content_error,
            insertion_time
        ) VALUES (
            %(aes_key)s,%(avatar)s,%(device_id)s,%(duration)s,%(enum_event_type)s,%(event_id)s,
            %(event_type)s,%(expire)s,%(is_need_upload_video)s,%(mark)s,%(media)s,%(media_api)s,
            %(pet_id)s,%(pet_name)s,%(preview)s,%(related_event)s,%(shit_pictures)s,%(storage_space)s,
            %(timestamp)s,%(toilet_detection)s,%(upload)s,%(user_id)s,%(content_area)s,%(content_auto_clear)s,
            %(content_clear_over_tips)s,%(content_count)s,%(content_interval)s,%(content_mark)s,%(content_media)s,
            %(content_pet_out_tips)s,%(content_pet_weight_g)s,%(content_pet_weight_lb)s,%(content_start_time)s,%(content_time_in)s,
            %(content_time_out)s,%(content_toilet_duration)s,%(content_toilet_usage_type)s,%(content_toilet_detection)s,%(content_upload)s,%(content_error)s,
            %(insertion_time)s
        )
        ON CONFLICT DO NOTHING;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(insert_query, record)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("❌ Error inserting record:", e)
        logger.error(f"Error inserting record: {e}")