from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    password_hash: str
    role: str
    service: str | None = None
    created_at: datetime = datetime.utcnow()