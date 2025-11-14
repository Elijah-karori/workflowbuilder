from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, Boolean,
    DateTime, JSON, Enum as SQLEnum, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime


# -------------------------------------------------------------
# ENUMS
# -------------------------------------------------------------
class PolicyEffect(str, enum.Enum):
    allow = "allow"
    deny = "deny"


class ConditionOperator(str, enum.Enum):
    eq = "eq"              # Equal
    ne = "ne"              # Not equal
    gt = "gt"              # Greater than
    gte = "gte"            # Greater than or equal
    lt = "lt"              # Less than
    lte = "lte"            # Less than or equal
    in_ = "in"             # In list
    not_in = "not_in"      # Not in list
    contains = "contains"  # Contains substring
    starts_with = "starts_with"
    ends_with = "ends_with"
    between = "between"    # Between two values
    is_null = "is_null"
    is_not_null = "is_not_null"


class AttributeType(str, enum.Enum):
    user = "user"
    resource = "resource"
    environment = "environment"


# -------------------------------------------------------------
# ABAC POLICIES
# -------------------------------------------------------------
class ABACPolicy(Base):
    """Define attribute-based access control policies"""
    __tablename__ = "abac_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Policy definition
    effect = Column(SQLEnum(PolicyEffect), nullable=False, default=PolicyEffect.allow)
    priority = Column(Integer, default=0)  # Higher priority policies evaluated first
    
    # Action and Resource
    action = Column(String, nullable=False, index=True)  # e.g., "read", "approve", "delete"
    resource_type = Column(String, nullable=False, index=True)  # e.g., "invoice", "employee"
    
    # Conditions (JSON structure)
    conditions = Column(JSON, nullable=True)
    """
    Example structure:
    {
        "all": [  # All conditions must match (AND)
            {
                "attribute": "user.department_id",
                "operator": "eq",
                "value": "{{resource.department_id}}"
            },
            {
                "attribute": "resource.amount",
                "operator": "lte",
                "value": 10000
            }
        ]
    }
    OR:
    {
        "any": [  # Any condition must match (OR)
            {"attribute": "user.role", "operator": "eq", "value": "admin"},
            {"attribute": "user.is_superuser", "operator": "eq", "value": true}
        ]
    }
    """
    
    # Scope limitations
    department_ids = Column(JSON, nullable=True)  # [1, 2, 3] or null for all
    division_ids = Column(JSON, nullable=True)
    role_requirements = Column(JSON, nullable=True)  # ["manager", "supervisor"]
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    audit_logs = relationship("ABACAccessLog", back_populates="policy")


# -------------------------------------------------------------
# RESOURCE ATTRIBUTES (Dynamic metadata)
# -------------------------------------------------------------
class ResourceAttribute(Base):
    """Store dynamic attributes for resources"""
    __tablename__ = "resource_attributes"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String, nullable=False, index=True)
    resource_id = Column(Integer, nullable=False, index=True)
    
    attribute_name = Column(String, nullable=False, index=True)
    attribute_value = Column(Text, nullable=True)
    attribute_type = Column(String, nullable=False)  # string, number, boolean, json
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


# -------------------------------------------------------------
# ABAC AUDIT LOG
# -------------------------------------------------------------
class ABACAccessLog(Base):
    """Audit trail for all ABAC access decisions"""
    __tablename__ = "abac_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Request details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    
    # Decision
    decision = Column(String, nullable=False)  # "allow" or "deny"
    policy_id = Column(Integer, ForeignKey("abac_policies.id"), nullable=True)
    
    # Context
    user_attributes = Column(JSON, nullable=True)
    resource_attributes = Column(JSON, nullable=True)
    environment_attributes = Column(JSON, nullable=True)
    
    # Evaluation details
    evaluated_policies = Column(JSON, nullable=True)  # List of policy IDs evaluated
    evaluation_time_ms = Column(Integer, nullable=True)
    reason = Column(Text, nullable=True)
    
    # Request metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    endpoint = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", backref="abac_access_logs")
    policy = relationship("ABACPolicy", back_populates="audit_logs")


# -------------------------------------------------------------
# USER ATTRIBUTES (Extended profile)
# -------------------------------------------------------------
class UserAttribute(Base):
    """Extended user attributes for ABAC"""
    __tablename__ = "user_attributes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Organizational attributes
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=True, index=True)
    team_id = Column(Integer, nullable=True, index=True)
    
    # Position attributes
    job_title = Column(String, nullable=True)
    job_level = Column(Integer, nullable=True)  # 1=junior, 5=senior, 10=executive
    cost_center = Column(String, nullable=True)
    
    # Approval limits
    approval_limit_amount = Column(Integer, nullable=True)
    can_approve_own_department = Column(Boolean, default=False)
    can_approve_all_departments = Column(Boolean, default=False)
    
    # Custom attributes (JSON for flexibility)
    custom_attributes = Column(JSON, nullable=True)
    """
    Example:
    {
        "clearance_level": "confidential",
        "certifications": ["PMP", "CPA"],
        "languages": ["en", "es"]
    }
    """
    
    # Location
    office_location = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="abac_attributes")
    department = relationship("Department")
    division = relationship("Division")


# -------------------------------------------------------------
# POLICY TEMPLATES
# -------------------------------------------------------------
class PolicyTemplate(Base):
    """Pre-defined policy templates for common scenarios"""
    __tablename__ = "policy_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True, index=True)  # "finance", "hr", "workflow"
    
    template_config = Column(JSON, nullable=False)
    """
    Template structure with placeholders:
    {
        "action": "approve",
        "resource_type": "{{resource_type}}",
        "conditions": {
            "all": [
                {"attribute": "user.department_id", "operator": "eq", "value": "{{user.department_id}}"}
            ]
        }
    }
    """
    
    required_parameters = Column(JSON, nullable=True)  # ["resource_type", "max_amount"]
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)