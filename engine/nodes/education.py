# engine/nodes/education.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_admission_application', sectors=['education'], retry_policy='none')
class ValidateAdmissionApplicationNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['applicant_name', 'program', 'gpa', 'test_score']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'applicant_name': input_data.get('applicant_name', '')}


@register_node(code='check_eligibility_criteria', sectors=['education'], retry_policy='none')
class CheckEligibilityCriteriaNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        gpa           = float(input_data.get('gpa', 0))
        test_score    = int(input_data.get('test_score', 0))
        min_gpa       = float(input_data.get('min_gpa', 2.5))
        min_test      = int(input_data.get('min_test_score', 1000))
        eligible      = gpa >= min_gpa and test_score >= min_test
        return {'eligible': eligible, 'gpa': gpa, 'test_score': test_score,
                'status': 'PASS' if eligible else 'FAIL'}


@register_node(code='grant_compliance_check', sectors=['education'], retry_policy='none')
class GrantComplianceCheckNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        citizenship   = input_data.get('citizenship', '')
        program       = input_data.get('program', '')
        grant_eligible_programs = input_data.get('grant_eligible_programs', [])
        grant_ok      = program in grant_eligible_programs and citizenship == 'domestic'
        return {'grant_eligible': grant_ok, 'program': program,
                'status': 'PASS' if grant_ok else 'NOT_ELIGIBLE'}


@register_node(code='generate_admission_decision', sectors=['education'], retry_policy='bounded')
class GenerateAdmissionDecisionNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        import os, json, anthropic
        human_action   = input_data.get('human_action', {})
        applicant_name = input_data.get('applicant_name', '')
        program        = input_data.get('program', '')
        gpa            = input_data.get('gpa', 0)
        test_score     = input_data.get('test_score', 0)
        grant_eligible = input_data.get('grant_eligible', False)
        out = {
            'status': 'generated', 'applicant_name': applicant_name,
            'decision': human_action.get('action', ''), 'approved_by': human_action.get('actor', ''),
            'admission_letter': '', 'next_steps': [], 'scholarship_note': '', 'llm_powered': False,
        }
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            logger.warning('[generate_admission_decision] ANTHROPIC_API_KEY not set — returning fallback')
            return out
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a university admissions officer writing a formal admission decision.
Applicant: {applicant_name} | Program: {program} | GPA: {gpa} | Test Score: {test_score}
Grant Eligible: {grant_eligible}
Decision: {human_action.get('action','N/A')} by {human_action.get('actor','N/A')}
Justification: {human_action.get('justification','')}
Respond ONLY with valid JSON, no markdown fences:
{{"admission_letter":"2-sentence formal admission or rejection letter","next_steps":["step 1","step 2","step 3"],"scholarship_note":"scholarship or grant information or empty string if not applicable"}}"""
            msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=450,
                                         messages=[{'role':'user','content':prompt}])
            raw = msg.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'): raw = raw[4:]
                raw = raw.strip()
            p = json.loads(raw)
            out.update({'admission_letter': p.get('admission_letter',''), 'next_steps': p.get('next_steps',[]),
                        'scholarship_note': p.get('scholarship_note',''), 'llm_powered': True})
            logger.info('[generate_admission_decision] Claude admission decision generated')
        except json.JSONDecodeError as e:
            logger.error(f'[generate_admission_decision] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_admission_decision] Claude failed — {e}')
        return out