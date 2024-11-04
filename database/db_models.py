from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from .db_engine import Base
from datetime import datetime

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    equipment_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    value = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_equipment_timestamp', 'equipment_id', 'timestamp'),
        Index('idx_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SensorReading(equipment_id={self.equipment_id}, timestamp={self.timestamp}, value={self.value})>"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)