# engine/nodes/cybersecurity.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_security_incident', sectors=['cybersecurity'], retry_policy='none')
class ValidateSecurityIncidentNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['incident_id', 'severity', 'affected_systems', 'reported_by']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'incident_id': input_data.get('incident_id', '')}


@register_node(code='assess_threat_level', sectors=['cybersecurity'], retry_policy='none')
class AssessThreatLevelNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        severity          = input_data.get('severity', 'low')
        affected_systems  = input_data.get('affected_systems', [])
        data_breach       = input_data.get('data_breach', False)
        score = 0
        if severity == 'critical':  score += 40
        elif severity == 'high':    score += 30
        elif severity == 'medium':  score += 20
        else:                       score += 10
        score += len(affected_systems) * 5
        if data_breach: score += 30
        threat = 'CRITICAL' if score >= 60 else 'HIGH' if score >= 40 else 'MEDIUM' if score >= 20 else 'LOW'
        return {'threat_level': threat, 'threat_score': score,
                'requires_escalation': score >= 60, 'data_breach': data_breach,
                'status': 'PASS'}


@register_node(code='check_regulatory_notification', sectors=['cybersecurity'], retry_policy='none')
class CheckRegulatoryNotificationNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        data_breach    = input_data.get('data_breach', False)
        records_count  = int(input_data.get('affected_records', 0))
        gdpr_required  = data_breach and records_count > 0
        return {'gdpr_notification_required': gdpr_required,
                'affected_records': records_count,
                'notification_deadline_hours': 72 if gdpr_required else 0,
                'status': 'PASS'}


@register_node(code='generate_incident_report', sectors=['cybersecurity'], retry_policy='bounded')
class GenerateIncidentReportNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return {
            'status':          'generated',
            'incident_id':     input_data.get('incident_id', ''),
            'threat_level':    input_data.get('threat_level', ''),
            'data_breach':     input_data.get('data_breach', False),
            'decision':        input_data.get('human_action', {}).get('action', ''),
            'approved_by':     input_data.get('human_action', {}).get('actor', ''),
        }