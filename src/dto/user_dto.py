from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class UserDto:
    id: Optional[int]
    email: str
    created_at: Optional[datetime] = None