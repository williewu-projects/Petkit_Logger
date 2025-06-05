from pypetkitapi import PetKitClient
from config import PETKIT_EMAIL, PETKIT_PASSWORD

class PetkitService:
    def __init__(self, session):       
        print("setting up client session")
        #self.client = PetKitClient(PETKIT_EMAIL, PETKIT_PASSWORD, "US", "America/Los_Angeles", session)
        self.client = PetKitClient("praline.villari@gmail.com", "minifoss2", "US", "America/Los_Angeles", session)
       
    def get_devices(self):
        return self.client.get_devices()

    def get_device_status(self, device_id):
        return self.client.get_device_status(device_id)