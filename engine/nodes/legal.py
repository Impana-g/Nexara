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
        return {
            'status':        'generated',
            'title':         input_data.get('title', ''),
            'risk_level':    input_data.get('risk_level', ''),
            'approved_by':   input_data.get('human_action', {}).get('actor', ''),
            'decision':      input_data.get('human_action', {}).get('action', ''),
        }