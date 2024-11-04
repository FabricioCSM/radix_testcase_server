from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from .db_models import SensorReading
from typing import List, Dict, Any

class SensorQueries:

    @staticmethod
    async def get_all_readings(db: Session) -> List[SensorReading]:
        readings = db.query(SensorReading).all()
        return readings

    @staticmethod
    async def get_unique_equipment_ids(db: Session) -> List[str]:
        equipment_ids = db.query(SensorReading.equipment_id).distinct().all()
        return [id_[0] for id_ in equipment_ids] 

    @staticmethod
    async def create_reading(db: Session, reading: Dict[str, Any]) -> SensorReading:
        db_reading = SensorReading(
            equipment_id=reading["equipment_id"],
            timestamp=reading["timestamp"],
            value=reading["value"]
        )
        db.add(db_reading)
        db.commit()
        db.refresh(db_reading)
        return db_reading

    @staticmethod
    async def get_readings_by_equipment(
        db: Session, 
        equipment_id: str, 
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 100
    ) -> List[SensorReading]:
        query = db.query(SensorReading)\
            .filter(SensorReading.equipment_id == equipment_id)
        
        if start_time:
            query = query.filter(SensorReading.timestamp >= start_time)
        if end_time:
            query = query.filter(SensorReading.timestamp <= end_time)
            
        return query.order_by(SensorReading.timestamp.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    async def get_equipment_statistics(
        db: Session,
        equipment_id: str,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, float]:
        start_time = datetime.utcnow() - time_window
        
        result = db.query(
            func.avg(SensorReading.value).label('average'),
            func.min(SensorReading.value).label('minimum'),
            func.max(SensorReading.value).label('maximum'),
            func.count(SensorReading.value).label('count')
        ).filter(
            SensorReading.equipment_id == equipment_id,
            SensorReading.timestamp >= start_time
        ).first()
        
        return {
            'average': float(result.average) if result.average else 0.0,
            'minimum': float(result.minimum) if result.minimum else 0.0,
            'maximum': float(result.maximum) if result.maximum else 0.0,
            'count': int(result.count) if result.count else 0
        }
    
    async def update_or_insert_reading_value(db_session: Session, equipment_id: str, timestamp: str, new_value: float):
        try:
            reading = db_session.query(SensorReading).filter(
                SensorReading.equipment_id == equipment_id,
                SensorReading.timestamp == timestamp
            ).first()

            if reading:
                reading.value = new_value
                db_session.commit()
                return True
            else:
                new_reading = SensorReading(
                    equipment_id=equipment_id,
                    timestamp=timestamp,
                    value=new_value
                )
                db_session.add(new_reading)
                db_session.commit()
                return True
        except IntegrityError as e:
            db_session.rollback()
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            db_session.rollback()
            raise Exception(f"Error updating or inserting reading: {str(e)}")