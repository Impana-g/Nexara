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

def build_hr_graph(service: WorkflowExecutionService) -> StateGraph:
    """
    HR hiring workflow graph.

    Flow:
        evaluate_policies           ⏸ HITL pause here (last node before human_decision)
            → human_decision
            → approval_gate
            → extract_insights
            → END
    """
    graph = StateGraph(WorkflowState)

    node_sequence = [
        'evaluate_policies',
        'human_decision',
        'approval_gate',
        'extract_insights',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    graph.set_entry_point('evaluate_policies')
    graph.add_edge('evaluate_policies', 'human_decision')
    graph.add_edge('human_decision',    'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs     = state.get('node_outputs', {})
        gate_output = outputs.get('approval_gate', {})
        route       = gate_output.get('route', 'APPROVED')
        if route == 'APPROVED':
            return 'extract_insights'
        return END

    graph.add_conditional_edges(
        'approval_gate',
        route_after_approval,
        {
            'extract_insights': 'extract_insights',
            END: END,
        }
    )

    graph.add_edge('extract_insights', END)

    return graph


# ─── Graph Registry ───────────────────────────────────────────────────────────

# Maps sector → graph builder function
GRAPH_REGISTRY = {
    'finance': build_finance_graph,
    'it':      build_it_graph,
    'hr':      build_hr_graph,
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