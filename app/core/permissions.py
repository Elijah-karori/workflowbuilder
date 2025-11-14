# =====================================================================
# FILE: app/core/permissions.py
# =====================================================================

from typing import List
from fastapi import HTTPException, status
from app.models.user import User
from app.models.workflow import WorkflowDefinition


class WorkflowPermissions:
    """Check workflow permissions based on roles and departments"""

    @staticmethod
    def can_create_workflow(user: User, department_id: int = None) -> bool:
        """Check if user can create workflows"""
        if user.role == "admin":
            return True
        
        # Managers can create workflows for their department
        if hasattr(user, "roles"):
            user_roles = [r.name for r in user.roles]
            if any(role in ["manager", "supervisor", "department_head"] for role in user_roles):
                if department_id and user.department_id == department_id:
                    return True
        
        return False

    @staticmethod
    def can_view_workflow(user: User, workflow: WorkflowDefinition) -> bool:
        """Check if user can view workflow"""
        # Admin can view all
        if user.role == "admin":
            return True
        
        # Creator can view
        if workflow.created_by == user.id:
            return True
        
        # Check department/division access
        if workflow.department_id and user.department_id == workflow.department_id:
            return True
        
        if workflow.division_id and user.division_id == workflow.division_id:
            return True
        
        # Check role-based access
        if workflow.can_view_roles:
            user_roles = [r.name for r in getattr(user, "roles", [])] or [user.role]
            if any(role in workflow.can_view_roles for role in user_roles):
                return True
        
        return False

    @staticmethod
    def can_edit_workflow(user: User, workflow: WorkflowDefinition) -> bool:
        """Check if user can edit workflow"""
        # Admin can edit all
        if user.role == "admin":
            return True
        
        # Creator can edit (if draft)
        if workflow.created_by == user.id and workflow.status == "draft":
            return True
        
        # Check role-based edit permissions
        if workflow.can_edit_roles:
            user_roles = [r.name for r in getattr(user, "roles", [])] or [user.role]
            if any(role in workflow.can_edit_roles for role in user_roles):
                return True
        
        return False

    @staticmethod
    def can_publish_workflow(user: User, workflow: WorkflowDefinition) -> bool:
        """Check if user can publish workflow"""
        # Only admins and managers can publish
        if user.role == "admin":
            return True
        
        if workflow.created_by == user.id:
            user_roles = [r.name for r in getattr(user, "roles", [])] or [user.role]
            if any(role in ["manager", "supervisor", "department_head"] for role in user_roles):
                return True
        
        return False

    @staticmethod
    def can_use_workflow(user: User, workflow: WorkflowDefinition) -> bool:
        """Check if user can initiate workflow"""
        # Must be active
        if workflow.status != "active":
            return False
        
        # Admin can use all
        if user.role == "admin":
            return True
        
        # Check role-based usage permissions
        if workflow.can_use_roles:
            user_roles = [r.name for r in getattr(user, "roles", [])] or [user.role]
            if any(role in workflow.can_use_roles for role in user_roles):
                return True
        
        # Check department access
        if workflow.department_id and user.department_id == workflow.department_id:
            return True
        
        return False