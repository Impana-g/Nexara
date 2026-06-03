# engine/nodes/insurance.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_claim', sectors=['insurance'], retry_policy='none')
class ValidateClaimNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['claim_id', 'policy_number', 'claim_type', 'amount', 'incident_date']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'claim_id': input_data.get('claim_id', ''),
                'claim_type': input_data.get('claim_type', '')}


@register_node(code='fraud_detection_check', sectors=['insurance'], retry_policy='none')
class FraudDetectionCheckNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        amount           = float(input_data.get('amount', 0))
        claim_type       = input_data.get('claim_type', '')
        prior_claims     = int(input_data.get('prior_claims_count', 0))
        flagged_policies = input_data.get('flagged_policies', [])
        policy_number    = input_data.get('policy_number', '')
        score = 0
        if amount > 500000:    score += 30
        elif amount > 100000:  score += 15
        if prior_claims > 3:   score += 25
        if policy_number in flagged_policies: score += 40
        risk = 'HIGH' if score >= 50 else 'MEDIUM' if score >= 25 else 'LOW'
        return {'fraud_risk': risk, 'fraud_score': score,
                'requires_investigation': score >= 50,
                'status': 'FAIL' if score >= 50 else 'PASS'}


@register_node(code='calculate_settlement', sectors=['insurance'], retry_policy='none')
class CalculateSettlementNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        amount      = float(input_data.get('amount', 0))
        claim_type  = input_data.get('claim_type', '')
        deductible  = float(input_data.get('deductible', 0))
        coverage_pct= float(input_data.get('coverage_percentage', 100))
        settlement  = max(0, (amount - deductible) * coverage_pct / 100)
        return {'settlement_amount': round(settlement, 2),
                'original_amount': amount, 'deductible': deductible,
                'coverage_percentage': coverage_pct}


@register_node(code='generate_claim_decision', sectors=['insurance'], retry_policy='bounded')
class GenerateClaimDecisionNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action      = input_data.get('human_action', {})
        claim_id          = input_data.get('claim_id', '')
        claim_type        = input_data.get('claim_type', '')
        amount            = input_data.get('amount', 0)
        settlement_amount = input_data.get('settlement_amount', 0)
        fraud_risk        = input_data.get('fraud_risk', 'LOW')
        out = {
            'status': 'generated', 'claim_id': claim_id,
            'decision': human_action.get('action', ''), 'approved_by': human_action.get('actor', ''),
            'decision_rationale': '', 'payment_instructions': [], 'fraud_notes': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_claim_decision] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are an insurance claims adjuster writing a formal claim decision.
Claim: {claim_id} | Type: {claim_type} | Claimed: {amount} | Settlement: {settlement_amount}
Fraud Risk: {fraud_risk}
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"decision_rationale":"2-sentence rationale for the claim decision","payment_instructions":["step 1","step 2"],"fraud_notes":"fraud risk observations or empty string if low risk"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=400,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'decision_rationale': p.get('decision_rationale',''), 'payment_instructions': p.get('payment_instructions',[]),
                        'fraud_notes': p.get('fraud_notes',''), 'llm_powered': True})
            logger.info('[generate_claim_decision] Claude claim decision generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_claim_decision] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_claim_decision] Claude failed — {e}')
        return out