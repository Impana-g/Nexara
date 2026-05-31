# engine/nodes/telecom.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_license_application', sectors=['telecom'], retry_policy='none')
class ValidateLicenseApplicationNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['operator_name', 'license_type', 'spectrum_band', 'region']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'operator_name': input_data.get('operator_name', '')}


@register_node(code='check_spectrum_availability', sectors=['telecom'], retry_policy='none')
class CheckSpectrumAvailabilityNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        spectrum_band    = input_data.get('spectrum_band', '')
        occupied_bands   = input_data.get('occupied_bands', [])
        available        = spectrum_band not in occupied_bands
        return {'available': available, 'spectrum_band': spectrum_band,
                'status': 'PASS' if available else 'FAIL'}


@register_node(code='generate_license_decision', sectors=['telecom'], retry_policy='bounded')
class GenerateLicenseDecisionNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return {
            'status':         'generated',
            'operator_name':  input_data.get('operator_name', ''),
            'spectrum_band':  input_data.get('spectrum_band', ''),
            'decision':       input_data.get('human_action', {}).get('action', ''),
            'approved_by':    input_data.get('human_action', {}).get('actor', ''),
        }