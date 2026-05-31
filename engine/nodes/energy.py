# engine/nodes/energy.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_esg_report', sectors=['energy'], retry_policy='none')
class ValidateESGReportNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['company_name', 'reporting_period', 'carbon_emissions', 'energy_consumption']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'company_name': input_data.get('company_name', '')}


@register_node(code='check_emission_limits', sectors=['energy'], retry_policy='none')
class CheckEmissionLimitsNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        emissions  = float(input_data.get('carbon_emissions', 0))
        limit      = float(input_data.get('emission_limit', 1000))
        exceeded   = emissions > limit
        return {'status': 'FAIL' if exceeded else 'PASS',
                'emissions': emissions, 'limit': limit,
                'excess': max(0, emissions - limit)}


@register_node(code='generate_esg_certificate', sectors=['energy'], retry_policy='bounded')
class GenerateESGCertificateNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return {
            'status':          'generated',
            'company_name':    input_data.get('company_name', ''),
            'carbon_emissions': input_data.get('carbon_emissions', 0),
            'decision':        input_data.get('human_action', {}).get('action', ''),
            'approved_by':     input_data.get('human_action', {}).get('actor', ''),
        }