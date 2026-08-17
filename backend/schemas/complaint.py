from pydantic import BaseModel


class ComplaintCreateRequest(BaseModel):
    title: str
    description: str
    service: str
    location: str

class ComplaintAssignRequest(BaseModel):
    technician_id: str