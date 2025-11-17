import StartNode from './StartNode';
import EndNode from './EndNode';
import ApprovalNode from './ApprovalNode';
import ConditionNode from './ConditionNode';

export const nodeTypes = {
  start: StartNode,
  end: EndNode,
  approval: ApprovalNode,
  condition: ConditionNode,
};
