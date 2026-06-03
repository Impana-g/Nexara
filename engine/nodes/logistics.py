# engine/nodes/logistics.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_shipment', sectors=['logistics'], retry_policy='none')
class ValidateShipmentNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['shipment_id', 'origin_country', 'destination_country', 'cargo_type', 'weight_kg']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'shipment_id': input_data.get('shipment_id', '')}


@register_node(code='check_customs_compliance', sectors=['logistics'], retry_policy='none')
class CheckCustomsComplianceNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        cargo_type        = input_data.get('cargo_type', '')
        destination       = input_data.get('destination_country', '')
        restricted_cargo  = input_data.get('restricted_cargo_types', [])
        embargoed         = input_data.get('embargoed_countries', [])
        cargo_ok          = cargo_type not in restricted_cargo
        country_ok        = destination not in embargoed
        status = 'PASS' if (cargo_ok and country_ok) else 'FAIL'
        return {'status': status, 'cargo_restricted': not cargo_ok,
                'country_embargoed': not country_ok,
                'destination': destination}


@register_node(code='generate_shipping_clearance', sectors=['logistics'], retry_policy='bounded')
class GenerateShippingClearanceNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action        = input_data.get('human_action', {})
        shipment_id         = input_data.get('shipment_id', '')
        origin_country      = input_data.get('origin_country', '')
        destination_country = input_data.get('destination_country', '')
        cargo_type          = input_data.get('cargo_type', '')
        weight_kg           = input_data.get('weight_kg', 0)
        out = {
            'status': 'generated', 'shipment_id': shipment_id,
            'decision': human_action.get('action', ''), 'approved_by': human_action.get('actor', ''),
            'clearance_notes': '', 'customs_instructions': [], 'handling_requirements': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_shipping_clearance] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a customs clearance officer issuing a shipping clearance document.
Shipment: {shipment_id} | Origin: {origin_country} | Destination: {destination_country}
Cargo: {cargo_type} | Weight: {weight_kg}kg
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"clearance_notes":"2-sentence customs clearance or hold notice","customs_instructions":["instruction 1","instruction 2"],"handling_requirements":"special handling or storage requirements, or empty string if standard"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=400,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'clearance_notes': p.get('clearance_notes',''), 'customs_instructions': p.get('customs_instructions',[]),
                        'handling_requirements': p.get('handling_requirements',''), 'llm_powered': True})
            logger.info('[generate_shipping_clearance] Claude clearance generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_shipping_clearance] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_shipping_clearance] Claude failed — {e}')
        return out