# engine/nodes/insurance.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_claim', sectors=['insurance'], retry_policy='none')
class ValidateClaimNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['claim_id', 'policy_number', 'claim_amount', 'incident_date']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'claim_id': input_data.get('claim_id', '')}


@register_node(code='fraud_detection_check', sectors=['insurance'], retry_policy='none')
class FraudDetectionCheckNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        claim_amount    = float(input_data.get('claim_amount', 0))
        policy_limit    = float(input_data.get('policy_limit', 100000))
        prior_claims    = int(input_data.get('prior_claims_count', 0))
        fraud_score     = 0
        if claim_amount > policy_limit * 0.8: fraud_score += 30
        if prior_claims > 3:                  fraud_score += 30
        if input_data.get('incident_suspicious', False): fraud_score += 40
        risk = 'HIGH' if fraud_score >= 60 else 'MEDIUM' if fraud_score >= 30 else 'LOW'
        return {'fraud_score': fraud_score, 'fraud_risk': risk,
                'requires_investigation': fraud_score >= 60,
                'status': 'FAIL' if fraud_score >= 60 else 'PASS'}


@register_node(code='calculate_settlement', sectors=['insurance'], retry_policy='none')
class CalculateSettlementNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        claim_amount  = float(input_data.get('claim_amount', 0))
        deductible    = float(input_data.get('deductible', 0))
        coverage_pct  = float(input_data.get('coverage_pct', 100))
        settlement    = (claim_amount - deductible) * (coverage_pct / 100)
        return {'settlement_amount': max(0, round(settlement, 2)),
                'claim_amount': claim_amount, 'deductible': deductible,
                'status': 'PASS'}


@register_node(code='generate_claim_decision', sectors=['insurance'], retry_policy='bounded')
class GenerateClaimDecisionNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return {
            'status':            'generated',
            'claim_id':          input_data.get('claim_id', ''),
            'settlement_amount': input_data.get('settlement_amount', 0),
            'decision':          input_data.get('human_action', {}).get('action', ''),
            'approved_by':       input_data.get('human_action', {}).get('actor', ''),
        }