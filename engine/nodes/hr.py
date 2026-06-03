# engine/nodes/hr.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(
    code='validate_job_requisition',
    sectors=['hr'],
    retry_policy='none'
)
class ValidateJobRequisitionNode(BaseNode):
    """
    Validates job requisition completeness.
    Checks title, department, budget range.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['title', 'department', 'budget_min', 'budget_max', 'requested_by']
        missing  = [f for f in required if not input_data.get(f)]

        status = 'FAIL' if missing else 'PASS'
        logger.info(f'validate_job_requisition: {status}')

        return {
            'status':        status,
            'missing_fields': missing,
            'title':         input_data.get('title', ''),
            'department':    input_data.get('department', ''),
            'budget_min':    input_data.get('budget_min', 0),
            'budget_max':    input_data.get('budget_max', 0),
        }


@register_node(
    code='validate_salary_band',
    sectors=['hr'],
    retry_policy='none'
)
class ValidateSalaryBandNode(BaseNode):
    """
    Checks if offered salary is within approved band.
    Returns PASS, WARN, or REQUIRES_APPROVAL.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        offered     = float(input_data.get('offered_salary', 0))
        band_min    = float(input_data.get('salary_band_min', 0))
        band_max    = float(input_data.get('salary_band_max', 0))

        if offered < band_min:
            status = 'WARN'
            reason = 'Salary below band minimum'
        elif offered > band_max:
            status = 'REQUIRES_APPROVAL'
            reason = 'Salary exceeds band maximum'
        else:
            status = 'PASS'
            reason = 'Salary within approved band'

        logger.info(f'validate_salary_band: {status} — offered={offered}')

        return {
            'status':       status,
            'reason':       reason,
            'offered':      offered,
            'band_min':     band_min,
            'band_max':     band_max,
            'variance_pct': round((offered - band_max) / band_max * 100, 2) if band_max else 0,
        }


@register_node(
    code='check_headcount_budget',
    sectors=['hr'],
    retry_policy='none'
)
class CheckHeadcountBudgetNode(BaseNode):
    """
    Checks if department has approved headcount and budget.
    Returns PASS or REQUIRES_APPROVAL.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        department          = input_data.get('department', '')
        approved_headcount  = input_data.get('approved_headcount', 0)
        current_headcount   = input_data.get('current_headcount', 0)
        budget_utilized_pct = input_data.get('budget_utilized_pct', 0)

        if current_headcount >= approved_headcount:
            status = 'REQUIRES_APPROVAL'
            reason = 'Headcount limit reached for department'
        elif budget_utilized_pct >= 90:
            status = 'REQUIRES_APPROVAL'
            reason = 'Department budget 90% utilized'
        else:
            status = 'PASS'
            reason = 'Headcount and budget available'

        logger.info(f'check_headcount_budget: {status} — dept={department}')

        return {
            'status':               status,
            'reason':               reason,
            'department':           department,
            'approved_headcount':   approved_headcount,
            'current_headcount':    current_headcount,
            'budget_utilized_pct':  budget_utilized_pct,
        }


@register_node(
    code='generate_offer_letter',
    sectors=['hr'],
    retry_policy='bounded'
)
class GenerateOfferLetterNode(BaseNode):
    """
    Claude-powered offer letter generator.
    Produces a professional, complete offer letter
    from candidate details and approved compensation.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        import os
        import json
        import anthropic

        candidate_name  = input_data.get('candidate_name', '')
        designation     = input_data.get('designation', '')
        department      = input_data.get('department', '')
        offered_salary  = input_data.get('offered_salary', 0)
        joining_date    = input_data.get('joining_date', '')
        human_action    = input_data.get('human_action', {})

        if human_action.get('action') == 'REJECTED':
            return {
                'status':    'rejected',
                'reason':    human_action.get('justification', ''),
                'candidate': candidate_name,
                'llm_powered': False,
            }

        # safe fallback
        offer = {
            'status':         'generated',
            'candidate_name': candidate_name,
            'designation':    designation,
            'department':     department,
            'offered_salary': offered_salary,
            'joining_date':   joining_date,
            'approved_by':    human_action.get('actor', ''),
            'offer_letter':   f'Dear {candidate_name}, We are pleased to offer you the position of {designation} in the {department} department with a salary of {offered_salary}.',
            'subject_line':   f'Offer of Employment — {designation}',
            'llm_powered':    False,
        }

        try:
            api_key = os.environ.get('ANTHROPIC_API_KEY', '')
            if not api_key:
                logger.warning('[generate_offer_letter] ANTHROPIC_API_KEY not set — returning fallback')
                return offer

            client = anthropic.Anthropic(api_key=api_key)

            prompt = f"""You are an HR professional writing a formal employment offer letter.

Candidate Details:
- Name: {candidate_name}
- Designation: {designation}
- Department: {department}
- Offered Salary: {offered_salary}
- Joining Date: {joining_date if joining_date else 'To be confirmed'}
- Approved by: {human_action.get('actor', 'HR Manager')}

Write a professional offer letter. Respond ONLY with a valid JSON object. No markdown, no code fences.
Use exactly this structure:
{{
  "subject_line": "email subject line for the offer",
  "offer_letter": "the full text of the offer letter — formal, warm, professional tone. Include all key details. 3-4 paragraphs."
}}

Rules:
- Address the candidate by name
- State the role, department, and salary clearly
- Include joining date if provided
- End with instructions to accept by signing and returning
- Keep it under 300 words"""

            message = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=700,
                messages=[{'role': 'user', 'content': prompt}]
            )

            raw = message.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
                raw = raw.strip()

            parsed = json.loads(raw)
            offer.update({
                'offer_letter':  parsed.get('offer_letter', offer['offer_letter']),
                'subject_line':  parsed.get('subject_line', offer['subject_line']),
                'llm_powered':   True,
            })

            logger.info(f'[generate_offer_letter] Claude offer letter generated for {candidate_name}')

        except json.JSONDecodeError as e:
            logger.error(f'[generate_offer_letter] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_offer_letter] Claude call failed — {e}')

        return offer


@register_node(
    code='check_pf_esi_compliance',
    sectors=['hr'],
    retry_policy='none'
)
class CheckPFESIComplianceNode(BaseNode):
    """
    Validates PF and ESI deductions are correct
    per statutory requirements.
    PF = 12% of basic, ESI = 0.75% of gross (if salary <= 21000).
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        basic_salary   = float(input_data.get('basic_salary', 0))
        pf_deduction   = float(input_data.get('pf_deduction', 0))
        esi_deduction  = float(input_data.get('esi_deduction', 0))
        gross_salary   = float(input_data.get('gross_salary', basic_salary))

        expected_pf    = round(basic_salary * 0.12, 2)
        expected_esi   = round(gross_salary * 0.0075, 2) if gross_salary <= 21000 else 0

        pf_ok  = abs(pf_deduction - expected_pf) < 1
        esi_ok = abs(esi_deduction - expected_esi) < 1

        status = 'PASS' if (pf_ok and esi_ok) else 'FAIL'

        logger.info(f'check_pf_esi_compliance: {status}')

        return {
            'status':       status,
            'pf_ok':        pf_ok,
            'esi_ok':       esi_ok,
            'expected_pf':  expected_pf,
            'expected_esi': expected_esi,
            'actual_pf':    pf_deduction,
            'actual_esi':   esi_deduction,
        }