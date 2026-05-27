# engine/nodes/common.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(
    code='evaluate_policies',
    sectors=[],             # available to all sectors
    retry_policy='none'     # deterministic — never retry
)
class EvaluatePoliciesNode(BaseNode):
    """
    Runs all active policy rules for the current sector.
    Returns PASS / WARN / FAIL / REQUIRES_APPROVAL per rule.
    Plugs into engine/policies/ — sector-specific rules loaded dynamically.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        sector   = context.get('sector', 'unknown')
        run_id   = context.get('run_id', '')

        logger.info(f'Evaluating policies for sector={sector} run={run_id}')

        # Policy engine will be wired in engine/policies/ in a later step.
        # For now returns a stub so the node registry works end-to-end.
        return {
            'sector':  sector,
            'results': [],          # will be populated by policy engine
            'status':  'PASS',
        }


@register_node(
    code='human_decision',
    sectors=[],
    retry_policy='timeout'  # HITL — escalation on timeout, not error retry
)
class HumanDecisionNode(BaseNode):
    """
    Pauses the graph and waits for a human reviewer to approve/reject/escalate.
    The actual pause is handled by LangGraph interrupt_before.
    This node records the decision once the graph resumes.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        action = input_data.get('action')
        if not action:
            # Graph was interrupted here — LangGraph will pause before this executes
            return {'status': 'awaiting_human_input'}

        return {
            'action':       action,
            'actor':        input_data.get('actor', ''),
            'reason_code':  input_data.get('reason_code', ''),
            'justification': input_data.get('justification', ''),
        }


@register_node(
    code='approval_gate',
    sectors=[],
    retry_policy='none'
)
class ApprovalGateNode(BaseNode):
    """
    Routes workflow based on a human decision outcome.
    APPROVED → next node, REJECTED → compensation, ESCALATED → senior reviewer.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        action = input_data.get('action', 'APPROVED')
        return {
            'route':  action,
            'reason': input_data.get('reason_code', ''),
        }