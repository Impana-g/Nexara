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


# ─── Graph Builder ────────────────────────────────────────────────────────────

def build_finance_graph(service: WorkflowExecutionService) -> StateGraph:
    """
    Builds the finance portfolio review workflow graph.

    Flow:
        portfolio_import
            → compute_metrics
            → concentration_check
            → suitability_check
            → evaluate_policies
            → human_decision        ← HITL pause here
            → approval_gate
            → generate_report
            → END
    """
    graph = StateGraph(WorkflowState)

    # Register all nodes
    node_sequence = [
        'portfolio_import',
        'compute_metrics',
        'concentration_check',
        'suitability_check',
        'evaluate_policies',
        'human_decision',
        'approval_gate',
        'generate_report',
    ]

    for code in node_sequence:
        graph.add_node(code, make_graph_node(code, service))

    # Linear edges
    graph.set_entry_point('portfolio_import')
    graph.add_edge('portfolio_import',   'compute_metrics')
    graph.add_edge('compute_metrics',    'concentration_check')
    graph.add_edge('concentration_check','suitability_check')
    graph.add_edge('suitability_check',  'evaluate_policies')
    graph.add_edge('evaluate_policies',  'human_decision')

    # Conditional edge after approval_gate
    graph.add_edge('human_decision',     'approval_gate')

    def route_after_approval(state: WorkflowState) -> str:
        outputs      = state.get('node_outputs', {})
        gate_output  = outputs.get('approval_gate', {})
        route        = gate_output.get('route', 'APPROVED')

        if route == 'APPROVED':
            return 'generate_report'
        else:
            # REJECTED or ESCALATED — end without report
            return END

    graph.add_conditional_edges(
        'approval_gate',
        route_after_approval,
        {
            'generate_report': 'generate_report',
            END: END,
        }
    )

    graph.add_edge('generate_report', END)

    return graph


# ─── Graph Registry ───────────────────────────────────────────────────────────

# Maps sector → graph builder function
GRAPH_REGISTRY = {
    'finance': build_finance_graph,
}


# ─── Main Executor ────────────────────────────────────────────────────────────

def execute_graph(workflow_run: WorkflowRun) -> dict:
    """
    Main entry point called by execute_workflow_task (Celery).
    Builds the correct graph for the sector, runs it, returns output.
    """
    sector  = workflow_run.tenant.sector
    run_id  = str(workflow_run.id)

    logger.info(f'execute_graph — run_id={run_id} sector={sector}')

    # Get the graph builder for this sector
    builder_fn = GRAPH_REGISTRY.get(sector)
    if not builder_fn:
        raise ValueError(f'No graph registered for sector: {sector}')

    # Build execution service
    service = WorkflowExecutionService(workflow_run)

    # Build and compile graph with in-memory checkpointer
    graph        = builder_fn(service)
    checkpointer = MemorySaver()
    compiled     = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=['human_decision'],   # HITL pause point
    )

    # Initial state
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

    # Run graph — pauses automatically at human_decision
    final_state = compiled.invoke(initial_state, config=config)

    # If paused at HITL, update WorkflowRun status and return
    if final_state.get('status') != 'failed':
        current = final_state.get('current_node', '')
        if current == 'evaluate_policies':
            # Graph paused before human_decision
            workflow_run.status         = WorkflowRun.Status.WAITING
            workflow_run.graph_thread_id = run_id
            workflow_run.save()
            logger.info(f'Graph paused at HITL — run_id={run_id}')
            return {'status': 'waiting_for_input', 'run_id': run_id}

    if final_state.get('status') == 'failed':
        service.fail(final_state.get('error', 'unknown error'))
        return {'status': 'failed'}

    # Completed
    output = final_state.get('node_outputs', {})
    service.complete(output)
    return output