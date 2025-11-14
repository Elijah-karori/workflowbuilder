# =====================================================================
# FILE: app/services/workflow_templates.py
# =====================================================================

from typing import Dict, Any, List


class WorkflowTemplates:
    """Pre-built workflow templates for common scenarios"""

    @staticmethod
    def get_template(template_name: str) -> Dict[str, Any]:
        """Get workflow template by name"""
        templates = {
            "employee_onboarding": WorkflowTemplates.employee_onboarding(),
            "leave_request": WorkflowTemplates.leave_request(),
            "purchase_order": WorkflowTemplates.purchase_order(),
            "expense_approval": WorkflowTemplates.expense_approval(),
            "budget_revision": WorkflowTemplates.budget_revision(),
        }
        return templates.get(template_name, {})

    @staticmethod
    def get_all_templates() -> List[Dict[str, Any]]:
        """Get all available templates"""
        return [
            {
                "id": "employee_onboarding",
                "name": "Employee Onboarding",
                "description": "Multi-stage approval for new employee profiles",
                "category": "HR",
            },
            {
                "id": "leave_request",
                "name": "Leave Request",
                "description": "Manager and HR approval for leave applications",
                "category": "HR",
            },
            {
                "id": "purchase_order",
                "name": "Purchase Order",
                "description": "Department, finance, and executive approval based on amount",
                "category": "Finance",
            },
            {
                "id": "expense_approval",
                "name": "Expense Approval",
                "description": "Manager approval for employee expenses",
                "category": "Finance",
            },
            {
                "id": "budget_revision",
                "name": "Budget Revision",
                "description": "Multi-level approval for budget changes",
                "category": "Finance",
            },
        ]

    @staticmethod
    def employee_onboarding() -> Dict[str, Any]:
        """Employee onboarding workflow template"""
        return {
            "name": "Employee Onboarding",
            "description": "New employee approval workflow",
            "model_name": "EmployeeProfile",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start",
                    "position": {"x": 250, "y": 50},
                    "data": {"label": "Start"},
                },
                {
                    "id": "approval-1",
                    "type": "approval",
                    "position": {"x": 250, "y": 150},
                    "data": {
                        "label": "HR Manager Review",
                        "required_role": "hr_manager",
                        "approval_type": "sequential",
                        "sla_hours": 24,
                        "notification_template": "New employee profile requires your review",
                    },
                },
                {
                    "id": "approval-2",
                    "type": "approval",
                    "position": {"x": 250, "y": 300},
                    "data": {
                        "label": "Department Head Approval",
                        "required_role": "department_head",
                        "approval_type": "sequential",
                        "sla_hours": 48,
                    },
                },
                {
                    "id": "end-1",
                    "type": "end",
                    "position": {"x": 250, "y": 450},
                    "data": {"label": "Complete"},
                },
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "approval-1"},
                {"id": "e2", "source": "approval-1", "target": "approval-2"},
                {"id": "e3", "source": "approval-2", "target": "end-1"},
            ],
        }

    @staticmethod
    def purchase_order() -> Dict[str, Any]:
        """Purchase order approval workflow template"""
        return {
            "name": "Purchase Order Approval",
            "description": "Amount-based approval routing",
            "model_name": "PurchaseOrder",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start",
                    "position": {"x": 300, "y": 50},
                    "data": {"label": "Start"},
                },
                {
                    "id": "approval-1",
                    "type": "approval",
                    "position": {"x": 300, "y": 150},
                    "data": {
                        "label": "Department Manager",
                        "required_role": "department_manager",
                        "approval_type": "sequential",
                        "sla_hours": 24,
                    },
                },
                {
                    "id": "condition-1",
                    "type": "condition",
                    "position": {"x": 300, "y": 300},
                    "data": {
                        "label": "Check Amount",
                        "condition_field": "total_amount",
                        "condition_operator": ">",
                        "condition_value": "10000",
                    },
                },
                {
                    "id": "approval-2",
                    "type": "approval",
                    "position": {"x": 150, "y": 450},
                    "data": {
                        "label": "CFO Approval",
                        "required_role": "cfo",
                        "approval_type": "sequential",
                        "sla_hours": 72,
                    },
                },
                {
                    "id": "approval-3",
                    "type": "approval",
                    "position": {"x": 450, "y": 450},
                    "data": {
                        "label": "Finance Manager",
                        "required_role": "finance_manager",
                        "approval_type": "sequential",
                        "sla_hours": 48,
                    },
                },
                {
                    "id": "end-1",
                    "type": "end",
                    "position": {"x": 300, "y": 600},
                    "data": {"label": "Approved"},
                },
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "approval-1"},
                {"id": "e2", "source": "approval-1", "target": "condition-1"},
                {
                    "id": "e3",
                    "source": "condition-1",
                    "target": "approval-2",
                    "data": {"label": "> $10,000", "condition": True},
                },
                {
                    "id": "e4",
                    "source": "condition-1",
                    "target": "approval-3",
                    "data": {"label": "≤ $10,000", "condition": True},
                },
                {"id": "e5", "source": "approval-2", "target": "end-1"},
                {"id": "e6", "source": "approval-3", "target": "end-1"},
            ],
        }

    @staticmethod
    def expense_approval() -> Dict[str, Any]:
        """Expense approval workflow template"""
        return {
            "name": "Expense Approval",
            "description": "Manager approval for employee expenses",
            "model_name": "ExpenseReport",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start",
                    "position": {"x": 250, "y": 50},
                    "data": {"label": "Submit Expense"},
                },
                {
                    "id": "approval-1",
                    "type": "approval",
                    "position": {"x": 250, "y": 200},
                    "data": {
                        "label": "Manager Approval",
                        "required_role": "manager",
                        "approval_type": "sequential",
                        "sla_hours": 48,
                    },
                },
                {
                    "id": "end-1",
                    "type": "end",
                    "position": {"x": 250, "y": 350},
                    "data": {"label": "Approved"},
                },
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "approval-1"},
                {"id": "e2", "source": "approval-1", "target": "end-1"},
            ],
        }


    @staticmethod
    def budget_revision() -> Dict[str, Any]:
        """Budget revision workflow template"""
        return {
            "name": "Budget Revision",
            "description": "Multi-level approval for budget changes",
            "model_name": "BudgetRevision",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start",
                    "position": {"x": 300, "y": 50},
                    "data": {"label": "Start"},
                },
                {
                    "id": "approval-1",
                    "type": "approval",
                    "position": {"x": 300, "y": 150},
                    "data": {
                        "label": "Department Manager",
                        "required_role": "department_manager",
                        "approval_type": "sequential",
                        "sla_hours": 24,
                    },
                },
                {
                    "id": "condition-1",
                    "type": "condition",
                    "position": {"x": 300, "y": 300},
                    "data": {
                        "label": "Check Amount",
                        "condition_field": "revision_amount",
                        "condition_operator": ">",
                        "condition_value": "5000",
                    },
                },
                {
                    "id": "approval-2",
                    "type": "approval",
                    "position": {"x": 150, "y": 450},
                    "data": {
                        "label": "CFO Approval",
                        "required_role": "cfo",
                        "approval_type": "sequential",
                        "sla_hours": 72,
                    },
                },
                {
                    "id": "approval-3",
                    "type": "approval",
                    "position": {"x": 450, "y": 450},
                    "data": {
                        "label": "Finance Manager",
                        "required_role": "finance_manager",
                        "approval_type": "sequential",
                        "sla_hours": 48,
                    },
                },
                {
                    "id": "end-1",
                    "type": "end",
                    "position": {"x": 300, "y": 600},
                    "data": {"label": "Approved"},
                },
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "approval-1"},
                {"id": "e2", "source": "approval-1", "target": "condition-1"},
                {
                    "id": "e3",
                    "source": "condition-1",
                    "target": "approval-2",
                    "data": {"label": "> $5,000", "condition": True},
                },
                {
                    "id": "e4",
                    "source": "condition-1",
                    "target": "approval-3",
                    "data": {"label": "≤ $5,000", "condition": True},
                },
                {"id": "e5", "source": "approval-2", "target": "end-1"},
                {"id": "e6", "source": "approval-3", "target": "end-1"},
            ],
        }

    @staticmethod
    def leave_request() -> Dict[str, Any]:
        """Leave request workflow template"""
        return {
            "name": "Leave Request",
            "description": "Employee leave approval",
            "model_name": "LeaveRequest",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start",
                    "position": {"x": 250, "y": 50},
                    "data": {"label": "Submit Leave"},
                },
                {
                    "id": "approval-1",
                    "type": "approval",
                    "position": {"x": 250, "y": 200},
                    "data": {
                        "label": "Manager Approval",
                        "required_role": "manager",
                        "approval_type": "sequential",
                        "sla_hours": 24,
                    },
                },
                {
                    "id": "condition-1",
                    "type": "condition",
                    "position": {"x": 250, "y": 350},
                    "data": {
                        "label": "Check Duration",
                        "condition_field": "days",
                        "condition_operator": ">",
                        "condition_value": "5",
                    },
                },
                {
                    "id": "approval-2",
                    "type": "approval",
                    "position": {"x": 100, "y": 500},
                    "data": {
                        "label": "HR Approval",
                        "required_role": "hr_manager",
                        "approval_type": "sequential",
                        "sla_hours": 48,
                    },
                },
                {
                    "id": "end-1",
                    "type": "end",
                    "position": {"x": 250, "y": 650},
                    "data": {"label": "Approved"},
                },
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "approval-1"},
                {"id": "e2", "source": "approval-1", "target": "condition-1"},
                {
                    "id": "e3",
                    "source": "condition-1",
                    "target": "approval-2",
                    "data": {"label": "> 5 days", "condition": True},
                },
                {
                    "id": "e4",
                    "source": "condition-1",
                    "target": "end-1",
                    "data": {"label": "≤ 5 days", "condition": True},
                },
                {"id": "e5", "source": "approval-2", "target": "end-1"},
            ],
        }