# engine/nodes/legal.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_contract', sectors=['legal'], retry_policy='none')
class ValidateContractNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['title', 'parties', 'contract_type', 'value', 'start_date']
        missing  = [f for f in required if not input_data.get(f)]
        status   = 'FAIL' if missing else 'PASS'
        return {'status': status, 'missing_fields': missing,
                'title': input_data.get('title', ''),
                'contract_type': input_data.get('contract_type', '')}


@register_node(code='conflict_of_interest_check', sectors=['legal'], retry_policy='none')
class ConflictOfInterestCheckNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        parties          = input_data.get('parties', [])
        flagged_entities = input_data.get('flagged_entities', [])
        conflicts        = [p for p in parties if p in flagged_entities]
        status           = 'FAIL' if conflicts else 'PASS'
        return {'status': status, 'conflicts': conflicts, 'parties': parties}


@register_node(code='legal_risk_assessment', sectors=['legal'], retry_policy='none')
class LegalRiskAssessmentNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        value         = float(input_data.get('value', 0))
        contract_type = input_data.get('contract_type', '')
        jurisdiction  = input_data.get('jurisdiction', 'domestic')
        score = 0
        if value > 1000000:   score += 30
        elif value > 100000:  score += 20
        else:                 score += 10
        if jurisdiction == 'international': score += 20
        if contract_type in ('partnership', 'acquisition'): score += 20
        risk = 'HIGH' if score >= 50 else 'MEDIUM' if score >= 30 else 'LOW'
        return {'risk_level': risk, 'risk_score': score, 'requires_legal_review': score >= 30}


@register_node(code='generate_legal_summary', sectors=['legal'], retry_policy='bounded')
class GenerateLegalSummaryNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action  = input_data.get('human_action', {})
        title         = input_data.get('title', '')
        risk_level    = input_data.get('risk_level', '')
        contract_type = input_data.get('contract_type', '')
        value         = input_data.get('value', 0)
        parties       = input_data.get('parties', [])
        out = {
            'status': 'generated', 'title': title, 'risk_level': risk_level,
            'approved_by': human_action.get('actor', ''), 'decision': human_action.get('action', ''),
            'summary': '', 'key_obligations': [], 'risk_notes': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_legal_summary] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a corporate legal analyst. Write a concise contract review summary.
Contract: {title} | Type: {contract_type} | Value: {value} | Risk: {risk_level}
Parties: {parties}
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"summary":"2-sentence executive summary","key_obligations":["obligation 1","obligation 2"],"risk_notes":"1 sentence on key legal risk"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=400,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'summary': p.get('summary',''), 'key_obligations': p.get('key_obligations',[]),
                        'risk_notes': p.get('risk_notes',''), 'llm_powered': True})
            logger.info('[generate_legal_summary] Claude summary generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_legal_summary] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_legal_summary] Claude failed — {e}')
        return out