# engine/nodes/healthcare.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_patient_record', sectors=['healthcare'], retry_policy='none')
class ValidatePatientRecordNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['patient_id', 'name', 'dob', 'diagnosis']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'patient_id': input_data.get('patient_id', '')}


@register_node(code='check_prescription_limits', sectors=['healthcare'], retry_policy='none')
class CheckPrescriptionLimitsNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        dosage     = float(input_data.get('dosage_mg', 0))
        max_dosage = float(input_data.get('max_dosage_mg', 100))
        status     = 'FAIL' if dosage > max_dosage else 'PASS'
        return {'status': status, 'dosage': dosage, 'max_dosage': max_dosage,
                'exceeded_by': max(0, dosage - max_dosage)}


@register_node(code='insurance_eligibility_check', sectors=['healthcare'], retry_policy='none')
class InsuranceEligibilityCheckNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        policy_active  = input_data.get('policy_active', False)
        covered_codes  = input_data.get('covered_diagnosis_codes', [])
        diagnosis_code = input_data.get('diagnosis_code', '')
        eligible       = policy_active and (not covered_codes or diagnosis_code in covered_codes)
        return {'eligible': eligible, 'policy_active': policy_active,
                'diagnosis_code': diagnosis_code,
                'status': 'PASS' if eligible else 'REQUIRES_APPROVAL'}


@register_node(code='generate_clinical_summary', sectors=['healthcare'], retry_policy='bounded')
class GenerateClinicalSummaryNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return {
            'status':       'generated',
            'patient_id':   input_data.get('patient_id', ''),
            'diagnosis':    input_data.get('diagnosis', ''),
            'approved_by':  input_data.get('human_action', {}).get('actor', ''),
            'decision':     input_data.get('human_action', {}).get('action', ''),
        }