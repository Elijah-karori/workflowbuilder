from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, Tuple
from fastapi import HTTPException
import time
import re
from datetime import datetime

from app.models.abac import (
    ABACPolicy, ABACAccessLog, ResourceAttribute, UserAttribute,
    PolicyEffect, ConditionOperator
)
from app.models.user import User


class ABACService:
    """Attribute-Based Access Control evaluation engine"""

    # ============================================================
    # MAIN AUTHORIZATION CHECK
    # ============================================================
    @staticmethod
    def check_access(
        db: Session,
        user: User,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        resource_obj: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Optional[ABACPolicy]]:
        """
        Evaluate ABAC policies and return access decision
        
        Returns:
            Tuple of (allowed: bool, reason: str, applied_policy: ABACPolicy)
        """
        start_time = time.time()
        
        # Gather attributes
        user_attrs = ABACService._get_user_attributes(db, user)
        resource_attrs = ABACService._get_resource_attributes(
            db, resource_type, resource_id, resource_obj
        )
        env_attrs = ABACService._get_environment_attributes(context)
        
        # Get applicable policies
        policies = ABACService._get_applicable_policies(
            db, action, resource_type, user
        )
        
        evaluated_policy_ids = []
        decision = "deny"
        reason = "No matching policy found"
        applied_policy = None
        
        # Evaluate policies (highest priority first)
        for policy in sorted(policies, key=lambda p: p.priority, reverse=True):
            evaluated_policy_ids.append(policy.id)
            
            if ABACService._evaluate_policy(
                policy, user_attrs, resource_attrs, env_attrs
            ):
                decision = policy.effect.value
                reason = f"Policy '{policy.name}' matched"
                applied_policy = policy
                
                # DENY takes precedence - stop immediately
                if policy.effect == PolicyEffect.deny:
                    break
                
                # ALLOW found - continue checking for DENY
                if policy.effect == PolicyEffect.allow:
                    continue
        
        # Log the decision
        evaluation_time = int((time.time() - start_time) * 1000)
        ABACService._log_access(
            db=db,
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            decision=decision,
            policy_id=applied_policy.id if applied_policy else None,
            user_attrs=user_attrs,
            resource_attrs=resource_attrs,
            env_attrs=env_attrs,
            evaluated_policies=evaluated_policy_ids,
            evaluation_time_ms=evaluation_time,
            reason=reason,
            context=context
        )
        
        return decision == "allow", reason, applied_policy

    # ============================================================
    # POLICY EVALUATION
    # ============================================================
    @staticmethod
    def _evaluate_policy(
        policy: ABACPolicy,
        user_attrs: Dict[str, Any],
        resource_attrs: Dict[str, Any],
        env_attrs: Dict[str, Any]
    ) -> bool:
        """Evaluate if policy conditions match"""
        
        if not policy.conditions:
            return True  # No conditions = always match
        
        conditions = policy.conditions
        
        # Handle "all" logic (AND)
        if "all" in conditions:
            return all(
                ABACService._evaluate_condition(
                    cond, user_attrs, resource_attrs, env_attrs
                )
                for cond in conditions["all"]
            )
        
        # Handle "any" logic (OR)
        if "any" in conditions:
            return any(
                ABACService._evaluate_condition(
                    cond, user_attrs, resource_attrs, env_attrs
                )
                for cond in conditions["any"]
            )
        
        # Handle "none" logic (NOT)
        if "none" in conditions:
            return not any(
                ABACService._evaluate_condition(
                    cond, user_attrs, resource_attrs, env_attrs
                )
                for cond in conditions["none"]
            )
        
        return False

    @staticmethod
    def _evaluate_condition(
        condition: Dict[str, Any],
        user_attrs: Dict[str, Any],
        resource_attrs: Dict[str, Any],
        env_attrs: Dict[str, Any]
    ) -> bool:
        """Evaluate a single condition"""
        
        attribute_path = condition.get("attribute")
        operator = condition.get("operator", "eq")
        expected_value = condition.get("value")
        
        # Get actual value from attributes
        actual_value = ABACService._get_attribute_value(
            attribute_path, user_attrs, resource_attrs, env_attrs
        )
        
        # Resolve value if it's a reference (e.g., "{{resource.department_id}}")
        if isinstance(expected_value, str) and expected_value.startswith("{{"):
            expected_value = ABACService._resolve_reference(
                expected_value, user_attrs, resource_attrs, env_attrs
            )
        
        # Evaluate based on operator
        return ABACService._apply_operator(operator, actual_value, expected_value)

    @staticmethod
    def _apply_operator(operator: str, actual: Any, expected: Any) -> bool:
        """Apply comparison operator"""
        
        try:
            if operator == "eq":
                return actual == expected
            
            elif operator == "ne":
                return actual != expected
            
            elif operator == "gt":
                return float(actual) > float(expected)
            
            elif operator == "gte":
                return float(actual) >= float(expected)
            
            elif operator == "lt":
                return float(actual) < float(expected)
            
            elif operator == "lte":
                return float(actual) <= float(expected)
            
            elif operator == "in":
                return actual in expected if isinstance(expected, list) else False
            
            elif operator == "not_in":
                return actual not in expected if isinstance(expected, list) else True
            
            elif operator == "contains":
                return str(expected) in str(actual)
            
            elif operator == "starts_with":
                return str(actual).startswith(str(expected))
            
            elif operator == "ends_with":
                return str(actual).endswith(str(expected))
            
            elif operator == "between":
                if isinstance(expected, list) and len(expected) == 2:
                    return float(expected[0]) <= float(actual) <= float(expected[1])
                return False
            
            elif operator == "is_null":
                return actual is None
            
            elif operator == "is_not_null":
                return actual is not None
            
            else:
                return False
                
        except (ValueError, TypeError, AttributeError):
            return False

    # ============================================================
    # ATTRIBUTE GATHERING
    # ============================================================
    @staticmethod
    def _get_user_attributes(db: Session, user: User) -> Dict[str, Any]:
        """Gather all user attributes"""
        
        user_attr = db.query(UserAttribute).filter_by(user_id=user.id).first()
        
        attrs = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "is_superuser": getattr(user, "is_superuser", False),
        }
        
        # Add ABAC attributes if they exist
        if user_attr:
            attrs.update({
                "department_id": user_attr.department_id,
                "division_id": user_attr.division_id,
                "team_id": user_attr.team_id,
                "job_title": user_attr.job_title,
                "job_level": user_attr.job_level,
                "approval_limit_amount": user_attr.approval_limit_amount,
                "can_approve_own_department": user_attr.can_approve_own_department,
                "can_approve_all_departments": user_attr.can_approve_all_departments,
                "office_location": user_attr.office_location,
                "country_code": user_attr.country_code,
            })
            
            # Merge custom attributes
            if user_attr.custom_attributes:
                attrs.update(user_attr.custom_attributes)
        
        # Add roles if using many-to-many
        if hasattr(user, "roles"):
            attrs["roles"] = [r.name for r in user.roles]
        
        return attrs

    @staticmethod
    def _get_resource_attributes(
        db: Session,
        resource_type: str,
        resource_id: Optional[int],
        resource_obj: Optional[Any]
    ) -> Dict[str, Any]:
        """Gather resource attributes"""
        
        attrs = {
            "type": resource_type,
            "id": resource_id,
        }
        
        # If resource object provided, extract attributes
        if resource_obj:
            # Common attributes
            for attr_name in [
                "status", "amount", "total_amount", "created_by",
                "department_id", "division_id", "created_at",
                "priority", "category", "assigned_to"
            ]:
                if hasattr(resource_obj, attr_name):
                    attrs[attr_name] = getattr(resource_obj, attr_name)
        
        # Get dynamic attributes from database
        if resource_id:
            dynamic_attrs = db.query(ResourceAttribute).filter_by(
                resource_type=resource_type,
                resource_id=resource_id
            ).all()
            
            for attr in dynamic_attrs:
                attrs[attr.attribute_name] = ABACService._parse_attribute_value(
                    attr.attribute_value,
                    attr.attribute_type
                )
        
        return attrs

    @staticmethod
    def _get_environment_attributes(context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Gather environment attributes"""
        
        now = datetime.utcnow()
        
        attrs = {
            "current_time": now.isoformat(),
            "current_date": now.date().isoformat(),
            "current_hour": now.hour,
            "current_day_of_week": now.strftime("%A"),
            "current_month": now.month,
            "current_year": now.year,
        }
        
        # Add context if provided
        if context:
            attrs.update({
                "ip_address": context.get("ip_address"),
                "user_agent": context.get("user_agent"),
                "endpoint": context.get("endpoint"),
            })
        
        return attrs

    # ============================================================
    # HELPER METHODS
    # ============================================================
    @staticmethod
    def _get_applicable_policies(
        db: Session,
        action: str,
        resource_type: str,
        user: User
    ) -> List[ABACPolicy]:
        """Get policies that might apply to this request"""
        
        query = db.query(ABACPolicy).filter(
            ABACPolicy.is_active == True,
            ABACPolicy.action == action,
            ABACPolicy.resource_type == resource_type
        )
        
        # Filter by role requirements if specified
        policies = query.all()
        
        applicable = []
        user_roles = [r.name for r in getattr(user, "roles", [])] or [user.role]
        
        for policy in policies:
            # Check role requirements
            if policy.role_requirements:
                if not any(role in policy.role_requirements for role in user_roles):
                    continue
            
            # Check department/division scope
            user_attr = db.query(UserAttribute).filter_by(user_id=user.id).first()
            
            if policy.department_ids and user_attr:
                if user_attr.department_id not in policy.department_ids:
                    continue
            
            if policy.division_ids and user_attr:
                if user_attr.division_id not in policy.division_ids:
                    continue
            
            applicable.append(policy)
        
        return applicable

    @staticmethod
    def _get_attribute_value(
        path: str,
        user_attrs: Dict,
        resource_attrs: Dict,
        env_attrs: Dict
    ) -> Any:
        """Get attribute value from dot-notation path"""
        
        parts = path.split(".")
        
        if parts[0] == "user":
            obj = user_attrs
        elif parts[0] == "resource":
            obj = resource_attrs
        elif parts[0] == "environment":
            obj = env_attrs
        else:
            return None
        
        # Navigate nested attributes
        for part in parts[1:]:
            if isinstance(obj, dict):
                obj = obj.get(part)
            else:
                obj = getattr(obj, part, None)
            
            if obj is None:
                return None
        
        return obj

    @staticmethod
    def _resolve_reference(
        reference: str,
        user_attrs: Dict,
        resource_attrs: Dict,
        env_attrs: Dict
    ) -> Any:
        """Resolve {{attribute.path}} reference"""
        
        # Extract path from {{...}}
        match = re.match(r"\{\{(.+?)\}\}", reference)
        if not match:
            return reference
        
        path = match.group(1).strip()
        return ABACService._get_attribute_value(
            path, user_attrs, resource_attrs, env_attrs
        )

    @staticmethod
    def _parse_attribute_value(value: str, value_type: str) -> Any:
        """Parse attribute value based on type"""
        
        if value_type == "number":
            try:
                return float(value)
            except ValueError:
                return value
        
        elif value_type == "boolean":
            return value.lower() in ["true", "1", "yes"]
        
        elif value_type == "json":
            import json
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        
        return value  # string

    # ============================================================
    # AUDIT LOGGING
    # ============================================================
    @staticmethod
    def _log_access(
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int],
        decision: str,
        policy_id: Optional[int],
        user_attrs: Dict,
        resource_attrs: Dict,
        env_attrs: Dict,
        evaluated_policies: List[int],
        evaluation_time_ms: int,
        reason: str,
        context: Optional[Dict] = None
    ):
        """Create audit log entry"""
        
        log = ABACAccessLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            decision=decision,
            policy_id=policy_id,
            user_attributes=user_attrs,
            resource_attributes=resource_attrs,
            environment_attributes=env_attrs,
            evaluated_policies=evaluated_policies,
            evaluation_time_ms=evaluation_time_ms,
            reason=reason,
            ip_address=context.get("ip_address") if context else None,
            user_agent=context.get("user_agent") if context else None,
            endpoint=context.get("endpoint") if context else None,
        )
        
        db.add(log)
        db.commit()

    # ============================================================
    # POLICY MANAGEMENT
    # ============================================================
    @staticmethod
    def create_policy(
        db: Session,
        name: str,
        action: str,
        resource_type: str,
        effect: PolicyEffect,
        conditions: Dict[str, Any],
        user: User,
        **kwargs
    ) -> ABACPolicy:
        """Create new ABAC policy"""
        
        policy = ABACPolicy(
            name=name,
            action=action,
            resource_type=resource_type,
            effect=effect,
            conditions=conditions,
            created_by=user.id,
            **kwargs
        )
        
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
        return policy

    @staticmethod
    def update_policy(
        db: Session,
        policy_id: int,
        **updates
    ) -> ABACPolicy:
        """Update existing policy"""
        
        policy = db.query(ABACPolicy).filter_by(id=policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        db.commit()
        db.refresh(policy)
        
        return policy