# engine/nodes/healthcare.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_patient_record', sectors=['healthcare'], retry_policy='none')
class ValidatePatientRecordNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['patient_id', 'diagnosis', 'medications', 'doctor_id']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'patient_id': input_data.get('patient_id', '')}


@register_node(code='check_prescription_limits', sectors=['healthcare'], retry_policy='none')
class CheckPrescriptionLimitsNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        medications   = input_data.get('medications', [])
        controlled    = input_data.get('controlled_substances', [])
        flagged       = [m for m in medications if m in controlled]
        return {'status': 'FAIL' if flagged else 'PASS',
                'flagged_medications': flagged, 'requires_review': bool(flagged)}


@register_node(code='insurance_eligibility_check', sectors=['healthcare'], retry_policy='none')
class InsuranceEligibilityCheckNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        policy_active  = input_data.get('policy_active', False)
        coverage_type  = input_data.get('coverage_type', '')
        diagnosis      = input_data.get('diagnosis', '')
        eligible       = policy_active and bool(coverage_type)
        return {'eligible': eligible, 'coverage_type': coverage_type,
                'status': 'PASS' if eligible else 'FAIL',
                'diagnosis': diagnosis}


@register_node(code='generate_clinical_summary', sectors=['healthcare'], retry_policy='bounded')
class GenerateClinicalSummaryNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action  = input_data.get('human_action', {})
        patient_id    = input_data.get('patient_id', '')
        diagnosis     = input_data.get('diagnosis', '')
        medications   = input_data.get('medications', [])
        coverage_type = input_data.get('coverage_type', '')
        eligible      = input_data.get('eligible', False)
        out = {
            'status': 'generated', 'patient_id': patient_id,
            'decision': human_action.get('action', ''), 'approved_by': human_action.get('actor', ''),
            'clinical_summary': '', 'care_instructions': [], 'contraindications': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_clinical_summary] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a clinical documentation specialist. Write a concise patient care summary.
Patient: {patient_id} | Diagnosis: {diagnosis}
Medications: {medications} | Insurance Coverage: {coverage_type} | Eligible: {eligible}
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"clinical_summary":"2-sentence clinical summary","care_instructions":["instruction 1","instruction 2"],"contraindications":"key contraindications or empty string if none"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=400,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'clinical_summary': p.get('clinical_summary',''), 'care_instructions': p.get('care_instructions',[]),
                        'contraindications': p.get('contraindications',''), 'llm_powered': True})
            logger.info('[generate_clinical_summary] Claude clinical summary generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_clinical_summary] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_clinical_summary] Claude failed — {e}')
        return out