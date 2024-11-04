from fastapi import FastAPI, Header, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.db_engine import db
import pandas as pd
from io import BytesIO
from statistics import mean
from collections import defaultdict
from database.queries import SensorQueries
from database.db_models import SensorReading, User
from auth.auth import create_access_token, decode_access_token
from sample_data import sample_data
from api_models.sensor_model import SensorReadingCreate, SensorReadingResponse, SensorStatistics, EquipmentStatisticsResponse, CreateUserRequest, LoginRequest
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from passlib.context import CryptContext 
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],   
)

@app.on_event("startup")
def startup_event():
    with next(db.get_session()) as db_session:
        initialize_sample_data(db_session)

def get_db():
    db_session = next(db.get_session())
    try:
        yield db_session
    finally:
        db_session.close()

def initialize_sample_data(db_session: Session):
    if db_session.query(SensorReading).count() == 0:
        sensor_readings = [
            SensorReading(
                equipment_id=entry["equipment_id"],
                timestamp=datetime.fromisoformat(entry["timestamp"]),
                value=entry["value"],
                created_at=datetime.fromisoformat(entry["created_at"])
            )
            for entry in sample_data
        ]
        
        db_session.bulk_save_objects(sensor_readings)
        db_session.commit()
        
        logger.info("Sample data initialized.")
    else:
        logger.info("Database already contains data; skipping initialization.")

async def get_current_user(token: str = Depends(decode_access_token)):
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

@app.get("/sensor-data/equipment-ids", response_model=List[str],
            summary="Retrieve unique equipment IDs",
            description="Fetch all unique equipment IDs that have recorded sensor readings.")
async def get_all_equipment_ids(
    authorization: str = Header(None),
    db_session: Session = Depends(get_db)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing or invalid")

    access_token = authorization.split(" ")[1]
    await decode_access_token(access_token)
    
    try:
        equipment_ids = await SensorQueries.get_unique_equipment_ids(db_session)
        return equipment_ids
    except Exception as e:
        logger.error(f"Error retrieving unique equipment IDs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/sensor-data/all", response_model=List[SensorReadingResponse],
            summary="Retrieve all recorded sensor readings",
            description="Fetch all recorded sensor readings.")
async def get_all_sensor_readings(
    authorization: str = Header(None),
    db_session: Session = Depends(get_db)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing or invalid")

    access_token = authorization.split(" ")[1]
    await decode_access_token(access_token)
    
    try:
        readings = await SensorQueries.get_all_readings(db_session)
        return readings
    except Exception as e:
        logger.error(f"Error retrieving all sensor readings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/sensor-data/{equipment_id}", response_model=List[SensorReadingResponse], 
            summary="Retrieve sensor readings by equipment ID",
            description="Fetch sensor readings for a specific equipment ID, with optional time filtering.")
async def get_sensor_readings(
    equipment_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    authorization: str = Header(None),
    db_session: Session = Depends(get_db)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing or invalid")

    access_token = authorization.split(" ")[1]
    await decode_access_token(access_token)
    
    try:
        readings = await SensorQueries.get_readings_by_equipment(
            db_session,
            equipment_id,
            start_time,
            end_time,
            limit
        )
        return readings
    except Exception as e:
        logger.error(f"Error retrieving sensor readings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/sensor-data/statistics/{time_period}", response_model=List[EquipmentStatisticsResponse],
                summary="Retrieve sensor readings statistics by time period and equipment_id as optional",
                description="Fetch sensor readings statistics for a specific time period, with optional equipment_id.")
async def get_sensor_statistics(
    time_period: int,
    authorization: str = Header(None)
) -> List[EquipmentStatisticsResponse]:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing or invalid")

    access_token = authorization.split(" ")[1]
    await decode_access_token(access_token)

    end_time = datetime.now()
    start_time = end_time - timedelta(hours=time_period)
    equipment_stats = defaultdict(list)

    for record in sample_data:
        timestamp = datetime.fromisoformat(record['timestamp'])
        if start_time <= timestamp <= end_time:
            equipment_stats[record['equipment_id']].append(record['value'])

    if not equipment_stats:
        raise HTTPException(status_code=404, detail="No data available for the specified time period.")

    statistics_list = [
        EquipmentStatisticsResponse(
            equipment_id=equipment_id,
            statistics=SensorStatistics(
                average=mean(values),
                minimum=min(values),
                maximum=max(values),
                count=len(values)
            )
        )
        for equipment_id, values in equipment_stats.items()
    ]

    return statistics_list

@app.post("/sensor-data/", response_model=dict, status_code=201, 
            summary="Create a new sensor reading",
            description="Create a new sensor reading by providing equipment ID, timestamp, and value.")
async def create_sensor_reading(
    reading: SensorReadingCreate,
    authorization: str = Header(None),
    db_session: Session = Depends(get_db)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing or invalid")

    access_token = authorization.split(" ")[1]
    await decode_access_token(access_token)
    
    try:
        await SensorQueries.create_reading(db_session, {
            "equipment_id": reading.equipmentId,
            "timestamp": reading.timestamp,
            "value": reading.value
        })
        return {"status": "success", "message": "Reading stored successfully"}
    except Exception as e:
        logger.error(f"Error creating sensor reading: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/signup/user/", summary="Create a new user", description="Create a new user with a name, email, and password.")
async def create_user(user_data: CreateUserRequest, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user_data.password)
    
    try:
        user = User(name=user_data.name, email=user_data.email, password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"id": user.id, "name": user.name, "email": user.email}
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=400, detail="Error creating user")

@app.post("/token", summary="Login user and return access token")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not pwd_context.verify(login_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=90)
    access_token = create_access_token(
        data={"sub": user.email, "name": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/sensor-data/update-values/", 
           summary="Update sensor values from CSV",
           description="Upload a CSV file to update sensor values for a specific equipment ID.")
async def update_sensor_values(
    file: UploadFile = File(...),
    authorization: str = Header(None),
    db_session: Session = Depends(get_db)
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing or invalid")

    access_token = authorization.split(" ")[1]
    await decode_access_token(access_token)
    
    try:
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))
        required_columns = {'equipmentId', 'timestamp', 'value'}

        for _, row in df.iterrows():
            equipment_id = row['equipmentId']
            timestamp = row['timestamp']
            value = row['value']
            print(equipment_id, timestamp, value)
            result = await SensorQueries.update_or_insert_reading_value(db_session, equipment_id, timestamp, value)

            if not result:
                logger.warning(f"No update or insert performed for equipment ID {equipment_id} at timestamp {timestamp}")

        return {"status": "success", "message": "Sensor values updated successfully"}
    
    except Exception as e:
        logger.error(f"Error updating sensor values: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)