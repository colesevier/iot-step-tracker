# server/models.py
from pydantic import BaseModel
from datetime import datetime


class StepData(BaseModel):
    device_id: str
    steps: int
    timestamp: datetime
