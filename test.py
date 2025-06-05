import asyncio
import psycopg2
import json
from pypetkitapi import PetKitClient
from aiohttp import ClientSession
from datetime import datetime, timedelta, date

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
    if 'time' in record and record['time']:
        record['time'] = datetime.fromtimestamp(record['time'])
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


    # Convert boolean fields to Python boolean     
    record['empty'] = bool(record.get('empty', False))
    record['is_executed'] = bool(record.get('is_executed', False))
    record['is_need_upload_video'] = bool(record.get('is_need_upload_video', False))


    insert_query = """
        INSERT INTO feeder_events (
            aes_key, aes_key1, aes_key2, amount, amount1, amount2, completed_at,
            content, description, device_id, duration, eat_end_time, eat_start_time,
            eat_video, eat_weight, empty, end_time, enum_event_type, event,
            event_id, event_type, expire, expire1, expire2, is_executed,
            is_need_upload_video, left_weight, mark, media_api, media_list,
            name, pet_id, preview, preview1, preview2, record_type, src, start_time, state,
            status, storage_space, time, timestamp
        ) VALUES (
            %(aes_key)s, %(aes_key1)s, %(aes_key2)s, %(amount)s, %(amount1)s, %(amount2)s, %(completed_at)s,
            %(content)s, %(desc)s, %(device_id)s, %(duration)s, %(eat_end_time)s, %(eat_start_time)s,
            %(eat_video)s, %(eat_weight)s, %(empty)s, %(end_time)s, %(enum_event_type)s, %(event)s,
            %(event_id)s, %(event_type)s, %(expire)s, %(expire1)s, %(expire2)s, %(is_executed)s,
            %(is_need_upload_video)s, %(left_weight)s, %(mark)s, %(media_api)s, %(media_list)s,
            %(name)s, %(pet_id)s, %(preview)s, %(preview1)s, %(preview2)s, %(record_type)s, %(src)s, %(start_time)s, %(state)s,
            %(status)s, %(storage_space)s, %(time)s, %(timestamp)s
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

def insert_litter_event(conn, record):
    
    record['event_id'] = record.get('timestamp', None)  #TEXT

    # Flatten content record if enum_event_type is 'pet_out'
    #if record.get('enum_event_type') == 'pet_out':
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
    record['content_pet_weight'] = int(value) if value is not None else 0                #INTEGER
    
    start_time_raw = record['content'].get('start_time', None)
    record['content_start_time'] = datetime.fromtimestamp(start_time_raw) if start_time_raw is not None else None
    
    time_in_raw = record['content'].get('time_in', None)
    record['content_time_in'] = datetime.fromtimestamp(time_in_raw) if time_in_raw is not None else None

    time_out_raw = record['content'].get('time_out', None)
    record['content_time_out'] = datetime.fromtimestamp(time_out_raw) if time_out_raw is not None else None

    record['content_toilet_detection'] = record['content'].get('toilet_detection', None) #TEXT
    record['content_upload'] = record['content'].get('upload', None)                     #TEXT
    record['content_error'] = record['content'].get('error', None)                       #TEXT

    # Convert TIMESTAMP fields to datetime objects
    if 'expire' in record and record['expire']:
        record['expire'] = datetime.fromtimestamp(record['expire'])  
    if 'timestamp' in record and record['timestamp']:
        record['timestamp'] = datetime.fromtimestamp(record['timestamp'])

    insert_query = """
        INSERT INTO litterbox_events (
            aes_key,avatar,device_id,duration,enum_event_type,event_id,event_type,expire,
            is_need_upload_video,mark,media,media_api,pet_id,pet_name,preview,related_event,
            shit_pictures,storage_space,timestamp,toilet_detection,upload,user_id,content_area,
            content_auto_clear,content_clear_over_tips,content_count,content_interval,content_mark,
            content_media,content_pet_out_tips,content_pet_weight,content_start_time,content_time_in,
            content_time_out,content_toilet_detection,content_upload,content_error
        ) VALUES (
            %(aes_key)s,%(avatar)s,%(device_id)s,%(duration)s,%(enum_event_type)s,%(event_id)s,
            %(event_type)s,%(expire)s,%(is_need_upload_video)s,%(mark)s,%(media)s,%(media_api)s,
            %(pet_id)s,%(pet_name)s,%(preview)s,%(related_event)s,%(shit_pictures)s,%(storage_space)s,
            %(timestamp)s,%(toilet_detection)s,%(upload)s,%(user_id)s,%(content_area)s,%(content_auto_clear)s,
            %(content_clear_over_tips)s,%(content_count)s,%(content_interval)s,%(content_mark)s,%(content_media)s,
            %(content_pet_out_tips)s,%(content_pet_weight)s,%(content_start_time)s,%(content_time_in)s,
            %(content_time_out)s,%(content_toilet_detection)s,%(content_upload)s,%(content_error)s
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



async def main():
    async with ClientSession() as session:
        
# Connect to PostgreSQL database
        
        conn = psycopg2.connect(
            host="192.168.1.9",
            port=5433,
            dbname="petkit",
            user="miyukiliu",
            password="michanhungry"
        )

        cur = conn.cursor()
        cur.execute("SELECT version();")
        print("Connected to:", cur.fetchone())


        #Create table query
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
            event_id TEXT UNIQUE,
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
            timestamp TIMESTAMP
        );
        """
        cur = conn.cursor()
        cur.execute(create_table_query)
        conn.commit()
        cur.close()

        # Connect to PetKit API
        client = PetKitClient("praline.villari@gmail.com","minifoss2","US","America/Los_Angeles",session)
        await client.login()

        # List devices
        await client.get_devices_data()

        # region Litterbox
        litterboxes = []
        for key, value in client.petkit_entities.items():
            print(f"{key}: {type(value).__name__} - {value.name}")
            if type(value).__name__ == "Litter":
                litterboxes.append(key)

        # Get first litterbox
        if (len(litterboxes) > 0):
            device_id = litterboxes[0]
            objLitterbox = client.petkit_entities[device_id]        
            litterboxRecords = objLitterbox.device_records

            print(f"Litterbox records\r\n")
            for value in litterboxRecords:
                print(f"Inserting Litterbox Record: {value} \r\n\r\n")
                tempDict = value.model_dump()                
                insert_litter_event(conn, tempDict)

        # endregion

        return
    
        # region Feeder

        # Lists all devices and pet from account
        feeders = []
        for key, value in client.petkit_entities.items():
            print(f"{key}: {type(value).__name__} - {value.name}")
            #if name contains "Feeder", add it to feeders list
            if type(value).__name__ == "Feeder":
                feeders.append(key)

        #get first feeder
        if (len(feeders) > 0):
            device_id = feeders[0]
            objFeeder = client.petkit_entities[device_id]        
            eatRecord = objFeeder.device_records.eat[0].items
            feedRecord = objFeeder.device_records.feed[0].items
            petRecord = objFeeder.device_records.pet[0].items

    
    
            print(f"Inserting eat records\r\n")
            for value in eatRecord:
                print(f"Inserting Eat Record: {value} \r\n\r\n")
                tempDict = value.model_dump()
                tempDict['record_type'] = 'eat'
                insert_petfeed_event(conn, tempDict)

            print(f"Inserting pet records\r\n")
            for value in petRecord:
                print(f"Inserting Pet Record: {value} \r\n\r\n")
                tempDict = value.model_dump()
                tempDict['record_type'] = 'pet'
                insert_petfeed_event(conn, tempDict)

            print(f"Inserting feed records\r\n")
            for value in feedRecord:
                print(f"Inserting Feed Record: {value} \r\n\r\n")
                tempDict = value.model_dump()
                tempDict['record_type'] = 'feed'
                insert_petfeed_event(conn, tempDict)

        
        # for value in feedRecord:
        #     print(f"Feed Record: {value} \r\n\r\n")


        # for value in petRecord:
        #     print(f"Pet Record: {value} \r\n\r\n")
        

        # fields_dict = value.model_dump()
        # fields_str = ', '.join(f"{k}" for k, v in fields_dict.items())
        # print(f"{fields_str}")
        
        # endregion

        conn.close()
        print("lalala")

loop = asyncio.get_event_loop() 
loop.run_until_complete(main())
