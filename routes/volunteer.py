from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List


from database import get_db
from schemas.volunteer import (
    VolunteerCreate, VolunteerResponse, VolunteerAvailabilityUpdate,
    AssignmentCreate, AssignmentResponse, AssignmentStatusUpdate,
    ResourceCreate, ResourceResponse, ResourceUpdate
)
from services.volunteer_service import (
    register_volunteer, get_all_volunteers, update_volunteer_availability,
    assign_volunteer, get_all_assignments, update_task_status,
    manage_resources
)
from services.auth_service import get_current_user

router = APIRouter(prefix="/volunteers", tags=["Volunteers & Resources"])


# ── VOLUNTEERS ──

@router.post("/register", response_model=VolunteerResponse, status_code=201)
def register(
    data: VolunteerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    POST /volunteers/register
    Logged-in user registers themselves as a volunteer.
    """
    return register_volunteer(
        user_id=current_user.id,
        skills=data.skills,
        db=db
    )


@router.get("/", response_model=List[VolunteerResponse])
def list_volunteers(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """GET /volunteers/ — All registered volunteers. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return get_all_volunteers(db)


@router.patch("/{volunteer_id}/availability", response_model=VolunteerResponse)
def toggle_availability(
    volunteer_id: int,
    data: VolunteerAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """PATCH /volunteers/{id}/availability — Update volunteer availability."""
    return update_volunteer_availability(volunteer_id, data.availability, db)


# ── ASSIGNMENTS ──

@router.post("/assign", response_model=AssignmentResponse, status_code=201)
def assign(
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    POST /volunteers/assign
    Admin assigns a volunteer to a help request.
    Requires: Admin role.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return assign_volunteer(data.volunteer_id, data.request_id, db)


@router.get("/assignments", response_model=List[AssignmentResponse])
def list_assignments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """GET /volunteers/assignments — All assignments. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return get_all_assignments(db)


@router.patch("/assignments/{assignment_id}/status", response_model=AssignmentResponse)
def task_status(
    assignment_id: int,
    data: AssignmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """PATCH /volunteers/assignments/{id}/status — Update task status."""
    return update_task_status(assignment_id, data.status, db)


# ── RESOURCES ──

@router.post("/resources", response_model=ResourceResponse, status_code=201)
def create_resource(
    data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """POST /volunteers/resources — Add a new resource. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return manage_resources("create", db, resource_data=data.model_dump())


@router.get("/resources", response_model=List[ResourceResponse])
def list_resources(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """GET /volunteers/resources — All resources."""
    return manage_resources("list", db)


@router.patch("/resources/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """PATCH /volunteers/resources/{id} — Update resource quantity. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return manage_resources("update", db, resource_id=resource_id, quantity=data.quantity)


@router.delete("/resources/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """DELETE /volunteers/resources/{id} — Remove a resource. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return manage_resources("delete", db, resource_id=resource_id)