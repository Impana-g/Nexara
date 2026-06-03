# engine/graph.py

import logging
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from engine.models import WorkflowRun
from engine.services import WorkflowExecutionService
from engine.events import publish_event

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
            publish_event(state['run_id'], 'node_complete', {
                'node':   node_code,
                'sector': state.get('sector', ''),
            })
            return {
                'node_outputs': {node_code: output},
                'current_node': node_code,
                'status':       'running',
            }
        except Exception as e:
            logger.error(f'Graph node {node_code} failed: {e}')
            publish_event(state['run_id'], 'node_failed', {
                'node':   node_code,
                'sector': state.get('sector', ''),
                'error':  str(e),
            })
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
        'validate_job_requisition', 'check_headcount_budget',
        'validate_salary_band', 'evaluate_policies',
        'check_pf_esi_compliance', 'human_decision',
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
    graph.add_edge('extract_insights',       END)
    return graph


# ─── Legal Graph ──────────────────────────────────────────────────────────────

def build_legal_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_contract', 'check_jurisdiction', 'evaluate_clauses',
        'evaluate_policies', 'human_decision', 'approval_gate',
        'generate_legal_summary', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_contract')
    graph.add_edge('validate_contract',  'check_jurisdiction')
    graph.add_edge('check_jurisdiction', 'evaluate_clauses')
    graph.add_edge('evaluate_clauses',   'evaluate_policies')
    graph.add_edge('evaluate_policies',  'human_decision')
    graph.add_edge('human_decision',     'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_legal_summary' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_legal_summary': 'generate_legal_summary', END: END})
    graph.add_edge('generate_legal_summary', 'extract_insights')
    graph.add_edge('extract_insights',        END)
    return graph


# ─── Healthcare Graph ─────────────────────────────────────────────────────────

def build_healthcare_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_patient_record', 'check_prescription_limits',
        'insurance_eligibility_check', 'evaluate_policies',
        'human_decision', 'approval_gate',
        'generate_clinical_summary', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_patient_record')
    graph.add_edge('validate_patient_record',    'check_prescription_limits')
    graph.add_edge('check_prescription_limits',  'insurance_eligibility_check')
    graph.add_edge('insurance_eligibility_check','evaluate_policies')
    graph.add_edge('evaluate_policies',          'human_decision')
    graph.add_edge('human_decision',             'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_clinical_summary' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_clinical_summary': 'generate_clinical_summary', END: END})
    graph.add_edge('generate_clinical_summary', 'extract_insights')
    graph.add_edge('extract_insights',           END)
    return graph


# ─── Insurance Graph ──────────────────────────────────────────────────────────

def build_insurance_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_claim', 'check_policy_coverage', 'assess_fraud_risk',
        'evaluate_policies', 'human_decision', 'approval_gate',
        'generate_claim_decision', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_claim')
    graph.add_edge('validate_claim',       'check_policy_coverage')
    graph.add_edge('check_policy_coverage','assess_fraud_risk')
    graph.add_edge('assess_fraud_risk',    'evaluate_policies')
    graph.add_edge('evaluate_policies',    'human_decision')
    graph.add_edge('human_decision',       'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_claim_decision' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_claim_decision': 'generate_claim_decision', END: END})
    graph.add_edge('generate_claim_decision', 'extract_insights')
    graph.add_edge('extract_insights',         END)
    return graph


# ─── Education Graph ──────────────────────────────────────────────────────────

def build_education_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_admission_application', 'check_eligibility_criteria',
        'grant_compliance_check', 'evaluate_policies',
        'human_decision', 'approval_gate',
        'generate_admission_decision', 'extract_insights',
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
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_admission_decision' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_admission_decision': 'generate_admission_decision', END: END})
    graph.add_edge('generate_admission_decision', 'extract_insights')
    graph.add_edge('extract_insights',             END)
    return graph


# ─── Government Graph ─────────────────────────────────────────────────────────

def build_government_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_tender', 'check_procurement_policy', 'evaluate_policies',
        'human_decision', 'approval_gate',
        'generate_tender_report', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_tender')
    graph.add_edge('validate_tender',          'check_procurement_policy')
    graph.add_edge('check_procurement_policy', 'evaluate_policies')
    graph.add_edge('evaluate_policies',        'human_decision')
    graph.add_edge('human_decision',           'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_tender_report' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_tender_report': 'generate_tender_report', END: END})
    graph.add_edge('generate_tender_report', 'extract_insights')
    graph.add_edge('extract_insights',        END)
    return graph


# ─── Energy Graph ─────────────────────────────────────────────────────────────

def build_energy_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_esg_report', 'check_emission_limits', 'evaluate_policies',
        'human_decision', 'approval_gate',
        'generate_esg_certificate', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_esg_report')
    graph.add_edge('validate_esg_report',  'check_emission_limits')
    graph.add_edge('check_emission_limits','evaluate_policies')
    graph.add_edge('evaluate_policies',    'human_decision')
    graph.add_edge('human_decision',       'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_esg_certificate' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_esg_certificate': 'generate_esg_certificate', END: END})
    graph.add_edge('generate_esg_certificate', 'extract_insights')
    graph.add_edge('extract_insights',          END)
    return graph


# ─── Telecom Graph ────────────────────────────────────────────────────────────

def build_telecom_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_service_request', 'check_regulatory_compliance', 'evaluate_policies',
        'human_decision', 'approval_gate',
        'generate_service_approval', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_service_request')
    graph.add_edge('validate_service_request',   'check_regulatory_compliance')
    graph.add_edge('check_regulatory_compliance','evaluate_policies')
    graph.add_edge('evaluate_policies',          'human_decision')
    graph.add_edge('human_decision',             'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_service_approval' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_service_approval': 'generate_service_approval', END: END})
    graph.add_edge('generate_service_approval', 'extract_insights')
    graph.add_edge('extract_insights',           END)
    return graph


# ─── Manufacturing Graph ──────────────────────────────────────────────────────

def build_manufacturing_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_production_order', 'check_quality_standards', 'evaluate_policies',
        'human_decision', 'approval_gate',
        'generate_production_clearance', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_production_order')
    graph.add_edge('validate_production_order', 'check_quality_standards')
    graph.add_edge('check_quality_standards',   'evaluate_policies')
    graph.add_edge('evaluate_policies',         'human_decision')
    graph.add_edge('human_decision',            'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_production_clearance' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_production_clearance': 'generate_production_clearance', END: END})
    graph.add_edge('generate_production_clearance', 'extract_insights')
    graph.add_edge('extract_insights',               END)
    return graph


# ─── Logistics Graph ──────────────────────────────────────────────────────────

def build_logistics_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_shipment', 'check_customs_compliance', 'evaluate_policies',
        'human_decision', 'approval_gate',
        'generate_shipment_clearance', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_shipment')
    graph.add_edge('validate_shipment',       'check_customs_compliance')
    graph.add_edge('check_customs_compliance','evaluate_policies')
    graph.add_edge('evaluate_policies',       'human_decision')
    graph.add_edge('human_decision',          'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_shipment_clearance' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_shipment_clearance': 'generate_shipment_clearance', END: END})
    graph.add_edge('generate_shipment_clearance', 'extract_insights')
    graph.add_edge('extract_insights',             END)
    return graph


# ─── Retail Graph ─────────────────────────────────────────────────────────────

def build_retail_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_promotion', 'check_margin_thresholds', 'evaluate_policies',
        'human_decision', 'approval_gate',
        'generate_promotion_approval', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_promotion')
    graph.add_edge('validate_promotion',    'check_margin_thresholds')
    graph.add_edge('check_margin_thresholds','evaluate_policies')
    graph.add_edge('evaluate_policies',     'human_decision')
    graph.add_edge('human_decision',        'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_promotion_approval' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_promotion_approval': 'generate_promotion_approval', END: END})
    graph.add_edge('generate_promotion_approval', 'extract_insights')
    graph.add_edge('extract_insights',             END)
    return graph


# ─── Cybersecurity Graph ──────────────────────────────────────────────────────

def build_cybersecurity_graph(service: WorkflowExecutionService) -> StateGraph:
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'validate_security_incident', 'assess_threat_level', 'check_containment_policy',
        'evaluate_policies', 'human_decision', 'approval_gate',
        'generate_incident_report', 'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('validate_security_incident')
    graph.add_edge('validate_security_incident', 'assess_threat_level')
    graph.add_edge('assess_threat_level',        'check_containment_policy')
    graph.add_edge('check_containment_policy',   'evaluate_policies')
    graph.add_edge('evaluate_policies',          'human_decision')
    graph.add_edge('human_decision',             'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        gate_output = state.get('node_outputs', {}).get('approval_gate', {})
        return 'generate_incident_report' if gate_output.get('route', 'APPROVED') == 'APPROVED' else END

    graph.add_conditional_edges('approval_gate', route_after_approval,
                                {'generate_incident_report': 'generate_incident_report', END: END})
    graph.add_edge('generate_incident_report', 'extract_insights')
    graph.add_edge('extract_insights',          END)
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
        # Save pre-HITL node outputs so resume_graph can use them as context
        workflow_run.output_data     = final_state.get('node_outputs', {})
        workflow_run.save()
        publish_event(run_id, 'hitl_pause', {
            'sector':  sector,
            'node':    hitl_pause_node,
            'message': 'Workflow paused — awaiting human decision',
        })
        logger.info(f'Graph paused at HITL — run_id={run_id} last_node={current}')
        return {'status': 'waiting_for_input', 'run_id': run_id}

    if final_state.get('status') == 'failed':
        service.fail(final_state.get('error', 'unknown error'))
        publish_event(run_id, 'workflow_failed', {
            'sector': sector,
            'error':  final_state.get('error', 'unknown error'),
        })
        return {'status': 'failed'}

    output = final_state.get('node_outputs', {})
    service.complete(output)
    publish_event(run_id, 'workflow_complete', {'sector': sector})
    return output


# ─── Resume Executor ──────────────────────────────────────────────────────────

def resume_graph(workflow_run: WorkflowRun, action: str, actor: str,
                 reason_code: str, justification: str) -> dict:
    """
    Resumes a paused workflow after a human decision.

    IMPORTANT: MemorySaver is in-process only — it doesn't survive across
    Celery task boundaries. So instead of trying to restore the LangGraph
    checkpoint (which is gone), we manually execute the post-HITL nodes
    using WorkflowExecutionService directly. This is intentional and correct.

    The pre-HITL node outputs are preserved in workflow_run.output_data,
    which execute_graph saves incrementally via service.complete() — wait,
    actually execute_graph only calls service.complete() at the END, and
    at HITL pause it only saves status=WAITING. So output_data is empty dict.

    Fix: we pass input_data as the accumulated context since that's all we have.
    Post-HITL nodes (generate_report, extract_insights) only need the human
    decision + whatever the pre-HITL nodes returned. We store pre-HITL outputs
    on WorkflowRun.output_data at pause time — see the patch in execute_graph above.
    """
    from sectors.registry import get_post_hitl_nodes, get_sector

    sector = workflow_run.tenant.sector
    run_id = str(workflow_run.id)

    logger.info(f'resume_graph — run_id={run_id} sector={sector} action={action}')

    # Guard: validate sector exists before doing anything
    try:
        get_sector(sector)
    except ValueError as e:
        logger.error(f'resume_graph — invalid sector: {e}')
        workflow_run.status        = WorkflowRun.Status.FAILED
        workflow_run.error_message = f'Invalid sector: {sector}'
        workflow_run.save()
        raise

    service = WorkflowExecutionService(workflow_run)

    human_action = {
        'action':        action,
        'actor':         actor,
        'reason_code':   reason_code,
        'justification': justification,
    }

    # ── Non-approval path: close the run immediately ──────────────────────────
    if action != 'APPROVED':
        logger.info(f'resume_graph — action={action}, closing run without post-HITL nodes')
        service.complete(workflow_run.output_data or {})
        publish_event(run_id, 'workflow_complete', {
            'sector': sector,
            'action': action,
        })
        return {'status': 'rejected_or_escalated', 'action': action}

    # ── Approval path ─────────────────────────────────────────────────────────
    publish_event(run_id, 'hitl_resume', {
        'sector': sector,
        'action': action,
        'actor':  actor,
    })

    # Build accumulated context: input_data + whatever was saved at pause
    accumulated = {
        **workflow_run.input_data,
        **(workflow_run.output_data or {}),
        'human_action': human_action,
        **human_action,   # flat keys so nodes can read action/actor directly
    }

    # Record human_decision node (audit only — no business logic)
    try:
        service.execute_node('human_decision', accumulated)
    except Exception as e:
        # human_decision failure is non-fatal — log and continue
        logger.error(f'resume_graph — human_decision node failed: {e}')

    # Record approval_gate node (audit only — route already decided)
    try:
        service.execute_node('approval_gate', human_action)
        accumulated['approval_gate'] = {'route': 'APPROVED', 'reason': reason_code}
    except Exception as e:
        logger.error(f'resume_graph — approval_gate node failed: {e}')

    # Execute all post-HITL nodes
    post_nodes = get_post_hitl_nodes(sector)
    output     = {}

    for node_code in post_nodes:
        try:
            result = service.execute_node(node_code, accumulated)
            accumulated[node_code] = result
            output[node_code]      = result
            publish_event(run_id, 'node_complete', {
                'node':   node_code,
                'sector': sector,
                'phase':  'post_hitl',
            })
            logger.info(f'resume_graph — completed node: {node_code}')
        except Exception as e:
            logger.error(f'resume_graph — node {node_code} failed: {e}')
            publish_event(run_id, 'node_failed', {
                'node':   node_code,
                'sector': sector,
                'phase':  'post_hitl',
                'error':  str(e),
            })
            # Non-fatal: continue with remaining nodes

    final_output = {**(workflow_run.output_data or {}), **output}
    service.complete(final_output)
    publish_event(run_id, 'workflow_complete', {'sector': sector})

    logger.info(f'resume_graph — completed — run_id={run_id}')
    return final_output