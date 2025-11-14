from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List, Callable, Tuple
from functools import wraps

from app.core.database import SessionLocal
from app.models.user import User
from app.services.abac_service import ABACService


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Placeholder for authentication - replace with your actual user retrieval logic
def get_current_user(db: Session = Depends(get_db)) -> User:
    # In a real app, you'd get this from a token
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============================================================
# ABAC DEPENDENCY
# ============================================================
def require_abac(
    action: str,
    resource_type: str,
    resource_id_param: Optional[str] = None,
    resource_loader: Optional[Callable] = None
):
    """
    ABAC authorization dependency
    
    Usage:
        @router.get("/invoices/{invoice_id}")
        def get_invoice(
            invoice_id: int,
            authorized: bool = Depends(require_abac("read", "invoice", "invoice_id"))
        ):
            ...
    """
    def dependency(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> bool:
        # Extract resource ID from path parameters
        resource_id = None
        if resource_id_param:
            resource_id = request.path_params.get(resource_id_param)
        
        # Load resource object if loader provided
        resource_obj = None
        if resource_loader and resource_id:
            resource_obj = resource_loader(db, resource_id)
        
        # Build context
        context = {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": request.url.path,
        }
        
        # Check access
        allowed, reason, policy = ABACService.check_access(
            db=db,
            user=current_user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_obj=resource_obj,
            context=context
        )
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {reason}"
            )
        
        return True
    
    return dependency


# ============================================================
# HYBRID RBAC + ABAC
# ============================================================
def require_hybrid_auth(
    roles: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None,
    abac_action: Optional[str] = None,
    abac_resource_type: Optional[str] = None,
    abac_resource_id_param: Optional[str] = None,
    require_all: bool = True  # True = AND, False = OR
):
    """
    Hybrid RBAC + ABAC authorization
    
    Usage:
        @router.post("/invoices/{invoice_id}/approve")
        def approve_invoice(
            invoice_id: int,
            authorized: bool = Depends(require_hybrid_auth(
                roles=["finance_manager"],
                abac_action="approve",
                abac_resource_type="invoice",
                abac_resource_id_param="invoice_id"
            ))
        ):
            ...
    """
    def dependency(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> bool:
        rbac_passed = False
        abac_passed = False
        
        # Check RBAC
        if roles or permissions:
            user_roles = [r.name for r in getattr(current_user, "roles", [])] or [current_user.role]
            
            if roles:
                rbac_passed = any(role in user_roles for role in roles)
            
            if permissions:
                # Implement permission checking logic
                # user_permissions = get_user_permissions(db, current_user)
                # rbac_passed = all(perm in user_permissions for perm in permissions)
                pass
        
        # Check ABAC
        if abac_action and abac_resource_type:
            resource_id = None
            if abac_resource_id_param:
                resource_id = request.path_params.get(abac_resource_id_param)
            
            context = {
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "endpoint": request.url.path,
            }
            
            allowed, reason, policy = ABACService.check_access(
                db=db,
                user=current_user,
                action=abac_action,
                resource_type=abac_resource_type,
                resource_id=resource_id,
                context=context
            )
            
            abac_passed = allowed
        
        # Evaluate based on require_all flag
        if require_all:
            # Both must pass (AND)
            if (roles or permissions) and (abac_action and abac_resource_type):
                authorized = rbac_passed and abac_passed
            elif roles or permissions:
                authorized = rbac_passed
            elif abac_action and abac_resource_type:
                authorized = abac_passed
            else:
                authorized = False
        else:
            # Either can pass (OR)
            authorized = rbac_passed or abac_passed
        
        if not authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Insufficient permissions"
            )
        
        return True
    
    return dependency


# ============================================================
# CONDITIONAL ABAC (for workflow integration)
# ============================================================
class ABACChecker:
    """Reusable ABAC checker for use in service methods"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check(
        self,
        user: User,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        resource_obj: Optional[any] = None
    ) -> Tuple[bool, str]:
        """Check ABAC authorization"""
        allowed, reason, policy = ABACService.check_access(
            db=self.db,
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_obj=resource_obj,
            context=None
        )
        return allowed, reason
    
    def require(
        self,
        user: User,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        resource_obj: Optional[any] = None
    ):
        """Check ABAC and raise exception if denied"""
        allowed, reason = self.check(
            user, action, resource_type, resource_id, resource_obj
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {reason}"
            )


def get_abac_checker(db: Session = Depends(get_db)) -> ABACChecker:
    """Dependency for ABAC checker"""
    return ABACChecker(db)
