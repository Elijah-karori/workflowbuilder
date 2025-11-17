# =====================================================================
# FILE: app/services/visual_workflow_service.py
# =====================================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import logging

from app.models.workflow import (
    WorkflowDefinition, WorkflowStage, WorkflowVersion, WorkflowInstance,
    NodeType, WorkflowStatus, ConditionalRoute, ApprovalType
)
from app.models.user import User

logger = logging.getLogger(__name__)


class VisualWorkflowService:
    """Service for managing visual workflow definitions"""

    # ============================================================
    # CREATE/UPDATE VISUAL WORKFLOW
    # ============================================================
    @staticmethod
    def save_workflow_graph(
        db: Session,
        workflow_id: Optional[int],
        graph_data: Dict[str, Any],
        user: User,
        description: str = None
    ):
        """Save or update visual workflow from React Flow graph"""
        
        # Validate graph structure
        VisualWorkflowService._validate_graph(graph_data)
        
        if workflow_id:
            # Update existing
            workflow = db.query(WorkflowDefinition).filter_by(id=workflow_id).first()
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
            
            # Check permissions
            if not VisualWorkflowService._can_edit(user, workflow):
                raise HTTPException(status_code=403, detail="No permission to edit workflow")
            
            # Create version backup
            db.add(WorkflowVersion(
                workflow_id=workflow.id,
                version_number=workflow.version,
                workflow_graph=workflow.workflow_graph,
                change_description=description,
                created_by=user.id
            ))
            
            # Update workflow
            workflow.workflow_graph = graph_data
            workflow.version += 1
            workflow.updated_at = datetime.utcnow()
            
        else:
            # Create new
            workflow = WorkflowDefinition(
                name=graph_data.get('name', 'New Workflow'),
                description=graph_data.get('description'),
                model_name=graph_data.get('model_name', 'GenericModel'),
                workflow_graph=graph_data,
                created_by=user.id,
                status=WorkflowStatus.draft
            )
            db.add(workflow)
            db.flush()
        
        # Convert graph to stages
        VisualWorkflowService._sync_stages_from_graph(db, workflow, graph_data)
        
        db.commit()
        db.refresh(workflow)
        return workflow

    # ============================================================
    # SYNC STAGES FROM GRAPH
    # ============================================================
    @staticmethod
    def _sync_stages_from_graph(db: Session, workflow: WorkflowDefinition, graph_data: Dict):
        """Convert React Flow nodes/edges to WorkflowStage records"""
        
        # Clear existing stages
        db.query(WorkflowStage).filter_by(workflow_id=workflow.id).delete()
        db.query(ConditionalRoute).filter(
            ConditionalRoute.from_stage_id.in_(
                db.query(WorkflowStage.id).filter_by(workflow_id=workflow.id)
            )
        ).delete()
        
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        # Create stages from nodes
        node_to_stage = {}
        for idx, node in enumerate(nodes):
            node_id = node['id']
            node_data = node.get('data', {})
            node_type = node.get('type', 'approval')
            
            stage = WorkflowStage(
                workflow_id=workflow.id,
                node_id=node_id,
                node_type=NodeType(node_type) if node_type in NodeType.__members__ else NodeType.approval,
                name=node_data.get('label', f'Stage {idx + 1}'),
                order_index=idx,
                
                # Approval config
                required_role=node_data.get('required_role'),
                required_roles=node_data.get('required_roles'),
                specific_users=node_data.get('specific_users'),
                approval_type=ApprovalType(node_data.get('approval_type', 'sequential')),
                required_approvals_count=node_data.get('required_approvals_count'),
                
                # Conditional config
                condition_field=node_data.get('condition_field'),
                condition_operator=node_data.get('condition_operator'),
                condition_value=node_data.get('condition_value'),
                
                # SLA config
                sla_hours=node_data.get('sla_hours'),
                escalation_role=node_data.get('escalation_role'),
                escalation_user_id=node_data.get('escalation_user_id'),
                auto_escalate=node_data.get('auto_escalate', False),
                
                # Notifications
                notification_template=node_data.get('notification_template'),
                custom_action=node_data.get('custom_action'),
                
                # Position
                position_x=node.get('position', {}).get('x'),
                position_y=node.get('position', {}).get('y')
            )
            
            db.add(stage)
            db.flush()
            node_to_stage[node_id] = stage
        
        # Create connections from edges
        for edge in edges:
            source_id = edge['source']
            target_id = edge['target']
            edge_data = edge.get('data', {})
            
            source_stage = node_to_stage.get(source_id)
            target_stage = node_to_stage.get(target_id)
            
            if not source_stage or not target_stage:
                continue
            
            # Check if conditional edge
            if edge_data.get('condition'):
                # Create conditional route
                db.add(ConditionalRoute(
                    from_stage_id=source_stage.id,
                    to_stage_id=target_stage.id,
                    condition_label=edge_data.get('label'),
                    condition_field=edge_data.get('condition_field'),
                    operator=edge_data.get('operator'),
                    condition_value=edge_data.get('condition_value'),
                    priority=edge_data.get('priority', 0)
                ))
            else:
                # Default next stage
                if not source_stage.next_stage_id:
                    source_stage.next_stage_id = target_stage.id

    # ============================================================
    # PUBLISH WORKFLOW
    # ============================================================
    @staticmethod
    def publish_workflow(db: Session, workflow_id: int, user: User):
        """Activate workflow for use"""
        workflow = db.query(WorkflowDefinition).filter_by(id=workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        if not VisualWorkflowService._can_edit(user, workflow):
            raise HTTPException(status_code=403, detail="No permission to publish")
        
        # Validate workflow is complete
        errors = VisualWorkflowService._validate_workflow_completeness(db, workflow)
        if errors:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot publish incomplete workflow: {', '.join(errors)}"
            )
        
        workflow.status = WorkflowStatus.active
        workflow.published_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Workflow '{workflow.name}' published by {user.full_name}")
        return workflow

    # ============================================================
    # CLONE WORKFLOW (Template)
    # ============================================================
    @staticmethod
    def clone_workflow(db: Session, workflow_id: int, new_name: str, user: User):
        """Clone existing workflow as template"""
        source = db.query(WorkflowDefinition).filter_by(id=workflow_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Source workflow not found")
        
        if not VisualWorkflowService._can_view(user, source):
            raise HTTPException(status_code=403, detail="No permission to view workflow")
        
        # Clone workflow
        cloned = WorkflowDefinition(
            name=new_name,
            description=f"Cloned from: {source.name}",
            model_name=source.model_name,
            workflow_graph=source.workflow_graph,
            created_by=user.id,
            status=WorkflowStatus.draft,
            is_template=False
        )
        db.add(cloned)
        db.flush()
        
        # Clone stages
        VisualWorkflowService._sync_stages_from_graph(db, cloned, source.workflow_graph)
        
        db.commit()
        db.refresh(cloned)
        return cloned

    # ============================================================
    # PERMISSION CHECKS
    # ============================================================
    @staticmethod
    def _can_view(user: User, workflow: WorkflowDefinition) -> bool:
        """Check if user can view workflow"""
        if user.role == "admin":
            return True
        
        user_roles = [r.name for r in getattr(user, "roles", [])] or [user.role]
        
        if workflow.can_view_roles:
            return any(role in workflow.can_view_roles for role in user_roles)
        
        return True  # Default: all can view

    @staticmethod
    def _can_edit(user: User, workflow: WorkflowDefinition) -> bool:
        """Check if user can edit workflow"""
        if user.role == "admin":
            return True
        
        if workflow.created_by == user.id:
            return True
        
        user_roles = [r.name for r in getattr(user, "roles", [])] or [user.role]
        
        if workflow.can_edit_roles:
            return any(role in workflow.can_edit_roles for role in user_roles)
        
        return False

    @staticmethod
    def _can_use(user: User, workflow: WorkflowDefinition) -> bool:
        """Check if user can initiate workflow"""
        if workflow.status != WorkflowStatus.active:
            return False
        
        if user.role == "admin":
            return True
        
        user_roles = [r.name for r in getattr(user, "roles", [])] or [user.role]
        
        if workflow.can_use_roles:
            return any(role in workflow.can_use_roles for role in user_roles)
        
        return True

    # ============================================================
    # VALIDATION
    # ============================================================
    @staticmethod
    def _validate_graph(graph_data: Dict):
        """Validate graph structure"""
        if 'nodes' not in graph_data or 'edges' not in graph_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid graph: must contain 'nodes' and 'edges'"
            )
        
        nodes = graph_data['nodes']
        if not nodes:
            raise HTTPException(status_code=400, detail="Workflow must have at least one node")
        
        # Check for start node
        has_start = any(n.get('type') == 'start' for n in nodes)
        if not has_start:
            raise HTTPException(status_code=400, detail="Workflow must have a start node")

    @staticmethod
    def _validate_workflow_completeness(db: Session, workflow: WorkflowDefinition) -> List[str]:
        """Check if workflow is ready for publishing"""
        errors = []
        
        stages = db.query(WorkflowStage).filter_by(workflow_id=workflow.id).all()
        
        if not stages:
            errors.append("No stages defined")
        
        # Check each approval stage has required role
        for stage in stages:
            if stage.node_type == NodeType.approval:
                if not stage.required_role and not stage.required_roles and not stage.specific_users:
                    errors.append(f"Stage '{stage.name}' missing required approvers")
        
        return errors

    # ============================================================
    # GET WORKFLOWS FOR USER
    # ============================================================
    @staticmethod
    def get_user_workflows(
        db: Session,
        user: User,
        filter_status: Optional[str] = None,
        filter_department: Optional[int] = None
    ):
        """Get workflows user can access"""
        query = db.query(WorkflowDefinition)
        
        # Filter by permissions
        if user.role != "admin":
            user_roles = [r.name for r in getattr(user, "roles", [])] or [user.role]
            query = query.filter(
                (WorkflowDefinition.created_by == user.id) |
                (WorkflowDefinition.can_view_roles.contains(user_roles))
            )
        
        if filter_status:
            query = query.filter(WorkflowDefinition.status == filter_status)
        
        if filter_department:
            query = query.filter(WorkflowDefinition.department_id == filter_department)
        
        return query.all()