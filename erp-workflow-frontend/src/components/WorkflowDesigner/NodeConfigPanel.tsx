// =====================================================================
// FILE: src/components/WorkflowDesigner/NodeConfigPanel.tsx
// =====================================================================

import React, { useState, useEffect } from 'react';
import type { Node } from '@xyflow/react';
import { X, Plus, Trash2, Shield, Clock, Info } from 'lucide-react';

interface ABACCondition {
  attribute: string;
  operator: string;
  value: any;
}

interface NodeConfigPanelProps {
  node: Node | null;
  onUpdate: (nodeId: string, data: any) => void;
  onClose: () => void;
}

export default function NodeConfigPanel({ node, onUpdate, onClose }: NodeConfigPanelProps) {
  const [formData, setFormData] = useState<any>({});
  const [abacConditions, setABACConditions] = useState<ABACCondition[]>([]);

  useEffect(() => {
    if (node) {
      setFormData(node.data);
      setABACConditions(node.data.abac_conditions || []);
    }
  }, [node]);

  if (!node) return null;

  const handleChange = (field: string, value: any) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    onUpdate(node.id, newData);
  };

  const addABACCondition = () => {
    const newConditions = [
      ...abacConditions,
      { attribute: '', operator: 'eq', value: '' },
    ];
    setABACConditions(newConditions);
    handleChange('abac_conditions', newConditions);
  };

  const updateABACCondition = (index: number, field: string, value: any) => {
    const newConditions = [...abacConditions];
    newConditions[index] = { ...newConditions[index], [field]: value };
    setABACConditions(newConditions);
    handleChange('abac_conditions', newConditions);
  };

  const removeABACCondition = (index: number) => {
    const newConditions = abacConditions.filter((_, i) => i !== index);
    setABACConditions(newConditions);
    handleChange('abac_conditions', newConditions);
  };

  return (
    <div className="w-[400px] bg-white border-l border-gray-300 flex flex-col h-screen overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-gray-300 flex justify-between items-center bg-gray-100">
        <h3 className="m-0 text-lg font-semibold">Configure Node</h3>
        <button onClick={onClose} className="p-1 rounded hover:bg-gray-200">
          <X size={20} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        {/* Basic Settings */}
        <Section title="Basic Settings">
          <FormField label="Node Label">
            <input
              type="text"
              value={formData.label || ''}
              onChange={(e) => handleChange('label', e.target.value)}
              placeholder="e.g., Manager Approval"
              className="p-2 border border-gray-300 rounded text-sm w-full"
            />
          </FormField>
        </Section>

        {/* RBAC Settings */}
        {node.type === 'approval' && (
          <>
            <Section title="Role-Based Access (RBAC)" icon={<Shield size={16} />}>
              <FormField
                label="Required Role"
                hint="Single role required for this stage"
              >
                <input
                  type="text"
                  value={formData.required_role || ''}
                  onChange={(e) => handleChange('required_role', e.target.value)}
                  placeholder="e.g., finance_manager"
                  className="p-2 border border-gray-300 rounded text-sm w-full"
                />
              </FormField>

              <FormField
                label="Multiple Roles (OR logic)"
                hint="Comma-separated list. Any role can approve."
              >
                <input
                  type="text"
                  value={formData.required_roles?.join(', ') || ''}
                  onChange={(e) =>
                    handleChange('required_roles', e.target.value.split(',').map((s) => s.trim()))
                  }
                  placeholder="e.g., finance_manager, cfo"
                  className="p-2 border border-gray-300 rounded text-sm w-full"
                />
              </FormField>

              <FormField label="Approval Type">
                <select
                  value={formData.approval_type || 'sequential'}
                  onChange={(e) => handleChange('approval_type', e.target.value)}
                  className="p-2 border border-gray-300 rounded text-sm w-full"
                >
                  <option value="sequential">Sequential (One approver)</option>
                  <option value="parallel_all">Parallel - All must approve</option>
                  <option value="parallel_any">Parallel - Any can approve</option>
                  <option value="parallel_majority">Parallel - Majority required</option>
                </select>
              </FormField>

              {formData.approval_type === 'parallel_majority' && (
                <FormField label="Required Approvals Count">
                  <input
                    type="number"
                    value={formData.required_approvals_count || 2}
                    onChange={(e) =>
                      handleChange('required_approvals_count', parseInt(e.target.value))
                    }
                    min="1"
                    className="p-2 border border-gray-300 rounded text-sm w-full"
                  />
                </FormField>
              )}
            </Section>

            {/* ABAC Settings */}
            <Section title="Attribute-Based Access (ABAC)" icon={<Shield size={16} />}>
              <FormField>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.enable_abac || false}
                    onChange={(e) => handleChange('enable_abac', e.target.checked)}
                    className="cursor-pointer"
                  />
                  Enable ABAC Conditions
                </label>
              </FormField>

              {formData.enable_abac && (
                <>
                  <div className="p-3 bg-blue-50 border border-blue-500 rounded text-xs flex items-start gap-2 text-blue-800">
                    <Info size={14} />
                    <span>These conditions will be evaluated in addition to role requirements.</span>
                  </div>

                  {abacConditions.map((condition, index) => (
                    <div key={index} className="p-3 bg-gray-50 border border-gray-300 rounded mb-3">
                      <div className="flex gap-2 mb-2">
                        <select
                          value={condition.attribute}
                          onChange={(e) => updateABACCondition(index, 'attribute', e.target.value)}
                          className="flex-1 p-2 border border-gray-300 rounded text-sm"
                        >
                          <option value="">Select Attribute</option>
                          <optgroup label="User Attributes">
                            <option value="user.department_id">User Department</option>
                            <option value="user.division_id">User Division</option>
                            <option value="user.job_level">User Job Level</option>
                            <option value="user.approval_limit_amount">User Approval Limit</option>
                          </optgroup>
                          <optgroup label="Resource Attributes">
                            <option value="resource.department_id">Resource Department</option>
                            <option value="resource.amount">Resource Amount</option>
                            <option value="resource.status">Resource Status</option>
                            <option value="resource.created_by">Resource Creator</option>
                          </optgroup>
                        </select>

                        <select
                          value={condition.operator}
                          onChange={(e) => updateABACCondition(index, 'operator', e.target.value)}
                          className="w-20 p-2 border border-gray-300 rounded text-sm"
                        >
                          <option value="eq">=</option>
                          <option value="ne">≠</option>
                          <option value="gt">&gt;</option>
                          <option value="gte">≥</option>
                          <option value="lt">&lt;</option>
                          <option value="lte">≤</option>
                          <option value="in">in</option>
                        </select>

                        <input
                          type="text"
                          value={condition.value}
                          onChange={(e) => updateABACCondition(index, 'value', e.target.value)}
                          placeholder="Value or {{reference}}"
                          className="flex-1 p-2 border border-gray-300 rounded text-sm"
                        />

                        <button
                          onClick={() => removeABACCondition(index)}
                          className="p-2 border border-red-500 text-red-500 rounded hover:bg-red-50"
                          title="Remove condition"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                      <div className="text-xs text-gray-500 italic">
                        Example: user.department_id = {`{{resource.department_id}}`}
                      </div>
                    </div>
                  ))}

                  <button onClick={addABACCondition} className="bg-gray-500 text-white px-4 py-2 rounded-md flex items-center gap-2 w-full justify-center hover:bg-gray-600">
                    <Plus size={16} />
                    Add ABAC Condition
                  </button>
                </>
              )}
            </Section>

            {/* SLA & Escalation */}
            <Section title="SLA & Escalation" icon={<Clock size={16} />}>
              <FormField label="SLA (hours)" hint="Time limit before escalation">
                <input
                  type="number"
                  value={formData.sla_hours || ''}
                  onChange={(e) =>
                    handleChange('sla_hours', e.target.value ? parseInt(e.target.value) : null)
                  }
                  placeholder="e.g., 24"
                  className="p-2 border border-gray-300 rounded text-sm w-full"
                />
              </FormField>

              <FormField>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.auto_escalate || false}
                    onChange={(e) => handleChange('auto_escalate', e.target.checked)}
                    className="cursor-pointer"
                  />
                  Auto-escalate on SLA breach
                </label>
              </FormField>

              {formData.auto_escalate && (
                <FormField label="Escalation Role">
                  <input
                    type="text"
                    value={formData.escalation_role || ''}
                    onChange={(e) => handleChange('escalation_role', e.target.value)}
                    placeholder="e.g., senior_manager"
                    className="p-2 border border-gray-300 rounded text-sm w-full"
                  />
                </FormField>
              )}
            </Section>

            {/* Notifications */}
            <Section title="Notifications">
              <FormField label="Email Template">
                <textarea
                  value={formData.notification_template || ''}
                  onChange={(e) => handleChange('notification_template', e.target.value)}
                  rows={4}
                  placeholder="Subject: Approval Required&#10;&#10;Hi {{approver_name}},&#10;&#10;Please review {{resource_type}} #{{resource_id}}..."
                  className="p-2 border border-gray-300 rounded text-xs font-mono w-full resize-y"
                />
              </FormField>
            </Section>
          </>
        )}

        {/* Condition Node Settings */}
        {node.type === 'condition' && (
          <Section title="Condition Settings">
            <FormField label="Field to Check">
              <input
                type="text"
                value={formData.condition_field || ''}
                onChange={(e) => handleChange('condition_field', e.target.value)}
                placeholder="e.g., amount, department"
                className="p-2 border border-gray-300 rounded text-sm w-full"
              />
            </FormField>

            <FormField label="Operator">
              <select
                value={formData.condition_operator || '>'}
                onChange={(e) => handleChange('condition_operator', e.target.value)}
                className="p-2 border border-gray-300 rounded text-sm w-full"
              >
                <option value=">">Greater than (&gt;)</option>
                <option value="<">Less than (&lt;)</option>
                <option value="==">Equal to (==)</option>
                <option value="!=">Not equal to (!=)</option>
                <option value="in">In list (in)</option>
              </select>
            </FormField>

            <FormField label="Value">
              <input
                type="text"
                value={formData.condition_value || ''}
                onChange={(e) => handleChange('condition_value', e.target.value)}
                placeholder="e.g., 10000 or IT,Finance"
                className="p-2 border border-gray-300 rounded text-sm w-full"
              />
            </FormField>
          </Section>
        )}

        {/* Preview */}
        {node.type === 'approval' && (
          <Section title="Authorization Preview">
            <div className="p-4 bg-green-50 border border-green-500 rounded text-sm">
              <strong>Access Requirements:</strong>
              <ul className="my-2 ml-5 list-disc">
                {formData.required_role && <li>✓ Role: {formData.required_role}</li>}
                {formData.required_roles && formData.required_roles.length > 0 && (
                  <li>✓ Any of roles: {formData.required_roles.join(', ')}</li>
                )}
                {formData.enable_abac && abacConditions.length > 0 && (
                  <li>
                    ✓ ABAC Conditions ({abacConditions.length}):
                    <ul className="my-1 ml-5 list-disc">
                      {abacConditions.map((cond, i) => (
                        <li key={i} className="text-xs text-gray-600">
                          {cond.attribute} {cond.operator} {cond.value}
                        </li>
                      ))}
                    </ul>
                  </li>
                )}
                {formData.approval_type !== 'sequential' && (
                  <li>✓ Approval Type: {formData.approval_type}</li>
                )}
                {formData.sla_hours && <li>⏱ SLA: {formData.sla_hours} hours</li>}
              </ul>
            </div>
          </Section>
        )}
      </div>
    </div>
  );
}

// Helper Components
function Section({ title, icon, children }: { title: string; icon?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="mb-6 pb-5 border-b border-gray-200 last:border-b-0">
      <h4 className="text-base font-semibold mb-4 flex items-center gap-2 text-gray-800">
        {icon && <span className="text-blue-500">{icon}</span>}
        {title}
      </h4>
      <div className="flex flex-col gap-4">{children}</div>
    </div>
  );
}

function FormField({
  label,
  hint,
  children,
}: {
  label?: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-2">
      {label && <label className="text-sm font-medium text-gray-800">{label}</label>}
      {children}
      {hint && <div className="text-xs text-gray-500 italic">{hint}</div>}
    </div>
  );
}