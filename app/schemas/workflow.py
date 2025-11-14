# =====================================================================
# FILE: app/schemas/workflow.py (Additional schemas)
# =====================================================================

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class NodeData(BaseModel):
    label: str
    required_role: Optional[str] = None
    required_roles: Optional[List[str]] = None
    specific_users: Optional[List[int]] = None
    approval_type: Optional[str] = "sequential"
    required_approvals_count: Optional[int] = None
    condition_field: Optional[str] = None
    condition_operator: Optional[str] = None
    condition_value: Optional[str] = None
    sla_hours: Optional[int] = None
    escalation_role: Optional[str] = None
    escalation_user_id: Optional[int] = None
    auto_escalate: Optional[bool] = False
    notification_template: Optional[str] = None
    custom_action: Optional[str] = None


class ReactFlowNode(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: NodeData


class ReactFlowEdge(BaseModel):
    id: str
    source: str
    target: str
    type: Optional[str] = "smoothstep"
    animated: Optional[bool] = False
    data: Optional[Dict[str, Any]] = None


class WorkflowGraphCreate(BaseModel):
    name: str
    description: Optional[str] = None
    model_name: str
    nodes: List[ReactFlowNode]
    edges: List[ReactFlowEdge]
    viewport: Optional[Dict[str, Any]] = None
    can_view_roles: Optional[List[str]] = None
    can_edit_roles: Optional[List[str]] = None
    can_use_roles: Optional[List[str]] = None


class WorkflowGraphUpdate(WorkflowGraphCreate):
    change_description: Optional[str] = None


class WorkflowDefinitionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    model_name: str
    workflow_graph: Optional[Dict[str, Any]]
    version: int
    status: str
    is_template: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]

    class Config:
        from_attributes = True