# =====================================================================
# FILE: app/api/v1/endpoints/workflows.py
# =====================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.workflow import WorkflowDefinition, WorkflowStatus
from app.services.visual_workflow_service import VisualWorkflowService
from app.schemas.workflow import (
    WorkflowDefinitionResponse,
    WorkflowGraphCreate,
    WorkflowGraphUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[WorkflowDefinitionResponse])
def get_workflows(
    status_filter: Optional[str] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all workflows user can access"""
    workflows = VisualWorkflowService.get_user_workflows(
        db, current_user, status_filter, department_id
    )
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowDefinitionResponse)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single workflow with graph data"""
    workflow = db.query(WorkflowDefinition).filter_by(id=workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if not VisualWorkflowService._can_view(current_user, workflow):
        raise HTTPException(status_code=403, detail="No permission to view")
    
    return workflow


@router.post("/graph", response_model=WorkflowDefinitionResponse)
def create_workflow_graph(
    data: WorkflowGraphCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new workflow from graph"""
    workflow = VisualWorkflowService.save_workflow_graph(
        db,
        workflow_id=None,
        graph_data=data.dict(),
        user=current_user,
    )
    return workflow


@router.put("/{workflow_id}/graph", response_model=WorkflowDefinitionResponse)
def update_workflow_graph(
    workflow_id: int,
    data: WorkflowGraphUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update existing workflow graph"""
    workflow = VisualWorkflowService.save_workflow_graph(
        db,
        workflow_id=workflow_id,
        graph_data=data.dict(),
        user=current_user,
        description=data.change_description,
    )
    return workflow


@router.post("/{workflow_id}/publish", response_model=WorkflowDefinitionResponse)
def publish_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publish workflow to make it active"""
    workflow = VisualWorkflowService.publish_workflow(db, workflow_id, current_user)
    return workflow


@router.post("/{workflow_id}/clone", response_model=WorkflowDefinitionResponse)
def clone_workflow(
    workflow_id: int,
    new_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clone existing workflow"""
    workflow = VisualWorkflowService.clone_workflow(db, workflow_id, new_name, current_user)
    return workflow


@router.get("/{workflow_id}/versions")
def get_workflow_versions(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get version history"""
    workflow = db.query(WorkflowDefinition).filter_by(id=workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if not VisualWorkflowService._can_view(current_user, workflow):
        raise HTTPException(status_code=403, detail="No permission")
    
    return workflow.versions


@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete workflow (admin only)"""
    workflow = db.query(WorkflowDefinition).filter_by(id=workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if not current_user.role == "admin" and workflow.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to delete")
    
    db.delete(workflow)
    db.commit()
    return {"message": "Workflow deleted successfully"}