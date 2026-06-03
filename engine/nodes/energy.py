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
        import os, json, anthropic
        human_action     = input_data.get('human_action', {})
        company_name     = input_data.get('company_name', '')
        carbon_emissions = input_data.get('carbon_emissions', 0)
        emission_limit   = input_data.get('emission_limit', 0)
        esg_score        = input_data.get('esg_score', 0)
        reporting_period = input_data.get('reporting_period', '')
        out = {
            'status': 'generated', 'company_name': company_name, 'carbon_emissions': carbon_emissions,
            'decision': human_action.get('action',''), 'approved_by': human_action.get('actor',''),
            'certificate_text': '', 'compliance_findings': [], 'improvement_areas': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_esg_certificate] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are an ESG compliance officer issuing an environmental certification.
Company: {company_name} | Period: {reporting_period}
Carbon Emissions: {carbon_emissions} (Limit: {emission_limit}) | ESG Score: {esg_score}/100
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"certificate_text":"2-sentence formal certificate or non-compliance notice text","compliance_findings":["finding 1","finding 2"],"improvement_areas":"key area(s) for emissions reduction or empty string if fully compliant"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=400,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'certificate_text': p.get('certificate_text',''), 'compliance_findings': p.get('compliance_findings',[]),
                        'improvement_areas': p.get('improvement_areas',''), 'llm_powered': True})
            logger.info('[generate_esg_certificate] Claude ESG certificate generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_esg_certificate] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_esg_certificate] Claude failed — {e}')
        return out