from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    effect: str = Field(..., pattern="^(allow|deny)$")
    priority: int = 0
    action: str
    resource_type: str
    conditions: Optional[Dict[str, Any]] = None
    department_ids: Optional[List[int]] = None
    division_ids: Optional[List[int]] = None
    role_requirements: Optional[List[str]] = None


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    effect: Optional[str] = Field(None, pattern="^(allow|deny)$")
    priority: Optional[int] = None
    conditions: Optional[Dict[str, Any]] = None
    department_ids: Optional[List[int]] = None
    division_ids: Optional[List[int]] = None
    role_requirements: Optional[List[str]] = None
    is_active: Optional[bool] = None


class PolicyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    effect: str
    priority: int
    action: str
    resource_type: str
    conditions: Optional[Dict[str, Any]]
    department_ids: Optional[List[int]]
    division_ids: Optional[List[int]]
    role_requirements: Optional[List[str]]
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AccessCheckRequest(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


class AccessCheckResponse(BaseModel):
    allowed: bool
    reason: str
    policy_id: Optional[int] = None
    policy_name: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    resource_type: str
    resource_id: Optional[int]
    decision: str
    policy_id: Optional[int]
    reason: Optional[str]
    evaluation_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class UserAttributeUpdate(BaseModel):
    department_id: Optional[int] = None
    division_id: Optional[int] = None
    team_id: Optional[int] = None
    job_title: Optional[str] = None
    job_level: Optional[int] = None
    approval_limit_amount: Optional[int] = None
    can_approve_own_department: Optional[bool] = None
    can_approve_all_departments: Optional[bool] = None
    office_location: Optional[str] = None
    country_code: Optional[str] = None
    custom_attributes: Optional[Dict[str, Any]] = None