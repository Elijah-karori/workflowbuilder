from sqlalchemy.orm import Session
from app.models import ABACPolicy, User
from app.models.abac import PolicyEffect


def seed_abac_policies(db: Session, admin_user: User):
    """Seed common ABAC policies for ERP"""
    
    policies = [
        # ============================================================
        # INVOICE POLICIES
        # ============================================================
        {
            "name": "Finance Manager - Approve Own Department Invoices",
            "description": "Finance managers can approve invoices from their department under $10,000",
            "effect": PolicyEffect.allow,
            "priority": 100,
            "action": "approve",
            "resource_type": "Invoice",
            "role_requirements": ["finance_manager"],
            "conditions": {
                "all": [
                    {
                        "attribute": "user.department_id",
                        "operator": "eq",
                        "value": "{{resource.department_id}}"
                    },
                    {
                        "attribute": "resource.amount",
                        "operator": "lte",
                        "value": 10000
                    },
                    {
                        "attribute": "resource.status",
                        "operator": "eq",
                        "value": "pending"
                    }
                ]
            }
        },
        
        {
            "name": "CFO - Approve High Value Invoices",
            "description": "CFO can approve any invoice over $10,000",
            "effect": PolicyEffect.allow,
            "priority": 150,
            "action": "approve",
            "resource_type": "Invoice",
            "role_requirements": ["cfo"],
            "conditions": {
                "all": [
                    {
                        "attribute": "resource.amount",
                        "operator": "gt",
                        "value": 10000
                    },
                    {
                        "attribute": "resource.status",
                        "operator": "in",
                        "value": ["pending", "manager_approved"]
                    }
                ]
            }
        },
        
        {
            "name": "Prevent Self-Approval of Invoices",
            "description": "Users cannot approve their own invoices",
            "effect": PolicyEffect.deny,
            "priority": 200,
            "action": "approve",
            "resource_type": "Invoice",
            "conditions": {
                "all": [
                    {
                        "attribute": "user.id",
                        "operator": "eq",
                        "value": "{{resource.created_by}}"
                    }
                ]
            }
        },
        
        # ============================================================
        # EMPLOYEE ONBOARDING POLICIES
        # ============================================================
        {
            "name": "HR Manager - Approve Department Employees",
            "description": "HR managers can approve employees for their department",
            "effect": PolicyEffect.allow,
            "priority": 100,
            "action": "approve",
            "resource_type": "EmployeeProfile",
            "role_requirements": ["hr_manager"],
            "conditions": {
                "all": [
                    {
                        "attribute": "user.department_id",
                        "operator": "eq",
                        "value": "{{resource.department_id}}"
                    }
                ]
            }
        },
        
        {
            "name": "Department Head - Approve Own Team",
            "description": "Department heads approve employees joining their team",
            "effect": PolicyEffect.allow,
            "priority": 100,
            "action": "approve",
            "resource_type": "EmployeeProfile",
            "role_requirements": ["department_head"],
            "conditions": {
                "all": [
                    {
                        "attribute": "user.department_id",
                        "operator": "eq",
                        "value": "{{resource.department_id}}"
                    }
                ]
            }
        },
        
        # ============================================================
        # PURCHASE ORDER POLICIES
        # ============================================================
        {
            "name": "Manager - Approve Small Purchase Orders",
            "description": "Managers can approve POs under $5,000 for their department",
            "effect": PolicyEffect.allow,
            "priority": 100,
            "action": "approve",
            "resource_type": "PurchaseOrder",
            "role_requirements": ["manager", "department_manager"],
            "conditions": {
                "all": [
                    {
                        "attribute": "user.department_id",
                        "operator": "eq",
                        "value": "{{resource.department_id}}"
                    },
                    {
                        "attribute": "resource.total_amount",
                        "operator": "lte",
                        "value": 5000
                    }
                ]
            }
        },
        
        {
            "name": "Finance - Approve Medium Purchase Orders",
            "description": "Finance can approve POs between $5,000 and $50,000",
            "effect": PolicyEffect.allow,
            "priority": 110,
            "action": "approve",
            "resource_type": "PurchaseOrder",
            "role_requirements": ["finance_manager"],
            "conditions": {
                "all": [
                    {
                        "attribute": "resource.total_amount",
                        "operator": "between",
                        "value": [5000, 50000]
                    }
                ]
            }
        },
        
        {
            "name": "Executive - Approve Large Purchase Orders",
            "description": "Executives approve POs over $50,000",
            "effect": PolicyEffect.allow,
            "priority": 120,
            "action": "approve",
            "resource_type": "PurchaseOrder",
            "role_requirements": ["cfo", "ceo"],
            "conditions": {
                "all": [
                    {
                        "attribute": "resource.total_amount",
                        "operator": "gt",
                        "value": 50000
                    }
                ]
            }
        },
        
        # ============================================================
        # LEAVE REQUEST POLICIES
        # ============================================================
        {
            "name": "Manager - Approve Short Leave",
            "description": "Managers can approve leave requests up to 5 days for their team",
            "effect": PolicyEffect.allow,
            "priority": 100,
            "action": "approve",
            "resource_type": "LeaveRequest",
            "role_requirements": ["manager", "supervisor"],
            "conditions": {
                "all": [
                    {
                        "attribute": "user.department_id",
                        "operator": "eq",
                        "value": "{{resource.department_id}}"
                    },
                    {
                        "attribute": "resource.days",
                        "operator": "lte",
                        "value": 5
                    }
                ]
            }
        },
        
        {
            "name": "HR - Approve Extended Leave",
            "description": "HR must approve leave requests over 5 days",
            "effect": PolicyEffect.allow,
            "priority": 110,
            "action": "approve",
            "resource_type": "LeaveRequest",
            "role_requirements": ["hr_manager"],
            "conditions": {
                "all": [
                    {
                        "attribute": "resource.days",
                        "operator": "gt",
                        "value": 5
                    }
                ]
            }
        },
        
        # ============================================================
        # BUDGET REVISION POLICIES
        # ============================================================
        {
            "name": "Department Head - Minor Budget Revisions",
            "description": "Department heads can approve budget revisions under 10%",
            "effect": PolicyEffect.allow,
            "priority": 100,
            "action": "approve",
            "resource_type": "BudgetRevision",
            "role_requirements": ["department_head"],
            "conditions": {
                "all": [
                    {
                        "attribute": "user.department_id",
                        "operator": "eq",
                        "value": "{{resource.department_id}}"
                    },
                    {
                        "attribute": "resource.variance_percentage",
                        "operator": "lte",
                        "value": 10
                    }
                ]
            }
        },
        
        {
            "name": "CFO - Major Budget Revisions",
            "description": "CFO must approve budget revisions over 10%",
            "effect": PolicyEffect.allow,
            "priority": 120,
            "action": "approve",
            "resource_type": "BudgetRevision",
            "role_requirements": ["cfo"],
            "conditions": {
                "all": [
                    {
                        "attribute": "resource.variance_percentage",
                        "operator": "gt",
                        "value": 10
                    }
                ]
            }
        },
        
        # ============================================================
        # TIME-BASED POLICIES
        # ============================================================
        {
            "name": "Business Hours Only - Approvals",
            "description": "Approvals can only be made during business hours",
            "effect": PolicyEffect.deny,
            "priority": 90,
            "action": "approve",
            "resource_type": "*",  # Applies to all resources
            "conditions": {
                "any": [
                    {
                        "attribute": "environment.current_hour",
                        "operator": "lt",
                        "value": 8
                    },
                    {
                        "attribute": "environment.current_hour",
                        "operator": "gt",
                        "value": 18
                    },
                    {
                        "attribute": "environment.current_day_of_week",
                        "operator": "in",
                        "value": ["Saturday", "Sunday"]
                    }
                ]
            }
        },
        
        # ============================================================
        # ADMIN OVERRIDE
        # ============================================================
        {
            "name": "Admin - Full Access",
            "description": "Admins have full access to all resources",
            "effect": PolicyEffect.allow,
            "priority": 999,
            "action": "*",
            "resource_type": "*",
            "role_requirements": ["admin"],
            "conditions": None
        }
    ]
    
    for policy_data in policies:
        # Check if policy already exists
        existing = db.query(ABACPolicy).filter_by(name=policy_data["name"]).first()
        if not existing:
            policy = ABACPolicy(
                **policy_data,
                created_by=admin_user.id
            )
            db.add(policy)
            print(f"✓ Created policy: {policy_data['name']}")
    
    db.commit()
    print(f"\n✓ Seeded {len(policies)} ABAC policies")