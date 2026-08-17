from datetime import datetime, timezone

from pydantic import BaseModel


ALLOWED_SERVICES = {
    "Electrical",
    "Plumbing",
}

ALLOWED_STATUSES = {
    "SUBMITTED",
    "ASSIGNED",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED",
    "REOPENED",
    "ESCALATED",
}


class Complaint(BaseModel):
    title: str
    description: str
    service: str
    location: str
    created_by: str
    status: str = "SUBMITTED"
    assigned_to: str | None = None
    assigned_at: datetime | None = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)