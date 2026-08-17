from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from database import complaints_collection
from models.complaint import Complaint
from schemas.complaint import ComplaintCreateRequest
from utils.auth import get_current_user, require_role

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("/")
def create_complaint(
    data: ComplaintCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    require_role(current_user, ["Faculty / Staff"])

    if data.service not in {"Electrical", "Plumbing"}:
        raise HTTPException(
            status_code=400,
            detail="Service must be Electrical or Plumbing",
        )

    complaint = Complaint(
        title=data.title,
        description=data.description,
        service=data.service,
        location=data.location,
        created_by=current_user["user_id"],
        status="SUBMITTED",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    result = complaints_collection.insert_one(complaint.model_dump())

    return {
        "message": "Complaint created successfully",
        "complaint_id": str(result.inserted_id),
    }

@router.get("/")
def get_complaints(
    current_user: dict = Depends(get_current_user),
):
    role = current_user["role"]

    if role == "Faculty / Staff":
        complaints = complaints_collection.find(
            {"created_by": current_user["user_id"]}
        )

    elif role in {"Service Incharge", "Technician", "Admin"}:
        complaints = complaints_collection.find()

    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = []

    for complaint in complaints:
        complaint["id"] = str(complaint["_id"])
        del complaint["_id"]
        result.append(complaint)

    return result