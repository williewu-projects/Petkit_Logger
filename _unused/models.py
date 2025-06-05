# from sqlalchemy import Column, Integer, String, DateTime, Float
# from sqlalchemy.ext.declarative import declarative_base
# import datetime

# Base = declarative_base()

# class Device(Base):
#     __tablename__ = 'devices'
#     id = Column(Integer, primary_key=True)
#     device_id = Column(String, unique=True)
#     name = Column(String)
#     type = Column(String)

# class DeviceLog(Base):
#     __tablename__ = 'device_logs'
#     id = Column(Integer, primary_key=True)
#     device_id = Column(String)
#     timestamp = Column(DateTime, default=datetime.datetime.utcnow)
#     status_json = Column(String)  # Or break this into columns if structured