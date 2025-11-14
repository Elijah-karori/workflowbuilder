from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db
from app.core.deps import get_current_user, require_hybrid_auth
from app.models.user import User
from app.models.abac import ABACPolicy, PolicyEffect
from app.services.abac_service import ABACService
from app.schemas.abac import (
    PolicyCreate, PolicyUpdate, PolicyResponse,
    AccessCheckRequest, AccessCheckResponse,
    AuditLogResponse
)

router = APIRouter()


# ============================================================
# POLICY MANAGEMENT
# ============================================================
@router.get("/policies", response_model=List[PolicyResponse])
def list_policies(
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorized: bool = Depends(require_hybrid_auth(roles=["admin", "security_admin"]))
):
    """List all ABAC policies"""
    query = db.query(ABACPolicy)
    
    if resource_type:
        query = query.filter(ABACPolicy.resource_type == resource_type)
    if action:
        query = query.filter(ABACPolicy.action == action)
    if is_active is not None:
        query = query.filter(ABACPolicy.is_active == is_active)
    
    return query.order_by(ABACPolicy.priority.desc()).all()


@router.post("/policies", response_model=PolicyResponse)
def create_policy(
    data: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorized: bool = Depends(require_hybrid_auth(roles=["admin", "security_admin"]))
):
    """Create new ABAC policy"""
    policy = ABACService.create_policy(
        db=db,
        name=data.name,
        action=data.action,
        resource_type=data.resource_type,
        effect=data.effect,
        conditions=data.conditions,
        user=current_user,
        description=data.description,
        priority=data.priority,
        department_ids=data.department_ids,
        division_ids=data.division_ids,
        role_requirements=data.role_requirements
    )
    return policy


@router.put("/policies/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: int,
    data: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorized: bool = Depends(require_hybrid_auth(roles=["admin", "security_admin"]))
):
    """Update existing ABAC policy"""
    policy = ABACService.update_policy(
        db=db,
        policy_id=policy_id,
        **data.dict(exclude_unset=True)
    )
    return policy


@router.delete("/policies/{policy_id}")
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorized: bool = Depends(require_hybrid_auth(roles=["admin"]))
):
    """Delete ABAC policy"""
    policy = db.query(ABACPolicy).filter_by(id=policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    db.delete(policy)
    db.commit()
    return {"message": "Policy deleted successfully"}


# ============================================================
# ACCESS CHECKING (Testing/Development)
# ============================================================
@router.post("/check-access", response_model=AccessCheckResponse)
def check_access(
    data: AccessCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if current user has access to perform action on resource"""
    allowed, reason, policy = ABACService.check_access(
        db=db,
        user=current_user,
        action=data.action,
        resource_type=data.resource_type,
        resource_id=data.resource_id,
        context=data.context
    )
    
    return AccessCheckResponse(
        allowed=allowed,
        reason=reason,
        policy_id=policy.id if policy else None,
        policy_name=policy.name if policy else None
    )


# ============================================================
# AUDIT LOGS
# ============================================================
@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    decision: Optional[str] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorized: bool = Depends(require_hybrid_auth(roles=["admin", "security_admin", "auditor"]))
):
    """Get ABAC access audit logs"""
    from app.models.abac import ABACAccessLog
    
    query = db.query(ABACAccessLog)
    
    if user_id:
        query = query.filter(ABACAccessLog.user_id == user_id)
    if resource_type:
        query = query.filter(ABACAccessLog.resource_type == resource_type)
    if action:
        query = query.filter(ABACAccessLog.action == action)
    if decision:
        query = query.filter(ABACAccessLog.decision == decision)
    
    return query.order_by(ABACAccessLog.created_at.desc()).limit(limit).all()


# ============================================================
# USER ATTRIBUTES MANAGEMENT
# ============================================================
@router.get("/users/{user_id}/attributes")
def get_user_attributes(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorized: bool = Depends(require_hybrid_auth(roles=["admin", "hr_manager"]))
):
    """Get user ABAC attributes"""
    from app.models.abac import UserAttribute
    
    user_attr = db.query(UserAttribute).filter_by(user_id=user_id).first()
    if not user_attr:
        raise HTTPException(status_code=404, detail="User attributes not found")
    
    return user_attr


@router.put("/users/{user_id}/attributes")
def update_user_attributes(
    user_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorized: bool = Depends(require_hybrid_auth(roles=["admin", "hr_manager"]))
):
    """Update user ABAC attributes"""
    from app.models.abac import UserAttribute
    
    user_attr = db.query(UserAttribute).filter_by(user_id=user_id).first()
    
    if not user_attr:
        user_attr = UserAttribute(user_id=user_id)
        db.add(user_attr)
    
    for key, value in data.items():
        if hasattr(user_attr, key):
            setattr(user_attr, key, value)
    
    db.commit()
    db.refresh(user_attr)
    return user_attr