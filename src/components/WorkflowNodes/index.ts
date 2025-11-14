import { NodeTypes } from ' @xyflow/react';
import StartNode from './StartNode';
import ApprovalNode from './ApprovalNode';
import ConditionNode from './ConditionNode';
import EndNode from './EndNode';

export const nodeTypes: NodeTypes = {
  start: StartNode,
  approval: ApprovalNode,
  condition: ConditionNode,
  end: EndNode,
};
