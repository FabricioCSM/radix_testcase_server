from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

class SensorReadingCreate(BaseModel):
    equipmentId: str = Field(..., example="EQ-12495")
    timestamp: datetime
    value: float = Field(..., example=78.42)

class SensorReadingResponse(BaseModel):
    equipment_id: str
    timestamp: datetime
    value: float
    created_at: datetime

    class Config:
        from_attributes = True

class SensorStatistics(BaseModel):
    average: Optional[float]
    minimum: Optional[float]
    maximum: Optional[float]
    count: int

class EquipmentStatisticsResponse(BaseModel):
    equipment_id: str
    statistics: SensorStatistics

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str