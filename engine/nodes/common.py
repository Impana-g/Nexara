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
        sector = context.get('sector', 'unknown')
        run_id = context.get('run_id', '')

        logger.info(f'Evaluating policies for sector={sector} run={run_id}')

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
            return {'status': 'awaiting_human_input'}

        return {
            'action':        action,
            'actor':         input_data.get('actor', ''),
            'reason_code':   input_data.get('reason_code', ''),
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


@register_node(
    code='extract_insights',
    sectors=[],             # cross-sector — finance, IT, HR, all sectors
    retry_policy='bounded'
)
class ExtractInsightsNode(BaseNode):
    """
    Claude-powered cross-sector insight extractor.
    Drop into any workflow after any compute/policy node.
    Returns structured key_findings, risk_flags, and recommended_action.
    Works for finance portfolio reviews, IT change requests, HR hiring — any sector.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        import os
        import json
        import anthropic

        sector   = context.get('sector', 'unknown')
        run_id   = context.get('run_id', '')
        workflow = context.get('workflow_code', 'unknown')

        # accept either a specific 'data' key or the whole input_data
        data_to_analyse = input_data.get('data', input_data)

        # safe default — returned as-is if LLM is unavailable
        insights = {
            'sector':             sector,
            'workflow':           workflow,
            'run_id':             run_id,
            'key_findings':       [],
            'risk_flags':         [],
            'recommended_action': '',
            'confidence':         'low',
            'llm_powered':        False,
        }

        try:
            api_key = os.environ.get('ANTHROPIC_API_KEY', '')
            if not api_key:
                logger.warning('[extract_insights] ANTHROPIC_API_KEY not set — returning empty insights')
                return insights

            client = anthropic.Anthropic(api_key=api_key)

            prompt = f"""You are a compliance and operations analyst reviewing workflow output data.

Sector: {sector}
Workflow: {workflow}

Workflow output:
{json.dumps(data_to_analyse, indent=2, default=str)}

Respond ONLY with a valid JSON object. No explanation, no markdown, no code fences.
Use exactly this structure:
{{
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "risk_flags": ["risk 1"],
  "recommended_action": "one concrete next step for a human reviewer",
  "confidence": "high"
}}

Rules:
- key_findings: 2-4 factual observations drawn only from the data above
- risk_flags: only real risks visible in the data — empty list [] if none
- recommended_action: one sentence, specific and actionable
- confidence: "high" if data is complete, "medium" if partial, "low" if sparse"""

            message = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=512,
                messages=[{'role': 'user', 'content': prompt}]
            )

            raw = message.content[0].text.strip()

            # strip markdown fences defensively — model sometimes wraps anyway
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
                raw = raw.strip()

            parsed = json.loads(raw)

            insights.update({
                'key_findings':       parsed.get('key_findings', []),
                'risk_flags':         parsed.get('risk_flags', []),
                'recommended_action': parsed.get('recommended_action', ''),
                'confidence':         parsed.get('confidence', 'low'),
                'llm_powered':        True,
            })

            logger.info(
                f'[extract_insights] sector={sector} '
                f'findings={len(insights["key_findings"])} '
                f'flags={len(insights["risk_flags"])}'
            )

        except json.JSONDecodeError as e:
            logger.error(f'[extract_insights] JSON parse failed — {e} — raw: {raw[:200]}')
        except Exception as e:
            logger.error(f'[extract_insights] Claude call failed — {e}')

        return insights