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
        return {
            'status':       'generated',
            'vendor_name':  input_data.get('vendor_name', ''),
            'decision':     input_data.get('human_action', {}).get('action', ''),
            'approved_by':  input_data.get('human_action', {}).get('actor', ''),
        }