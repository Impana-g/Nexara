# engine/nodes/telecom.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_license_application', sectors=['telecom'], retry_policy='none')
class ValidateLicenseApplicationNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['applicant_name', 'license_type', 'frequency_band', 'coverage_area']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'applicant_name': input_data.get('applicant_name', '')}


@register_node(code='check_spectrum_availability', sectors=['telecom'], retry_policy='none')
class CheckSpectrumAvailabilityNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        frequency_band    = input_data.get('frequency_band', '')
        coverage_area     = input_data.get('coverage_area', '')
        occupied_bands    = input_data.get('occupied_bands', [])
        available         = frequency_band not in occupied_bands
        return {'available': available, 'frequency_band': frequency_band,
                'status': 'PASS' if available else 'FAIL',
                'coverage_area': coverage_area}


@register_node(code='generate_license_decision', sectors=['telecom'], retry_policy='bounded')
class GenerateLicenseDecisionNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action   = input_data.get('human_action', {})
        applicant_name = input_data.get('applicant_name', '')
        license_type   = input_data.get('license_type', '')
        frequency_band = input_data.get('frequency_band', '')
        coverage_area  = input_data.get('coverage_area', '')
        available      = input_data.get('available', False)
        out = {
            'status': 'generated', 'applicant_name': applicant_name,
            'decision': human_action.get('action', ''), 'approved_by': human_action.get('actor', ''),
            'license_summary': '', 'regulatory_conditions': [], 'coverage_obligations': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_license_decision] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a telecom regulatory officer issuing a spectrum license decision.
Applicant: {applicant_name} | License Type: {license_type}
Frequency Band: {frequency_band} | Coverage Area: {coverage_area} | Band Available: {available}
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"license_summary":"2-sentence license grant or denial summary","regulatory_conditions":["condition 1","condition 2"],"coverage_obligations":"coverage rollout obligations or empty string if denied"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=400,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'license_summary': p.get('license_summary',''), 'regulatory_conditions': p.get('regulatory_conditions',[]),
                        'coverage_obligations': p.get('coverage_obligations',''), 'llm_powered': True})
            logger.info('[generate_license_decision] Claude license decision generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_license_decision] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_license_decision] Claude failed — {e}')
        return out