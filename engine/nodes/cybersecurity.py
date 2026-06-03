# engine/nodes/cybersecurity.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_security_incident', sectors=['cybersecurity'], retry_policy='none')
class ValidateSecurityIncidentNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['incident_id', 'incident_type', 'affected_systems', 'detected_at']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'incident_id': input_data.get('incident_id', '')}


@register_node(code='assess_threat_level', sectors=['cybersecurity'], retry_policy='none')
class AssessThreatLevelNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        incident_type    = input_data.get('incident_type', '')
        affected_systems = input_data.get('affected_systems', [])
        data_exfiltrated = input_data.get('data_exfiltrated', False)
        critical_types   = {'ransomware', 'apt', 'data_breach', 'zero_day'}
        score = 0
        if incident_type.lower() in critical_types: score += 40
        if len(affected_systems) > 5:  score += 20
        elif len(affected_systems) > 1: score += 10
        if data_exfiltrated: score += 30
        level = 'CRITICAL' if score >= 60 else 'HIGH' if score >= 40 else 'MEDIUM' if score >= 20 else 'LOW'
        return {'threat_level': level, 'threat_score': score,
                'requires_immediate_response': score >= 60,
                'status': 'PASS'}


@register_node(code='check_regulatory_notification', sectors=['cybersecurity'], retry_policy='none')
class CheckRegulatoryNotificationNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        threat_level     = input_data.get('threat_level', 'LOW')
        data_exfiltrated = input_data.get('data_exfiltrated', False)
        pii_involved     = input_data.get('pii_involved', False)
        notify_required  = threat_level in ('HIGH', 'CRITICAL') or (data_exfiltrated and pii_involved)
        hours_to_notify  = 72 if notify_required else None
        return {'notification_required': notify_required,
                'hours_to_notify': hours_to_notify,
                'gdpr_applicable': pii_involved,
                'status': 'PASS'}


@register_node(code='generate_incident_report', sectors=['cybersecurity'], retry_policy='bounded')
class GenerateIncidentReportNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action     = input_data.get('human_action', {})
        incident_id      = input_data.get('incident_id', '')
        incident_type    = input_data.get('incident_type', '')
        affected_systems = input_data.get('affected_systems', [])
        threat_level     = input_data.get('threat_level', 'LOW')
        notify_required  = input_data.get('notification_required', False)
        out = {
            'status': 'generated', 'incident_id': incident_id,
            'decision': human_action.get('action', ''), 'approved_by': human_action.get('actor', ''),
            'incident_summary': '', 'containment_actions': [], 'regulatory_obligations': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_incident_report] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a CISO writing a formal cybersecurity incident report.
Incident: {incident_id} | Type: {incident_type} | Threat Level: {threat_level}
Affected Systems: {affected_systems} | Regulatory Notification Required: {notify_required}
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"incident_summary":"2-sentence incident summary and impact assessment","containment_actions":["action 1","action 2","action 3"],"regulatory_obligations":"regulatory notification requirements or empty string if none"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=450,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'incident_summary': p.get('incident_summary',''), 'containment_actions': p.get('containment_actions',[]),
                        'regulatory_obligations': p.get('regulatory_obligations',''), 'llm_powered': True})
            logger.info('[generate_incident_report] Claude incident report generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_incident_report] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_incident_report] Claude failed — {e}')
        return out