# engine/nodes/education.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_admission_application', sectors=['education'], retry_policy='none')
class ValidateAdmissionApplicationNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['applicant_name', 'program', 'qualifications', 'dob']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'applicant_name': input_data.get('applicant_name', ''),
                'program': input_data.get('program', '')}


@register_node(code='check_eligibility_criteria', sectors=['education'], retry_policy='none')
class CheckEligibilityCriteriaNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        min_score      = float(input_data.get('min_score_required', 60))
        applicant_score = float(input_data.get('applicant_score', 0))
        eligible       = applicant_score >= min_score
        return {'eligible': eligible, 'applicant_score': applicant_score,
                'min_score': min_score,
                'status': 'PASS' if eligible else 'FAIL'}


@register_node(code='grant_compliance_check', sectors=['education'], retry_policy='none')
class GrantComplianceCheckNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        grant_amount  = float(input_data.get('grant_amount', 0))
        budget_limit  = float(input_data.get('budget_limit', 50000))
        compliant     = grant_amount <= budget_limit
        return {'compliant': compliant, 'grant_amount': grant_amount,
                'budget_limit': budget_limit,
                'status': 'PASS' if compliant else 'REQUIRES_APPROVAL'}


@register_node(code='generate_admission_decision', sectors=['education'], retry_policy='bounded')
class GenerateAdmissionDecisionNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return {
            'status':         'generated',
            'applicant_name': input_data.get('applicant_name', ''),
            'program':        input_data.get('program', ''),
            'decision':       input_data.get('human_action', {}).get('action', ''),
            'approved_by':    input_data.get('human_action', {}).get('actor', ''),
        }