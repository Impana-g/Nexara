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
    node_outputs:   Annotated[dict, operator.or_]
    current_node:   str
    status:         str
    error:          str
    human_action:   dict


# ─── Node Wrapper ─────────────────────────────────────────────────────────────

def make_graph_node(node_code: str, service: WorkflowExecutionService):
    def graph_node(state: WorkflowState) -> dict:
        logger.info(f'Graph executing node: {node_code}')

        input_data = {
            **state.get('input_data', {}),
            **state.get('node_outputs', {}),
        }

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
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'portfolio_import', 'compute_metrics', 'concentration_check',
        'suitability_check', 'evaluate_policies', 'human_decision',
        'approval_gate', 'generate_report', 'extract_insights',
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

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_report': 'generate_report', END: END})
    graph.add_edge('generate_report',  'extract_insights')
    graph.add_edge('extract_insights', END)
    return graph


# ─── IT Graph ─────────────────────────────────────────────────────────────────

def build_it_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_change_request', 'check_freeze_window', 'evaluate_risk_level',
        'evaluate_policies', 'notify_cab', 'human_decision', 'approval_gate',
        'generate_soc2_evidence', 'extract_insights',
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

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_soc2_evidence': 'generate_soc2_evidence', END: END})
    graph.add_edge('generate_soc2_evidence', 'extract_insights')
    graph.add_edge('extract_insights',        END)
    return graph


# ─── HR Graph ─────────────────────────────────────────────────────────────────

def build_hr_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_job_requisition', 'check_headcount_budget', 'validate_salary_band',
        'evaluate_policies', 'check_pf_esi_compliance', 'human_decision',
        'approval_gate', 'generate_offer_letter', 'extract_insights',
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

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_offer_letter': 'generate_offer_letter', END: END})
    graph.add_edge('generate_offer_letter', 'extract_insights')
    graph.add_edge('extract_insights',      END)
    return graph


# ─── Legal Graph ──────────────────────────────────────────────────────────────

def build_legal_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_contract', 'conflict_of_interest_check', 'legal_risk_assessment',
        'evaluate_policies', 'human_decision', 'approval_gate',
        'generate_legal_summary', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_contract')
    graph.add_edge('validate_contract',          'conflict_of_interest_check')
    graph.add_edge('conflict_of_interest_check', 'legal_risk_assessment')
    graph.add_edge('legal_risk_assessment',      'evaluate_policies')
    graph.add_edge('evaluate_policies',          'human_decision')
    graph.add_edge('human_decision',             'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_legal_summary' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_legal_summary': 'generate_legal_summary', END: END})
    graph.add_edge('generate_legal_summary', 'extract_insights')
    graph.add_edge('extract_insights',       END)
    return graph


# ─── Healthcare Graph ─────────────────────────────────────────────────────────

def build_healthcare_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_patient_record', 'check_prescription_limits',
        'insurance_eligibility_check', 'evaluate_policies', 'human_decision',
        'approval_gate', 'generate_clinical_summary', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_patient_record')
    graph.add_edge('validate_patient_record',   'check_prescription_limits')
    graph.add_edge('check_prescription_limits', 'insurance_eligibility_check')
    graph.add_edge('insurance_eligibility_check', 'evaluate_policies')
    graph.add_edge('evaluate_policies',         'human_decision')
    graph.add_edge('human_decision',            'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_clinical_summary' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_clinical_summary': 'generate_clinical_summary', END: END})
    graph.add_edge('generate_clinical_summary', 'extract_insights')
    graph.add_edge('extract_insights',          END)
    return graph


# ─── Insurance Graph ──────────────────────────────────────────────────────────

def build_insurance_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_claim', 'fraud_detection_check', 'calculate_settlement',
        'evaluate_policies', 'human_decision', 'approval_gate',
        'generate_claim_decision', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_claim')
    graph.add_edge('validate_claim',       'fraud_detection_check')
    graph.add_edge('fraud_detection_check', 'calculate_settlement')
    graph.add_edge('calculate_settlement', 'evaluate_policies')
    graph.add_edge('evaluate_policies',    'human_decision')
    graph.add_edge('human_decision',       'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_claim_decision' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_claim_decision': 'generate_claim_decision', END: END})
    graph.add_edge('generate_claim_decision', 'extract_insights')
    graph.add_edge('extract_insights',        END)
    return graph


# ─── Education Graph ──────────────────────────────────────────────────────────

def build_education_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_admission_application', 'check_eligibility_criteria',
        'grant_compliance_check', 'evaluate_policies', 'human_decision',
        'approval_gate', 'generate_admission_decision', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_admission_application')
    graph.add_edge('validate_admission_application', 'check_eligibility_criteria')
    graph.add_edge('check_eligibility_criteria',     'grant_compliance_check')
    graph.add_edge('grant_compliance_check',         'evaluate_policies')
    graph.add_edge('evaluate_policies',              'human_decision')
    graph.add_edge('human_decision',                 'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_admission_decision' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_admission_decision': 'generate_admission_decision', END: END})
    graph.add_edge('generate_admission_decision', 'extract_insights')
    graph.add_edge('extract_insights',            END)
    return graph


# ─── Government Graph ─────────────────────────────────────────────────────────

def build_government_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_tender', 'check_procurement_policy', 'evaluate_policies',
        'human_decision', 'approval_gate', 'generate_tender_report', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_tender')
    graph.add_edge('validate_tender',          'check_procurement_policy')
    graph.add_edge('check_procurement_policy', 'evaluate_policies')
    graph.add_edge('evaluate_policies',        'human_decision')
    graph.add_edge('human_decision',           'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_tender_report' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_tender_report': 'generate_tender_report', END: END})
    graph.add_edge('generate_tender_report', 'extract_insights')
    graph.add_edge('extract_insights',       END)
    return graph


# ─── Energy Graph ─────────────────────────────────────────────────────────────

def build_energy_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_esg_report', 'check_emission_limits', 'evaluate_policies',
        'human_decision', 'approval_gate', 'generate_esg_certificate', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_esg_report')
    graph.add_edge('validate_esg_report',  'check_emission_limits')
    graph.add_edge('check_emission_limits', 'evaluate_policies')
    graph.add_edge('evaluate_policies',    'human_decision')
    graph.add_edge('human_decision',       'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_esg_certificate' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_esg_certificate': 'generate_esg_certificate', END: END})
    graph.add_edge('generate_esg_certificate', 'extract_insights')
    graph.add_edge('extract_insights',         END)
    return graph


# ─── Telecom Graph ────────────────────────────────────────────────────────────

def build_telecom_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_license_application', 'check_spectrum_availability',
        'evaluate_policies', 'human_decision', 'approval_gate',
        'generate_license_decision', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_license_application')
    graph.add_edge('validate_license_application', 'check_spectrum_availability')
    graph.add_edge('check_spectrum_availability',  'evaluate_policies')
    graph.add_edge('evaluate_policies',            'human_decision')
    graph.add_edge('human_decision',               'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_license_decision' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_license_decision': 'generate_license_decision', END: END})
    graph.add_edge('generate_license_decision', 'extract_insights')
    graph.add_edge('extract_insights',          END)
    return graph


# ─── Manufacturing Graph ──────────────────────────────────────────────────────

def build_manufacturing_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_quality_inspection', 'check_defect_rate', 'evaluate_policies',
        'human_decision', 'approval_gate', 'generate_quality_certificate', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_quality_inspection')
    graph.add_edge('validate_quality_inspection', 'check_defect_rate')
    graph.add_edge('check_defect_rate',           'evaluate_policies')
    graph.add_edge('evaluate_policies',           'human_decision')
    graph.add_edge('human_decision',              'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_quality_certificate' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_quality_certificate': 'generate_quality_certificate', END: END})
    graph.add_edge('generate_quality_certificate', 'extract_insights')
    graph.add_edge('extract_insights',             END)
    return graph


# ─── Logistics Graph ──────────────────────────────────────────────────────────

def build_logistics_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_shipment', 'check_customs_compliance', 'evaluate_policies',
        'human_decision', 'approval_gate', 'generate_shipping_clearance', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_shipment')
    graph.add_edge('validate_shipment',        'check_customs_compliance')
    graph.add_edge('check_customs_compliance', 'evaluate_policies')
    graph.add_edge('evaluate_policies',        'human_decision')
    graph.add_edge('human_decision',           'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_shipping_clearance' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_shipping_clearance': 'generate_shipping_clearance', END: END})
    graph.add_edge('generate_shipping_clearance', 'extract_insights')
    graph.add_edge('extract_insights',            END)
    return graph


# ─── Retail Graph ─────────────────────────────────────────────────────────────

def build_retail_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_vendor_onboarding', 'check_return_policy_compliance',
        'evaluate_policies', 'human_decision', 'approval_gate',
        'generate_vendor_approval', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_vendor_onboarding')
    graph.add_edge('validate_vendor_onboarding',      'check_return_policy_compliance')
    graph.add_edge('check_return_policy_compliance',  'evaluate_policies')
    graph.add_edge('evaluate_policies',               'human_decision')
    graph.add_edge('human_decision',                  'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_vendor_approval' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_vendor_approval': 'generate_vendor_approval', END: END})
    graph.add_edge('generate_vendor_approval', 'extract_insights')
    graph.add_edge('extract_insights',         END)
    return graph


# ─── Cybersecurity Graph ──────────────────────────────────────────────────────

def build_cybersecurity_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_security_incident', 'assess_threat_level',
        'check_regulatory_notification', 'evaluate_policies', 'human_decision',
        'approval_gate', 'generate_incident_report', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_security_incident')
    graph.add_edge('validate_security_incident',  'assess_threat_level')
    graph.add_edge('assess_threat_level',         'check_regulatory_notification')
    graph.add_edge('check_regulatory_notification', 'evaluate_policies')
    graph.add_edge('evaluate_policies',           'human_decision')
    graph.add_edge('human_decision',              'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        return 'generate_incident_report' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_incident_report': 'generate_incident_report', END: END})
    graph.add_edge('generate_incident_report', 'extract_insights')
    graph.add_edge('extract_insights',         END)
    return graph


# ─── Graph Registry ───────────────────────────────────────────────────────────

GRAPH_REGISTRY = {
    'finance':       build_finance_graph,
    'it':            build_it_graph,
    'hr':            build_hr_graph,
    'legal':         build_legal_graph,
    'healthcare':    build_healthcare_graph,
    'insurance':     build_insurance_graph,
    'education':     build_education_graph,
    'government':    build_government_graph,
    'energy':        build_energy_graph,
    'telecom':       build_telecom_graph,
    'manufacturing': build_manufacturing_graph,
    'logistics':     build_logistics_graph,
    'retail':        build_retail_graph,
    'cybersecurity': build_cybersecurity_graph,
}


# ─── Main Executor ────────────────────────────────────────────────────────────

def execute_graph(workflow_run: WorkflowRun) -> dict:
    from sectors.registry import get_hitl_pause_node

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
        interrupt_before=['human_decision'],
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

    final_state = compiled.invoke(initial_state, config=config)

    hitl_pause_node = get_hitl_pause_node(sector)
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
    from sectors.registry import get_post_hitl_nodes

    sector = workflow_run.tenant.sector
    run_id = str(workflow_run.id)

    logger.info(f'resume_graph — run_id={run_id} action={action}')

    service = WorkflowExecutionService(workflow_run)

    human_action = {
        'action':        action,
        'actor':         actor,
        'reason_code':   reason_code,
        'justification': justification,
    }

    post_nodes = get_post_hitl_nodes(sector)

    if action != 'APPROVED':
        logger.info(f'resume_graph — action={action}, skipping post-HITL nodes')
        service.complete(workflow_run.output_data or {})
        return {'status': 'rejected_or_escalated', 'action': action}

    # Execute human_decision node to record the decision
    try:
        service.execute_node('human_decision', {
            **workflow_run.input_data,
            **(workflow_run.output_data or {}),
            'human_action': human_action,
            **human_action,
        })
    except Exception as e:
        logger.error(f'human_decision node failed: {e}')

    # Execute approval_gate
    try:
        service.execute_node('approval_gate', human_action)
    except Exception as e:
        logger.error(f'approval_gate node failed: {e}')

    # Execute remaining post-HITL nodes
    accumulated = {
        **workflow_run.input_data,
        **(workflow_run.output_data or {}),
        'human_action': human_action,
    }

    output = {}
    for node_code in post_nodes:
        try:
            result = service.execute_node(node_code, accumulated)
            accumulated[node_code] = result
            output[node_code]      = result
            logger.info(f'resume_graph — executed {node_code}')
        except Exception as e:
            logger.error(f'resume_graph — {node_code} failed: {e}')

    final_output = {**(workflow_run.output_data or {}), **output}
    service.complete(final_output)
    return final_output