from pypetkitapi import PetKitClient
import json
import db.db_handler as dbhandler
from utils.logger import setup_logger

logger = setup_logger(__name__)

#Fetches feeder eat events and loads them to the db
def handleFeederData(conn, objFeederRecord, recordType='eat'):

    print(f"Inserting Feeder Records\r\n")
    logger.info(f"Inserting Feeder Records")
    for value in objFeederRecord:

        tempDict = value.model_dump()
        tempDict['record_type'] = recordType
        if (tempDict['event_id'] is None):
            continue

        print(f"Inserting Feeder Record: {value} \r\n\r\n")
        logger.info(f"Inserting Feeder Record: {value} for record type {recordType}")
        dbhandler.insert_petfeed_event(conn, tempDict)

def handleLitterData(conn, objLitterRecords):

    print(f"Litterbox records\r\n")
    logger.info("Inserting Litterbox records")
    for value in objLitterRecords:
        print(f"Inserting Litterbox Record: {value} \r\n\r\n")
        logger.info(f"Inserting Litterbox Record: {value}")
        tempDict = value.model_dump()                
        dbhandler.insert_litter_event(conn, tempDict)