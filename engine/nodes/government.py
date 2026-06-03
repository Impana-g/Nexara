# engine/nodes/government.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_tender', sectors=['government'], retry_policy='none')
class ValidateTenderNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['tender_id', 'department', 'vendor_name', 'bid_amount', 'project_scope']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'tender_id': input_data.get('tender_id', '')}


@register_node(code='check_procurement_policy', sectors=['government'], retry_policy='none')
class CheckProcurementPolicyNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        bid_amount   = float(input_data.get('bid_amount', 0))
        budget_limit = float(input_data.get('budget_limit', 0))
        vendor_name  = input_data.get('vendor_name', '')
        blacklisted  = input_data.get('blacklisted_vendors', [])
        over_budget  = budget_limit > 0 and bid_amount > budget_limit
        is_blacklisted = vendor_name in blacklisted
        status = 'FAIL' if (over_budget or is_blacklisted) else 'PASS'
        return {'status': status, 'over_budget': over_budget,
                'is_blacklisted': is_blacklisted, 'bid_amount': bid_amount}


@register_node(code='generate_tender_report', sectors=['government'], retry_policy='bounded')
class GenerateTenderReportNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action  = input_data.get('human_action', {})
        tender_id     = input_data.get('tender_id', '')
        department    = input_data.get('department', '')
        vendor_name   = input_data.get('vendor_name', '')
        bid_amount    = input_data.get('bid_amount', 0)
        project_scope = input_data.get('project_scope', '')
        out = {
            'status': 'generated', 'tender_id': tender_id,
            'decision': human_action.get('action', ''), 'approved_by': human_action.get('actor', ''),
            'procurement_summary': '', 'transparency_notes': [], 'audit_trail': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_tender_report] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a government procurement officer writing a formal tender evaluation report.
Tender: {tender_id} | Department: {department} | Vendor: {vendor_name}
Bid Amount: {bid_amount} | Scope: {project_scope}
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"procurement_summary":"2-sentence procurement decision summary","transparency_notes":["note 1","note 2"],"audit_trail":"1-sentence audit trail entry for this decision"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=400,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'procurement_summary': p.get('procurement_summary',''), 'transparency_notes': p.get('transparency_notes',[]),
                        'audit_trail': p.get('audit_trail',''), 'llm_powered': True})
            logger.info('[generate_tender_report] Claude tender report generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_tender_report] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_tender_report] Claude failed — {e}')
        return out