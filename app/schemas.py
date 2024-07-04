from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class Visit(BaseModel):
    venue_type: str
    ts: datetime

class UsersData(BaseModel):
    data: Dict[str, List[Visit]]