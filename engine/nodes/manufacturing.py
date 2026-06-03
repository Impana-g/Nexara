# engine/nodes/manufacturing.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_quality_inspection', sectors=['manufacturing'], retry_policy='none')
class ValidateQualityInspectionNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['batch_id', 'product_name', 'defect_rate', 'units_inspected']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'batch_id': input_data.get('batch_id', '')}


@register_node(code='check_defect_rate', sectors=['manufacturing'], retry_policy='none')
class CheckDefectRateNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        defect_rate     = float(input_data.get('defect_rate', 0))
        threshold       = float(input_data.get('defect_threshold', 2.0))
        units_inspected = int(input_data.get('units_inspected', 0))
        failed          = defect_rate > threshold
        return {'status': 'FAIL' if failed else 'PASS',
                'defect_rate': defect_rate, 'threshold': threshold,
                'units_inspected': units_inspected,
                'requires_rework': failed}


@register_node(code='generate_quality_certificate', sectors=['manufacturing'], retry_policy='bounded')
class GenerateQualityCertificateNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action    = input_data.get('human_action', {})
        batch_id        = input_data.get('batch_id', '')
        product_name    = input_data.get('product_name', '')
        defect_rate     = input_data.get('defect_rate', 0)
        threshold       = input_data.get('defect_threshold', 2.0)
        units_inspected = input_data.get('units_inspected', 0)
        out = {
            'status': 'generated', 'batch_id': batch_id,
            'decision': human_action.get('action', ''), 'approved_by': human_action.get('actor', ''),
            'quality_verdict': '', 'corrective_actions': [], 'release_conditions': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_quality_certificate] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a quality assurance manager issuing a batch quality certificate.
Batch: {batch_id} | Product: {product_name}
Defect Rate: {defect_rate}% (Threshold: {threshold}%) | Units Inspected: {units_inspected}
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"quality_verdict":"2-sentence quality pass/fail verdict","corrective_actions":["action 1","action 2"],"release_conditions":"conditions for batch release or empty string if unconditional pass"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=400,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'quality_verdict': p.get('quality_verdict',''), 'corrective_actions': p.get('corrective_actions',[]),
                        'release_conditions': p.get('release_conditions',''), 'llm_powered': True})
            logger.info('[generate_quality_certificate] Claude quality certificate generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_quality_certificate] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_quality_certificate] Claude failed — {e}')
        return out