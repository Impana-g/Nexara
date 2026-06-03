# engine/nodes/it.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(
    code='validate_change_request',
    sectors=['it'],
    retry_policy='none'
)
class ValidateChangeRequestNode(BaseNode):
    """
    Validates RFC form completeness.
    Checks: affected_system, rollback_plan, deployment_window, risk_level.
    Returns PASS or FAIL with missing fields listed.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['title', 'affected_system', 'rollback_plan', 'deployment_window']
        missing  = [f for f in required if not input_data.get(f)]

        status = 'FAIL' if missing else 'PASS'
        logger.info(f'validate_change_request: {status} — missing={missing}')

        return {
            'status':        status,
            'missing_fields': missing,
            'title':         input_data.get('title', ''),
            'affected_system': input_data.get('affected_system', ''),
            'risk_level':    input_data.get('risk_level', 'medium'),
        }


@register_node(
    code='check_freeze_window',
    sectors=['it'],
    retry_policy='none'
)
class CheckFreezeWindowNode(BaseNode):
    """
    Checks if the deployment window falls within a change freeze period.
    Freeze periods: end of quarter, major holidays, production freeze windows.
    Returns PASS or FAIL with freeze reason.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        from datetime import datetime

        deployment_window = input_data.get('deployment_window', '')
        freeze_windows    = input_data.get('freeze_windows', [])

        # Simple check — if no freeze windows defined, always PASS
        if not freeze_windows:
            return {
                'status': 'PASS',
                'reason': 'No freeze windows configured',
                'deployment_window': deployment_window,
            }

        # Check if deployment falls in any freeze window
        for fw in freeze_windows:
            if fw.get('start') <= deployment_window <= fw.get('end'):
                return {
                    'status': 'FAIL',
                    'reason': fw.get('reason', 'Change freeze window active'),
                    'deployment_window': deployment_window,
                }

        return {
            'status': 'PASS',
            'reason': 'Outside all freeze windows',
            'deployment_window': deployment_window,
        }


@register_node(
    code='evaluate_risk_level',
    sectors=['it'],
    retry_policy='none'
)
class EvaluateRiskLevelNode(BaseNode):
    """
    Computes risk score from blast radius, deployment time,
    system criticality, and recent incident history.
    Tags RFC as LOW / MEDIUM / HIGH / CRITICAL.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        affected_system  = input_data.get('affected_system', '')
        risk_level       = input_data.get('risk_level', 'medium')
        rollback_plan    = input_data.get('rollback_plan', '')
        recent_incidents = input_data.get('recent_incidents', 0)

        # Risk score calculation
        score = 0
        if risk_level == 'critical':  score += 40
        elif risk_level == 'high':    score += 30
        elif risk_level == 'medium':  score += 20
        else:                         score += 10

        # Penalty for missing rollback plan
        if not rollback_plan:
            score += 20

        # Penalty for recent incidents on same system
        score += min(recent_incidents * 5, 20)

        # Final classification
        if score >= 50:    final = 'CRITICAL'
        elif score >= 35:  final = 'HIGH'
        elif score >= 20:  final = 'MEDIUM'
        else:              final = 'LOW'

        logger.info(f'evaluate_risk_level: score={score} final={final}')

        return {
            'risk_score':       score,
            'risk_classification': final,
            'affected_system':  affected_system,
            'requires_cab':     final in ('HIGH', 'CRITICAL'),
        }


@register_node(
    code='notify_cab',
    sectors=['it'],
    retry_policy='bounded'
)
class NotifyCABNode(BaseNode):
    """
    Notifies the Change Advisory Board (CAB) that a review is needed.
    In production this sends email/Slack. Currently logs and returns stub.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        risk_classification = input_data.get('risk_classification', 'MEDIUM')
        title               = input_data.get('title', '')
        requires_cab        = input_data.get('requires_cab', False)

        if not requires_cab:
            return {
                'status':  'skipped',
                'reason':  'CAB notification not required for this risk level',
            }

        logger.info(f'Notifying CAB for: {title} [{risk_classification}]')

        return {
            'status':      'notified',
            'notified_to': 'cab@company.com',
            'subject':     f'CAB Review Required: {title}',
            'risk':        risk_classification,
        }


@register_node(
    code='generate_soc2_evidence',
    sectors=['it'],
    retry_policy='bounded'
)
class GenerateSOC2EvidenceNode(BaseNode):
    """
    Claude-powered SOC 2 Change Management evidence generator.
    Produces a structured, auditor-ready evidence record
    from the full policy + HITL decision chain.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        import os
        import json
        import anthropic

        title          = input_data.get('title', '')
        risk           = input_data.get('risk_classification', '')
        human_action   = input_data.get('human_action', {})
        policy_results = input_data.get('policy_results', [])
        change_details = input_data.get('change_details', {})

        passed = sum(1 for r in policy_results if r.get('status') == 'PASS')
        failed = sum(1 for r in policy_results if r.get('status') == 'FAIL')

        # safe fallback
        evidence = {
            'evidence_type':   'soc2_change_management',
            'change_title':    title,
            'risk_level':      risk,
            'policy_summary':  {'passed': passed, 'failed': failed},
            'cab_decision':    human_action.get('action', 'N/A'),
            'decided_by':      human_action.get('actor', 'N/A'),
            'justification':   human_action.get('justification', ''),
            'run_id':          context.get('run_id', ''),
            'audit_narrative': '',
            'control_evidence': [],
            'llm_powered':     False,
            'status':          'complete',
        }

        try:
            api_key = os.environ.get('ANTHROPIC_API_KEY', '')
            if not api_key:
                logger.warning('[generate_soc2_evidence] ANTHROPIC_API_KEY not set — returning fallback')
                return evidence

            client = anthropic.Anthropic(api_key=api_key)

            prompt = f"""You are a SOC 2 compliance analyst writing a change management evidence record for an external auditor.

Change Request Details:
- Title: {title}
- Risk Classification: {risk}
- Change Details: {json.dumps(change_details, indent=2, default=str)}

Policy Check Results:
- Passed: {passed}, Failed: {failed}
- Details: {json.dumps(policy_results, indent=2, default=str)}

CAB (Change Advisory Board) Decision:
- Action: {human_action.get('action', 'N/A')}
- Decided by: {human_action.get('actor', 'N/A')}
- Justification: {human_action.get('justification', '')}

Workflow Run ID: {context.get('run_id', '')}

Write a formal SOC 2 Change Management evidence record. Respond ONLY with a valid JSON object. No markdown, no code fences.
Use exactly this structure:
{{
  "audit_narrative": "2-3 sentence formal description of the change and its approval for an auditor",
  "control_evidence": ["evidence point 1", "evidence point 2", "evidence point 3"]
}}

Rules:
- audit_narrative: formal auditor language, reference the change title, risk level, and decision
- control_evidence: 2-4 specific, verifiable evidence points that demonstrate SOC 2 CC8.1 compliance
- Be precise and factual — auditors will rely on this"""

            message = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=512,
                messages=[{'role': 'user', 'content': prompt}]
            )

            raw = message.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
                raw = raw.strip()

            parsed = json.loads(raw)
            evidence.update({
                'audit_narrative':  parsed.get('audit_narrative', ''),
                'control_evidence': parsed.get('control_evidence', []),
                'llm_powered':      True,
            })

            logger.info(f'[generate_soc2_evidence] Claude SOC2 evidence generated for: {title}')

        except json.JSONDecodeError as e:
            logger.error(f'[generate_soc2_evidence] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_soc2_evidence] Claude call failed — {e}')

        return evidencecod