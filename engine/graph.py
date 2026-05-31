# engine/graph.py

import logging
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from engine.models import WorkflowRun
from engine.services import WorkflowExecutionService

logger = logging.getLogger('nexara.engine.graph')


# ─── Graph State ──────────────────────────────────────────────────────────────

class WorkflowState(TypedDict):
    """
    Shared state object passed between every node in the graph.
    Each node reads from and writes to this dict.
    """
    run_id:         str
    tenant_id:      str
    sector:         str
    input_data:     dict
    node_outputs:   Annotated[dict, operator.or_]   # merges outputs from each node
    current_node:   str
    status:         str
    error:          str
    human_action:   dict    # populated when HITL node resumes


# ─── Node Wrapper ─────────────────────────────────────────────────────────────

def make_graph_node(node_code: str, service: WorkflowExecutionService):
    """
    Wraps a Nexara node as a LangGraph-compatible function.
    Each graph node function receives state, calls the real node,
    and returns updated state.
    """
    def graph_node(state: WorkflowState) -> dict:
        logger.info(f'Graph executing node: {node_code}')

        # Build input from accumulated node_outputs + original input
        input_data = {
            **state.get('input_data', {}),
            **state.get('node_outputs', {}),
        }

        # Add human_action if this is post-HITL
        if state.get('human_action'):
            input_data['human_action'] = state['human_action']

        try:
            output = service.execute_node(node_code, input_data)
            return {
                'node_outputs': {node_code: output},
                'current_node': node_code,
                'status':       'running',
            }
        except Exception as e:
            logger.error(f'Graph node {node_code} failed: {e}')
            return {
                'current_node': node_code,
                'status':       'failed',
                'error':        str(e),
            }

    graph_node.__name__ = f'node_{node_code}'
    return graph_node


# ─── Finance Graph ────────────────────────────────────────────────────────────

def build_finance_graph(service: WorkflowExecutionService) -> StateGraph:
    """
    Finance portfolio review workflow graph.

    Flow:
        portfolio_import
            → compute_metrics
            → concentration_check
            → suitability_check
            → evaluate_policies     ⏸ HITL pause here (last node before human_decision)
            → human_decision
            → approval_gate
            → generate_report
            → extract_insights
            → END
    """
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'portfolio_import',
        'compute_metrics',
        'concentration_check',
        'suitability_check',
        'evaluate_policies',
        'human_decision',
        'approval_gate',
        'generate_report',
        'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('portfolio_import')
    graph.add_edge('portfolio_import',    'compute_metrics')
    graph.add_edge('compute_metrics',     'concentration_check')
    graph.add_edge('concentration_check', 'suitability_check')
    graph.add_edge('suitability_check',   'evaluate_policies')
    graph.add_edge('evaluate_policies',   'human_decision')
    graph.add_edge('human_decision',      'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        route       = gate_output.get('route', 'APPROVED')
        if route == 'APPROVED':
            return 'generate_report'
        return END

    graph.add_conditional_edges(
        'approval_gate',
        route_after_approval,
        {
            'generate_report': 'generate_report',
            END: END,
        }
    )

    graph.add_edge('generate_report',  'extract_insights')
    graph.add_edge('extract_insights', END)

    return graph


# ─── IT Graph ─────────────────────────────────────────────────────────────────

def build_it_graph(service: WorkflowExecutionService) -> StateGraph:
    """
    IT Change Request Approval workflow graph.

    Flow:
        validate_change_request
            → check_freeze_window
            → evaluate_risk_level
            → evaluate_policies
            → notify_cab            ⏸ HITL pause here (last node before human_decision)
            → human_decision
            → approval_gate
            → generate_soc2_evidence
            → extract_insights
            → END
    """
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_change_request',
        'check_freeze_window',
        'evaluate_risk_level',
        'evaluate_policies',
        'notify_cab',
        'human_decision',
        'approval_gate',
        'generate_soc2_evidence',
        'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_change_request')
    graph.add_edge('validate_change_request', 'check_freeze_window')
    graph.add_edge('check_freeze_window',      'evaluate_risk_level')
    graph.add_edge('evaluate_risk_level',      'evaluate_policies')
    graph.add_edge('evaluate_policies',        'notify_cab')
    graph.add_edge('notify_cab',               'human_decision')
    graph.add_edge('human_decision',           'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        route       = gate_output.get('route', 'APPROVED')
        if route == 'APPROVED':
            return 'generate_soc2_evidence'
        return END

    graph.add_conditional_edges(
        'approval_gate',
        route_after_approval,
        {
            'generate_soc2_evidence': 'generate_soc2_evidence',
            END: END,
        }
    )

    graph.add_edge('generate_soc2_evidence', 'extract_insights')
    graph.add_edge('extract_insights',        END)

    return graph


# ─── HR Graph ─────────────────────────────────────────────────────────────────
# ─── HR Graph ─────────────────────────────────────────────────────────────────

def build_hr_graph(service: WorkflowExecutionService) -> StateGraph:
    """
    HR Offer Letter Approval workflow graph.

    Flow:
        validate_job_requisition
            → check_headcount_budget
            → validate_salary_band
            → evaluate_policies
            → check_pf_esi_compliance
            → human_decision        ← HR Manager approval (HITL)
            → approval_gate
            → generate_offer_letter
            → END
    """
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_job_requisition',
        'check_headcount_budget',
        'validate_salary_band',
        'evaluate_policies',
        'check_pf_esi_compliance',
        'human_decision',
        'approval_gate',
        'generate_offer_letter',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_job_requisition')
    graph.add_edge('validate_job_requisition', 'check_headcount_budget')
    graph.add_edge('check_headcount_budget',   'validate_salary_band')
    graph.add_edge('validate_salary_band',     'evaluate_policies')
    graph.add_edge('evaluate_policies',        'check_pf_esi_compliance')
    graph.add_edge('check_pf_esi_compliance',  'human_decision')
    graph.add_edge('human_decision',           'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        route       = gate_output.get('route', 'APPROVED')
        if route == 'APPROVED':
            return 'generate_offer_letter'
        return END

    graph.add_conditional_edges(
        'approval_gate',
        route_after_approval,
        {
            'generate_offer_letter': 'generate_offer_letter',
            END: END,
        }
    )

    graph.add_edge('generate_offer_letter', END)
    return graph

def build_legal_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_contract', 'conflict_of_interest_check',
             'legal_risk_assessment', 'evaluate_policies',
             'human_decision', 'approval_gate', 'generate_legal_summary']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_contract')
    graph.add_edge('validate_contract',          'conflict_of_interest_check')
    graph.add_edge('conflict_of_interest_check', 'legal_risk_assessment')
    graph.add_edge('legal_risk_assessment',      'evaluate_policies')
    graph.add_edge('evaluate_policies',          'human_decision')
    graph.add_edge('human_decision',             'approval_gate')
    def route(state):
        return 'generate_legal_summary' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_legal_summary': 'generate_legal_summary', END: END})
    graph.add_edge('generate_legal_summary', END)
    return graph


def build_healthcare_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_patient_record', 'check_prescription_limits',
             'insurance_eligibility_check', 'evaluate_policies',
             'human_decision', 'approval_gate', 'generate_clinical_summary']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_patient_record')
    graph.add_edge('validate_patient_record',    'check_prescription_limits')
    graph.add_edge('check_prescription_limits',  'insurance_eligibility_check')
    graph.add_edge('insurance_eligibility_check','evaluate_policies')
    graph.add_edge('evaluate_policies',          'human_decision')
    graph.add_edge('human_decision',             'approval_gate')
    def route(state):
        return 'generate_clinical_summary' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_clinical_summary': 'generate_clinical_summary', END: END})
    graph.add_edge('generate_clinical_summary', END)
    return graph


def build_insurance_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_claim', 'fraud_detection_check', 'calculate_settlement',
             'evaluate_policies', 'human_decision', 'approval_gate', 'generate_claim_decision']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_claim')
    graph.add_edge('validate_claim',        'fraud_detection_check')
    graph.add_edge('fraud_detection_check', 'calculate_settlement')
    graph.add_edge('calculate_settlement',  'evaluate_policies')
    graph.add_edge('evaluate_policies',     'human_decision')
    graph.add_edge('human_decision',        'approval_gate')
    def route(state):
        return 'generate_claim_decision' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_claim_decision': 'generate_claim_decision', END: END})
    graph.add_edge('generate_claim_decision', END)
    return graph


def build_education_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_admission_application', 'check_eligibility_criteria',
             'grant_compliance_check', 'evaluate_policies',
             'human_decision', 'approval_gate', 'generate_admission_decision']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_admission_application')
    graph.add_edge('validate_admission_application', 'check_eligibility_criteria')
    graph.add_edge('check_eligibility_criteria',     'grant_compliance_check')
    graph.add_edge('grant_compliance_check',         'evaluate_policies')
    graph.add_edge('evaluate_policies',              'human_decision')
    graph.add_edge('human_decision',                 'approval_gate')
    def route(state):
        return 'generate_admission_decision' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_admission_decision': 'generate_admission_decision', END: END})
    graph.add_edge('generate_admission_decision', END)
    return graph


def build_government_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_tender', 'check_procurement_policy', 'evaluate_policies',
             'human_decision', 'approval_gate', 'generate_tender_report']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_tender')
    graph.add_edge('validate_tender',           'check_procurement_policy')
    graph.add_edge('check_procurement_policy',  'evaluate_policies')
    graph.add_edge('evaluate_policies',         'human_decision')
    graph.add_edge('human_decision',            'approval_gate')
    def route(state):
        return 'generate_tender_report' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_tender_report': 'generate_tender_report', END: END})
    graph.add_edge('generate_tender_report', END)
    return graph


def build_energy_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_esg_report', 'check_emission_limits', 'evaluate_policies',
             'human_decision', 'approval_gate', 'generate_esg_certificate']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_esg_report')
    graph.add_edge('validate_esg_report',   'check_emission_limits')
    graph.add_edge('check_emission_limits', 'evaluate_policies')
    graph.add_edge('evaluate_policies',     'human_decision')
    graph.add_edge('human_decision',        'approval_gate')
    def route(state):
        return 'generate_esg_certificate' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_esg_certificate': 'generate_esg_certificate', END: END})
    graph.add_edge('generate_esg_certificate', END)
    return graph


def build_telecom_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_license_application', 'check_spectrum_availability',
             'evaluate_policies', 'human_decision', 'approval_gate', 'generate_license_decision']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_license_application')
    graph.add_edge('validate_license_application', 'check_spectrum_availability')
    graph.add_edge('check_spectrum_availability',  'evaluate_policies')
    graph.add_edge('evaluate_policies',            'human_decision')
    graph.add_edge('human_decision',               'approval_gate')
    def route(state):
        return 'generate_license_decision' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_license_decision': 'generate_license_decision', END: END})
    graph.add_edge('generate_license_decision', END)
    return graph


def build_manufacturing_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_quality_inspection', 'check_defect_rate', 'evaluate_policies',
             'human_decision', 'approval_gate', 'generate_quality_certificate']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_quality_inspection')
    graph.add_edge('validate_quality_inspection', 'check_defect_rate')
    graph.add_edge('check_defect_rate',           'evaluate_policies')
    graph.add_edge('evaluate_policies',           'human_decision')
    graph.add_edge('human_decision',              'approval_gate')
    def route(state):
        return 'generate_quality_certificate' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_quality_certificate': 'generate_quality_certificate', END: END})
    graph.add_edge('generate_quality_certificate', END)
    return graph


def build_logistics_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_shipment', 'check_customs_compliance', 'evaluate_policies',
             'human_decision', 'approval_gate', 'generate_shipping_clearance']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_shipment')
    graph.add_edge('validate_shipment',         'check_customs_compliance')
    graph.add_edge('check_customs_compliance',  'evaluate_policies')
    graph.add_edge('evaluate_policies',         'human_decision')
    graph.add_edge('human_decision',            'approval_gate')
    def route(state):
        return 'generate_shipping_clearance' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_shipping_clearance': 'generate_shipping_clearance', END: END})
    graph.add_edge('generate_shipping_clearance', END)
    return graph


def build_retail_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_vendor_onboarding', 'check_return_policy_compliance',
             'evaluate_policies', 'human_decision', 'approval_gate', 'generate_vendor_approval']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_vendor_onboarding')
    graph.add_edge('validate_vendor_onboarding',      'check_return_policy_compliance')
    graph.add_edge('check_return_policy_compliance',  'evaluate_policies')
    graph.add_edge('evaluate_policies',               'human_decision')
    graph.add_edge('human_decision',                  'approval_gate')
    def route(state):
        return 'generate_vendor_approval' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_vendor_approval': 'generate_vendor_approval', END: END})
    graph.add_edge('generate_vendor_approval', END)
    return graph


def build_cybersecurity_graph(service):
    graph = StateGraph(WorkflowState)
    nodes = ['validate_security_incident', 'assess_threat_level',
             'check_regulatory_notification', 'evaluate_policies',
             'human_decision', 'approval_gate', 'generate_incident_report']
    for code in nodes:
        graph.add_node(code, make_graph_node(code, service))
    graph.set_entry_point('validate_security_incident')
    graph.add_edge('validate_security_incident',    'assess_threat_level')
    graph.add_edge('assess_threat_level',           'check_regulatory_notification')
    graph.add_edge('check_regulatory_notification', 'evaluate_policies')
    graph.add_edge('evaluate_policies',             'human_decision')
    graph.add_edge('human_decision',                'approval_gate')
    def route(state):
        return 'generate_incident_report' if state.get('node_outputs', {}).get('approval_gate', {}).get('route') == 'APPROVED' else END
    graph.add_conditional_edges('approval_gate', route, {'generate_incident_report': 'generate_incident_report', END: END})
    graph.add_edge('generate_incident_report', END)
    return graph

# ─── Graph Registry ───────────────────────────────────────────────────────────

# Maps sector → graph builder function
GRAPH_REGISTRY = {
    'finance':        build_finance_graph,
    'it':             build_it_graph,
    'hr':             build_hr_graph,
    'legal':          build_legal_graph,
    'healthcare':     build_healthcare_graph,
    'insurance':      build_insurance_graph,
    'education':      build_education_graph,
    'government':     build_government_graph,
    'energy':         build_energy_graph,
    'telecom':        build_telecom_graph,
    'manufacturing':  build_manufacturing_graph,
    'logistics':      build_logistics_graph,
    'retail':         build_retail_graph,
    'cybersecurity':  build_cybersecurity_graph,
}

# Last node executed before human_decision per sector
# Used to detect when the graph has paused at HITL
HITL_PAUSE_NODES = {
    'finance': 'evaluate_policies',
    'it':      'notify_cab',
    'hr':      'evaluate_policies',
}


# ─── Main Executor ────────────────────────────────────────────────────────────

def execute_graph(workflow_run: WorkflowRun) -> dict:
    """
    Main entry point called by execute_workflow_task (Celery).
    Builds the correct graph for the sector, runs it, returns output.
    """
    sector = workflow_run.tenant.sector
    run_id = str(workflow_run.id)

    logger.info(f'execute_graph — run_id={run_id} sector={sector}')

    builder_fn = GRAPH_REGISTRY.get(sector)
    if not builder_fn:
        raise ValueError(f'No graph registered for sector: {sector}')

    service      = WorkflowExecutionService(workflow_run)
    graph        = builder_fn(service)
    checkpointer = MemorySaver()
    compiled     = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=['human_decision'],   # HITL pause point
    )

    initial_state: WorkflowState = {
        'run_id':       run_id,
        'tenant_id':    str(workflow_run.tenant.id),
        'sector':       sector,
        'input_data':   workflow_run.input_data,
        'node_outputs': {},
        'current_node': '',
        'status':       'running',
        'error':        '',
        'human_action': {},
    }

    config = {'configurable': {'thread_id': run_id}}

    # Run graph — pauses automatically before human_decision
    final_state = compiled.invoke(initial_state, config=config)

    # Detect HITL pause — last completed node is the one before human_decision
    hitl_pause_node = HITL_PAUSE_NODES.get(sector, '')
    current         = final_state.get('current_node', '')

    if final_state.get('status') != 'failed' and current == hitl_pause_node:
        workflow_run.status          = WorkflowRun.Status.WAITING
        workflow_run.graph_thread_id = run_id
        workflow_run.save()
        logger.info(f'Graph paused at HITL — run_id={run_id} last_node={current}')
        return {'status': 'waiting_for_input', 'run_id': run_id}

    if final_state.get('status') == 'failed':
        service.fail(final_state.get('error', 'unknown error'))
        return {'status': 'failed'}

    output = final_state.get('node_outputs', {})
    service.complete(output)
    return output


# ─── Resume Executor ──────────────────────────────────────────────────────────

def resume_graph(workflow_run: WorkflowRun, action: str, actor: str,
                 reason_code: str, justification: str) -> dict:
    """
    Resumes a paused WorkflowRun after a human decision is submitted.
    Called by resume_workflow_task (Celery).
    """
    sector = workflow_run.tenant.sector
    run_id = str(workflow_run.id)

    logger.info(f'resume_graph — run_id={run_id} action={action}')

    builder_fn = GRAPH_REGISTRY.get(sector)
    if not builder_fn:
        raise ValueError(f'No graph registered for sector: {sector}')

    service      = WorkflowExecutionService(workflow_run)
    graph        = builder_fn(service)
    checkpointer = MemorySaver()
    compiled     = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=['human_decision'],
    )

    config = {'configurable': {'thread_id': run_id}}

    # Resume with human action injected into state
    resume_state = {
        'human_action': {
            'action':        action,
            'actor':         actor,
            'reason_code':   reason_code,
            'justification': justification,
        },
        'status': 'running',
    }

    final_state = compiled.invoke(resume_state, config=config)

    if final_state.get('status') == 'failed':
        service.fail(final_state.get('error', 'unknown error'))
        return {'status': 'failed'}

    output = final_state.get('node_outputs', {})
    service.complete(output)
    return output