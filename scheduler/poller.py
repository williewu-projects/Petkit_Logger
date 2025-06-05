import time
from petkit.service import PetkitService
#from db.db_handler import insert_device_log, init_db
from db.db_handler import init_db
from config import POLL_INTERVAL_SEC
import  petkit.datahandler as data
from utils.logger import setup_logger

from pypetkitapi import PetKitClient
from aiohttp import ClientSession

logger = setup_logger(__name__)

async def start_polling(conn):
    init_db(conn)

    async with ClientSession() as session:
        service = PetkitService(session)                

        while True:
            logger.info("Polling devices...")
            try:
                await service.client.login()

                print("Getting device data...")
                logger.info("Fetching device data...")
                await service.client.get_devices_data()

                # Lists all devices and pet from account
                feeders = []
                litterboxes = []
                for key, value in service.client.petkit_entities.items():
                    print(f"{key}: {type(value).__name__} - {value.name}")
                    logger.info(f"{key}: {type(value).__name__} - {value.name}")
                    if type(value).__name__ == "Feeder":
                        feeders.append(key)
                    if type(value).__name__ == "Litter":
                        litterboxes.append(key)

                # Poll feeder(s)
                # 1. eat records
                # 2. feed records
                # 3. pet records

                # region Polling Feeder
                if (len(feeders) > 0):
                    device_id = feeders[0]
                    objFeeder = service.client.petkit_entities[device_id]  
                    
                    if len(objFeeder.device_records.eat) > 0:
                        eatRecord = objFeeder.device_records.eat[0].items     
                        data.handleFeederData(conn, eatRecord, 'eat')
                    if len(objFeeder.device_records.feed) > 0:
                        feedRecord = objFeeder.device_records.feed[0].items
                        data.handleFeederData(conn, feedRecord, 'feed')
                    if len(objFeeder.device_records.pet) > 0:
                        petRecord = objFeeder.device_records.pet[0].items
                        data.handleFeederData(conn, petRecord, 'pet')
                # endregion
                
                # region Polling Litter Box
                if (len(litterboxes) > 0):
                    device_id = litterboxes[0]
                    objLitterbox = service.client.petkit_entities[device_id]
                    objLitterBoxRecords = objLitterbox.device_records        
                    data.handleLitterData(conn,objLitterBoxRecords)

                # endregion

                # Scan water fountain

            except Exception as e:
                logger.error(f"Error during polling: {e}")

            time.sleep(POLL_INTERVAL_SEC)