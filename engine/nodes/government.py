# engine/nodes/government.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_tender', sectors=['government'], retry_policy='none')
class ValidateTenderNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['tender_id', 'title', 'budget', 'deadline', 'department']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'tender_id': input_data.get('tender_id', '')}


@register_node(code='check_procurement_policy', sectors=['government'], retry_policy='none')
class CheckProcurementPolicyNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        budget         = float(input_data.get('budget', 0))
        bidders_count  = int(input_data.get('bidders_count', 0))
        requires_audit = budget > 500000
        min_bidders    = 3
        status = 'FAIL' if bidders_count < min_bidders else 'PASS'
        return {'status': status, 'requires_audit': requires_audit,
                'bidders_count': bidders_count, 'min_bidders': min_bidders}


@register_node(code='generate_tender_report', sectors=['government'], retry_policy='bounded')
class GenerateTenderReportNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return {
            'status':     'generated',
            'tender_id':  input_data.get('tender_id', ''),
            'decision':   input_data.get('human_action', {}).get('action', ''),
            'approved_by': input_data.get('human_action', {}).get('actor', ''),
        }