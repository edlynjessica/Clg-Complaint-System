from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from bson import ObjectId
from database import complaints_collection, users_collection
from models.complaint import Complaint
from schemas.complaint import ComplaintCreateRequest, ComplaintAssignRequest
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

    elif role == "Service Incharge":
        incharge = users_collection.find_one(
            {"_id": ObjectId(current_user["user_id"])}
        )

        if not incharge:
            raise HTTPException(status_code=404, detail="Incharge not found")

        service = incharge.get("service")

        if service not in {"Electrical", "Plumbing"}:
            raise HTTPException(
                status_code=400,
                detail="Incharge service is not configured",
            )

        complaints = complaints_collection.find(
            {"service": service}
        )

    elif role == "Technician":
        complaints = complaints_collection.find(
            {"assigned_to": current_user["user_id"]}
        )

    elif role == "Admin":
        complaints = complaints_collection.find()

    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = []

    for complaint in complaints:
        complaint["id"] = str(complaint["_id"])
        del complaint["_id"]
        result.append(complaint)

    return result

from datetime import datetime, timezone

from bson import ObjectId

@router.patch("/{complaint_id}/assign")
def assign_technician(
    complaint_id: str,
    data: ComplaintAssignRequest,
    current_user: dict = Depends(get_current_user),
):
    require_role(current_user, ["Service Incharge"])

    technician = users_collection.find_one(
        {
            "_id": ObjectId(data.technician_id),
            "role": "Technician",
        }
    )

    if not technician:
        raise HTTPException(status_code=404, detail="Technician not found")

    if technician.get("service") is None:
        raise HTTPException(
            status_code=400,
            detail="Technician service is not configured",
        )

    complaint = complaints_collection.find_one(
        {"_id": ObjectId(complaint_id)}
    )

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint["service"] != technician["service"]:
        raise HTTPException(
            status_code=400,
            detail="Technician service does not match complaint service",
        )

    now = datetime.now(timezone.utc)

    complaints_collection.update_one(
        {"_id": ObjectId(complaint_id)},
        {
            "$set": {
                "assigned_to": data.technician_id,
                "assigned_at": now,
                "status": "ASSIGNED",
                "updated_at": now,
            }
        },
    )

    return {
        "message": "Technician assigned successfully",
        "complaint_id": complaint_id,
        "technician_id": data.technician_id,
        "status": "ASSIGNED",
    }

@router.patch("/{complaint_id}/status")
def update_status(
    complaint_id: str,
    status: str,
    current_user: dict = Depends(get_current_user),
):
    role = current_user["role"]

    allowed_statuses = {
        "IN_PROGRESS",
        "RESOLVED",
        "REOPENED",
        "CLOSED",
    }

    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    complaint = complaints_collection.find_one(
        {"_id": ObjectId(complaint_id)}
    )

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    current_status = complaint["status"]

    if role == "Technician":
        if complaint.get("assigned_to") != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Complaint is not assigned to you",
            )

        if status not in {"IN_PROGRESS", "RESOLVED"}:
            raise HTTPException(
                status_code=403,
                detail="Technician cannot set this status",
            )

    elif role == "Faculty / Staff":
        if complaint["created_by"] != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You can only verify your own complaints",
            )

        if status not in {"CLOSED", "REOPENED"}:
            raise HTTPException(
                status_code=403,
                detail="Faculty / Staff cannot set this status",
            )

        if current_status != "RESOLVED":
            raise HTTPException(
                status_code=400,
                detail="Complaint must be RESOLVED first",
            )

    else:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions",
        )

    valid_transitions = {
        "ASSIGNED": {"IN_PROGRESS"},
        "IN_PROGRESS": {"RESOLVED"},
        "RESOLVED": {"CLOSED", "REOPENED"},
        "REOPENED": {"IN_PROGRESS"},
    }

    if status not in valid_transitions.get(current_status, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current_status} to {status}",
        )

    now = datetime.now(timezone.utc)

    complaints_collection.update_one(
        {"_id": ObjectId(complaint_id)},
        {
            "$set": {
                "status": status,
                "updated_at": now,
            }
        },
    )

    return {
        "message": "Complaint status updated successfully",
        "complaint_id": complaint_id,
        "status": status,
    }

@router.get("/stats")
def get_complaint_stats(
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    complaints = list(complaints_collection.find())

    total = len(complaints)

    pending = sum(
        1 for complaint in complaints
        if complaint.get("status") in {"SUBMITTED", "ASSIGNED", "REOPENED"}
    )

    in_progress = sum(
        1 for complaint in complaints
        if complaint.get("status") == "IN_PROGRESS"
    )

    resolved = sum(
    1 for complaint in complaints
    if complaint.get("status") == "RESOLVED"
)

    closed = sum(
        1 for complaint in complaints
        if complaint.get("status") == "CLOSED"
    )

    electrical = sum(
        1 for complaint in complaints
        if complaint.get("service") == "Electrical"
    )

    plumbing = sum(
        1 for complaint in complaints
        if complaint.get("service") == "Plumbing"
    )
    escalated = sum(
        1 for complaint in complaints
        if complaint.get("status") == "ESCALATED"
    )

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": closed,
        "electrical": electrical,
        "plumbing": plumbing,
        "escalated": escalated,
        "overdue": 0,
    }

@router.patch("/{complaint_id}/escalate")
def escalate_complaint(
    complaint_id: str,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] not in {"Service Incharge", "Admin"}:
        raise HTTPException(
            status_code=403,
            detail="Only Incharge or Admin can escalate complaints",
        )

    complaint = complaints_collection.find_one(
        {"_id": ObjectId(complaint_id)}
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    if complaint.get("status") == "CLOSED":
        raise HTTPException(
            status_code=400,
            detail="Closed complaints cannot be escalated",
        )

    complaints_collection.update_one(
        {"_id": ObjectId(complaint_id)},
        {
            "$set": {
                "status": "ESCALATED",
                "escalated_by": current_user["user_id"],
                "escalated_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        },
    )

    return {
        "message": "Complaint escalated successfully",
        "complaint_id": complaint_id,
        "status": "ESCALATED",
    }