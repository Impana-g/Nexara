# engine/nodes/retail.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_vendor_onboarding', sectors=['retail'], retry_policy='none')
class ValidateVendorOnboardingNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['vendor_name', 'gst_number', 'category', 'bank_details']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'vendor_name': input_data.get('vendor_name', '')}


@register_node(code='check_return_policy_compliance', sectors=['retail'], retry_policy='none')
class CheckReturnPolicyComplianceNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return_days     = int(input_data.get('return_days_requested', 0))
        policy_max_days = int(input_data.get('return_policy_days', 30))
        compliant       = return_days <= policy_max_days
        return {'compliant': compliant, 'return_days': return_days,
                'policy_max_days': policy_max_days,
                'status': 'PASS' if compliant else 'REQUIRES_APPROVAL'}


@register_node(code='generate_vendor_approval', sectors=['retail'], retry_policy='bounded')
class GenerateVendorApprovalNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action    = input_data.get('human_action', {})
        vendor_name     = input_data.get('vendor_name', '')
        gstin           = input_data.get('gstin', '')
        return_days     = input_data.get('return_days', 0)
        margin_pct      = input_data.get('margin_pct', 0)
        return_compliant= input_data.get('compliant', True)
        out = {
            'status': 'generated', 'vendor_name': vendor_name,
            'decision': human_action.get('action',''), 'approved_by': human_action.get('actor',''),
            'approval_summary': '', 'onboarding_steps': [], 'compliance_notes': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_vendor_approval] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a retail procurement manager issuing a vendor approval decision.
Vendor: {vendor_name} | GSTIN: {gstin}
Margin: {margin_pct}% | Return Policy Days: {return_days} | Return Policy Compliant: {return_compliant}
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"approval_summary":"2-sentence vendor approval or rejection summary","onboarding_steps":["step 1","step 2","step 3"],"compliance_notes":"any GST or return policy compliance notes, or empty string"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=400,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'approval_summary': p.get('approval_summary',''), 'onboarding_steps': p.get('onboarding_steps',[]),
                        'compliance_notes': p.get('compliance_notes',''), 'llm_powered': True})
            logger.info('[generate_vendor_approval] Claude vendor approval generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_vendor_approval] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_vendor_approval] Claude failed — {e}')
        return out