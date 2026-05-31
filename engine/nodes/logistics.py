# engine/nodes/logistics.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_shipment', sectors=['logistics'], retry_policy='none')
class ValidateShipmentNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['shipment_id', 'origin', 'destination', 'cargo_type', 'weight_kg']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'shipment_id': input_data.get('shipment_id', '')}


@register_node(code='check_customs_compliance', sectors=['logistics'], retry_policy='none')
class CheckCustomsComplianceNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        cargo_type       = input_data.get('cargo_type', '')
        restricted_items = input_data.get('restricted_items', [])
        declared_value   = float(input_data.get('declared_value', 0))
        flagged          = cargo_type in restricted_items
        requires_customs = declared_value > 1000
        status           = 'FAIL' if flagged else 'PASS'
        return {'status': status, 'flagged': flagged,
                'requires_customs_clearance': requires_customs,
                'declared_value': declared_value}


@register_node(code='generate_shipping_clearance', sectors=['logistics'], retry_policy='bounded')
class GenerateShippingClearanceNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return {
            'status':       'generated',
            'shipment_id':  input_data.get('shipment_id', ''),
            'decision':     input_data.get('human_action', {}).get('action', ''),
            'approved_by':  input_data.get('human_action', {}).get('actor', ''),
        }