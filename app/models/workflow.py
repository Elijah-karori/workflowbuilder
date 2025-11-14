# =====================================================================
# FILE: app/models/workflow.py (Enhanced)
# =====================================================================

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime


# -------------------------------------------------------------
# ENUMS
# -------------------------------------------------------------
class WorkflowStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"
    archived = "archived"


class WorkflowActionType(str, enum.Enum):
    approve = "approve"
    reject = "reject"
    comment = "comment"
    escalate = "escalate"
    delegate = "delegate"


class NodeType(str, enum.Enum):
    start = "start"
    approval = "approval"
    condition = "condition"
    parallel = "parallel"
    end = "end"
    notification = "notification"
    action = "action"


class ApprovalType(str, enum.Enum):
    sequential = "sequential"
    parallel_all = "parallel_all"
    parallel_any = "parallel_any"
    parallel_majority = "parallel_majority"


# -------------------------------------------------------------
# WORKFLOW DEFINITIONS (Enhanced)
# -------------------------------------------------------------
class WorkflowDefinition(Base):
    """Visual workflow templates with graph structure"""
    __tablename__ = "workflow_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    model_name = Column(String, nullable=False)
    
    # ✅ NEW: Visual workflow data (React Flow format)
    workflow_graph = Column(JSON, nullable=True)
    # Structure: {"nodes": [...], "edges": [...], "viewport": {...}}
    
    # ✅ NEW: Workflow metadata
    version = Column(Integer, default=1)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.draft)
    is_template = Column(Boolean, default=False)
    
    # ✅ NEW: Access control
    created_by = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=True)
    
    # ✅ NEW: Permissions
    can_view_roles = Column(JSON, nullable=True)  # ["admin", "hr_manager"]
    can_edit_roles = Column(JSON, nullable=True)  # ["admin"]
    can_use_roles = Column(JSON, nullable=True)   # ["hr_manager", "employee"]
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    department = relationship("Department", backref="workflows")
    division = relationship("Division", backref="workflows")
    stages = relationship("WorkflowStage", back_populates="workflow", cascade="all, delete-orphan")
    instances = relationship("WorkflowInstance", back_populates="workflow")
    versions = relationship("WorkflowVersion", back_populates="workflow", cascade="all, delete-orphan")


# -------------------------------------------------------------
# WORKFLOW VERSIONS (Track changes)
# -------------------------------------------------------------
class WorkflowVersion(Base):
    """Track workflow definition changes"""
    __tablename__ = "workflow_versions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflow_definitions.id", ondelete="CASCADE"))
    version_number = Column(Integer, nullable=False)
    workflow_graph = Column(JSON, nullable=False)
    change_description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    workflow = relationship("WorkflowDefinition", back_populates="versions")
    creator = relationship("User")


# -------------------------------------------------------------
# ENHANCED WORKFLOW STAGES (From graph nodes)
# -------------------------------------------------------------
class WorkflowStage(Base):
    """Generated from workflow graph nodes"""
    __tablename__ = "workflow_stages"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflow_definitions.id", ondelete="CASCADE"))
    
    # ✅ Visual node reference
    node_id = Column(String, nullable=False)  # Matches React Flow node ID
    node_type = Column(Enum(NodeType), nullable=False)
    
    name = Column(String, nullable=False)
    order_index = Column(Integer, nullable=False)
    
    # ✅ Approval configuration
    required_role = Column(String, nullable=True)
    required_roles = Column(JSON, nullable=True)  # Multiple roles: ["hr_manager", "dept_head"]
    specific_users = Column(JSON, nullable=True)  # Specific users: [1, 2, 3]
    approval_type = Column(Enum(ApprovalType), default=ApprovalType.sequential)
    required_approvals_count = Column(Integer, nullable=True)
    
    # ✅ Conditional routing
    condition_field = Column(String, nullable=True)
    condition_operator = Column(String, nullable=True)  # >, <, ==, !=, in
    condition_value = Column(String, nullable=True)
    
    # ✅ SLA & Escalation
    sla_hours = Column(Integer, nullable=True)
    escalation_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    escalation_role = Column(String, nullable=True)
    auto_escalate = Column(Boolean, default=False)
    
    # ✅ Actions & Notifications
    notification_template = Column(String, nullable=True)
    custom_action = Column(String, nullable=True)  # Python function name
    
    # ✅ Node positioning (for visualization)
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    
    next_stage_id = Column(Integer, ForeignKey("workflow_stages.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    workflow = relationship("WorkflowDefinition", back_populates="stages")
    next_stage = relationship("WorkflowStage", remote_side=[id])
    escalation_user = relationship("User", foreign_keys=[escalation_user_id])
    instances = relationship("WorkflowInstance", back_populates="current_stage")
    stage_approvals = relationship("StageApproval", back_populates="stage")
    conditional_routes = relationship("ConditionalRoute", foreign_keys="ConditionalRoute.from_stage_id", back_populates="from_stage")


# -------------------------------------------------------------
# CONDITIONAL ROUTING
# -------------------------------------------------------------
class ConditionalRoute(Base):
    """Define conditional paths between nodes"""
    __tablename__ = "conditional_routes"

    id = Column(Integer, primary_key=True, index=True)
    from_stage_id = Column(Integer, ForeignKey("workflow_stages.id", ondelete="CASCADE"))
    to_stage_id = Column(Integer, ForeignKey("workflow_stages.id", ondelete="CASCADE"))
    
    condition_label = Column(String, nullable=True)  # "If amount > $10,000"
    condition_field = Column(String, nullable=False)
    operator = Column(String, nullable=False)
    condition_value = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    
    from_stage = relationship("WorkflowStage", foreign_keys=[from_stage_id], back_populates="conditional_routes")
    to_stage = relationship("WorkflowStage", foreign_keys=[to_stage_id])


# -------------------------------------------------------------
# STAGE APPROVALS (Parallel tracking)
# -------------------------------------------------------------
class StageApproval(Base):
    """Track individual approvals for parallel stages"""
    __tablename__ = "stage_approvals"

    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, ForeignKey("workflow_instances.id", ondelete="CASCADE"))
    stage_id = Column(Integer, ForeignKey("workflow_stages.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(Enum(WorkflowActionType), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    instance = relationship("WorkflowInstance")
    stage = relationship("WorkflowStage", back_populates="stage_approvals")
    user = relationship("User")


# -------------------------------------------------------------
# WORKFLOW INSTANCES (Enhanced)
# -------------------------------------------------------------
class WorkflowInstance(Base):
    """Runtime instance of a workflow"""
    __tablename__ = "workflow_instances"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflow_definitions.id", ondelete="CASCADE"))
    workflow_version = Column(Integer, default=1)
    
    related_model = Column(String, nullable=False)
    related_id = Column(Integer, nullable=False)
    
    current_stage_id = Column(Integer, ForeignKey("workflow_stages.id", ondelete="SET NULL"))
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.pending)
    
    initiated_by = Column(Integer, ForeignKey("users.id"))
    
    # ✅ NEW: Track execution path
    execution_path = Column(JSON, nullable=True)  # [stage_id1, stage_id2, ...]
    
    # ✅ NEW: Context data for conditions
    context_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    workflow = relationship("WorkflowDefinition", back_populates="instances")
    current_stage = relationship("WorkflowStage", back_populates="instances")
    actions = relationship("WorkflowAction", back_populates="instance", cascade="all, delete-orphan")
    initiator = relationship("User", foreign_keys=[initiated_by])


# -------------------------------------------------------------
# WORKFLOW ACTIONS (Audit trail)
# -------------------------------------------------------------
class WorkflowAction(Base):
    """Audit trail of all workflow actions"""
    __tablename__ = "workflow_actions"

    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, ForeignKey("workflow_instances.id", ondelete="CASCADE"))
    stage_id = Column(Integer, ForeignKey("workflow_stages.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(Enum(WorkflowActionType), nullable=False)
    comment = Column(Text, nullable=True)
    
    # ✅ NEW: Additional metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    instance = relationship("WorkflowInstance", back_populates="actions")
    stage = relationship("WorkflowStage")
    user = relationship("User")

