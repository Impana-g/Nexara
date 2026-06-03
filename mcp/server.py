# mcp/server.py

import json
import logging
import time
from functools import wraps

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.models import Tenant
from engine.models import WorkflowRun
from engine.services import WorkflowExecutionService
from engine.nodes import get_node, NODE_REGISTRY

logger = logging.getLogger('nexara.mcp')


# ── Tenant scope enforcement ──────────────────────────────────────────────────

def resolve_tenant(request) -> Tenant:
    """
    Extracts tenant from request headers.
    MCP clients must pass X-Tenant-ID on every call.
    """
    tenant_id = request.headers.get('X-Tenant-ID', '')
    if not tenant_id:
        raise PermissionError('X-Tenant-ID header is required.')
    try:
        return Tenant.objects.get(id=tenant_id, is_active=True)
    except Tenant.DoesNotExist:
        raise PermissionError(f'Tenant {tenant_id} not found or inactive.')


def mcp_endpoint(fn):
    """
    Decorator for all MCP tool endpoints.
    Handles: JSON parsing, tenant resolution, error formatting,
    and ToolCall audit logging.
    """
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        # Parse body
        try:
            body = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

        # Resolve tenant
        try:
            tenant = resolve_tenant(request)
        except PermissionError as e:
            return JsonResponse({'error': str(e)}, status=403)

        # Execute tool
        start = time.time()
        try:
            result = fn(request, body, tenant, *args, **kwargs)
            duration_ms = int((time.time() - start) * 1000)

            # Log ToolCall if workflow_run_id provided
            _log_tool_call(
                body        = body,
                tenant      = tenant,
                tool_name   = fn.__name__,
                output_data = result,
                status      = 'success',
                duration_ms = duration_ms,
            )
            return JsonResponse(result)

        except PermissionError as e:
            return JsonResponse({'error': str(e)}, status=403)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            logger.error(f'[mcp] {fn.__name__} failed: {e}')
            _log_tool_call(
                body        = body,
                tenant      = tenant,
                tool_name   = fn.__name__,
                output_data = {},
                status      = 'error',
                error       = str(e),
                duration_ms = duration_ms,
            )
            return JsonResponse({'error': str(e)}, status=500)

    return wrapper


def _log_tool_call(body, tenant, tool_name, output_data,
                   status, error='', duration_ms=None):
    """Write a ToolCall audit record if a workflow_run_id is present."""
    run_id = body.get('workflow_run_id')
    if not run_id:
        return
    try:
        workflow_run = WorkflowRun.objects.get(id=run_id, tenant=tenant)
        svc = WorkflowExecutionService(workflow_run)
        svc.record_tool_call(
            node_code   = body.get('node_code', ''),
            tool_name   = tool_name,
            input_data  = body,
            output_data = output_data,
            status      = status,
            error       = error,
            duration_ms = duration_ms,
        )
    except Exception as e:
        logger.warning(f'[mcp] ToolCall audit failed: {e}')


# ── Tool 1: execute_node ──────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['POST'])
@mcp_endpoint
def execute_node(request, body, tenant):
    """
    MCP Tool: execute_node
    Runs a single workflow node in the context of a WorkflowRun.

    Body:
        workflow_run_id  : str (UUID)
        node_code        : str
        input_data       : dict
    """
    run_id     = body.get('workflow_run_id', '')
    node_code  = body.get('node_code', '')
    input_data = body.get('input_data', {})

    if not run_id:
        raise ValueError('workflow_run_id is required.')
    if not node_code:
        raise ValueError('node_code is required.')

    # Enforce tenant scope — run must belong to this tenant
    try:
        workflow_run = WorkflowRun.objects.get(id=run_id, tenant=tenant)
    except WorkflowRun.DoesNotExist:
        raise PermissionError(f'WorkflowRun {run_id} not found for this tenant.')

    # Check node exists
    try:
        get_node(node_code)
    except KeyError:
        raise ValueError(f'Node "{node_code}" is not registered.')

    # Execute
    svc    = WorkflowExecutionService(workflow_run)
    output = svc.execute_node(node_code, input_data)

    logger.info(f'[mcp] execute_node: {node_code} run_id={run_id} tenant={tenant.id}')
    return {'success': True, 'node_code': node_code, 'output': output}


# ── Tool 2: submit_human_decision ─────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['POST'])
@mcp_endpoint
def submit_human_decision(request, body, tenant):
    """
    MCP Tool: submit_human_decision
    Submits a human APPROVED/REJECTED/ESCALATED decision for a HITL node.

    Body:
        workflow_run_id : str (UUID)
        node_code       : str
        action          : str  (APPROVED | REJECTED | ESCALATED)
        actor           : str  (username or email)
        justification   : str  (optional)
        reason_code     : str  (optional)
    """
    from engine.models import HumanAction

    run_id        = body.get('workflow_run_id', '')
    node_code     = body.get('node_code', '')
    action        = body.get('action', '').upper()
    actor         = body.get('actor', '')
    justification = body.get('justification', '')
    reason_code   = body.get('reason_code', '')

    if not run_id:
        raise ValueError('workflow_run_id is required.')
    if not node_code:
        raise ValueError('node_code is required.')
    if action not in ('APPROVED', 'REJECTED', 'ESCALATED'):
        raise ValueError('action must be APPROVED, REJECTED, or ESCALATED.')
    if not actor:
        raise ValueError('actor is required.')

    # Enforce tenant scope
    try:
        workflow_run = WorkflowRun.objects.get(id=run_id, tenant=tenant)
    except WorkflowRun.DoesNotExist:
        raise PermissionError(f'WorkflowRun {run_id} not found for this tenant.')

    # Must be in WAITING state
    if workflow_run.status != WorkflowRun.Status.WAITING:
        raise ValueError(
            f'WorkflowRun is in "{workflow_run.status}" state, not waiting_for_input.'
        )

    # Write immutable HumanAction record
    human_action = HumanAction.objects.create(
        workflow_run  = workflow_run,
        node_code     = node_code,
        actor         = actor,
        action        = action,
        justification = justification,
        reason_code   = reason_code,
    )

    # Resume the workflow graph
    from engine.graph import resume_graph
    resume_graph(workflow_run, human_action)

    logger.info(
        f'[mcp] submit_human_decision: {action} by {actor} '
        f'on {node_code} run_id={run_id}'
    )
    return {
        'success'       : True,
        'action'        : action,
        'actor'         : actor,
        'node_code'     : node_code,
        'workflow_run_id': run_id,
    }


# ── Tool 3: get_workflow_status ───────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['GET'])
@mcp_endpoint
def get_workflow_status(request, body, tenant):
    """
    MCP Tool: get_workflow_status
    Returns the current status and output of a WorkflowRun.

    Query params OR body:
        workflow_run_id : str (UUID)
    """
    run_id = (
        request.GET.get('workflow_run_id') or
        body.get('workflow_run_id', '')
    )

    if not run_id:
        raise ValueError('workflow_run_id is required.')

    # Enforce tenant scope
    try:
        workflow_run = WorkflowRun.objects.get(id=run_id, tenant=tenant)
    except WorkflowRun.DoesNotExist:
        raise PermissionError(f'WorkflowRun {run_id} not found for this tenant.')

    # Gather node run summary
    node_runs = workflow_run.node_runs.values(
        'node_code', 'status', 'duration_ms', 'retry_count', 'error', 'created_at'
    ).order_by('created_at')

    # Gather human actions
    human_actions = workflow_run.human_actions.values(
        'node_code', 'actor', 'action', 'justification', 'timestamp'
    ).order_by('timestamp')

    return {
        'workflow_run_id' : str(workflow_run.id),
        'status'          : workflow_run.status,
        'template'        : workflow_run.template.code,
        'template_version': workflow_run.template_version,
        'sector'          : tenant.sector,
        'started_at'      : str(workflow_run.started_at or ''),
        'completed_at'    : str(workflow_run.completed_at or ''),
        'error_message'   : workflow_run.error_message,
        'output_data'     : workflow_run.output_data,
        'node_runs'       : list(node_runs),
        'human_actions'   : list(human_actions),
    }


# ── Tool 4: list_nodes ────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['GET'])
@mcp_endpoint
def list_nodes(request, body, tenant):
    """
    MCP Tool: list_nodes
    Lists all registered nodes, optionally filtered by sector.

    Query params:
        sector : str (optional)
    """
    sector = request.GET.get('sector', '')

    nodes = []
    for code, entry in NODE_REGISTRY.items():
        sectors = entry.get('sectors', [])
        if sector and sector not in sectors and sectors:
            continue
        nodes.append({
            'code'         : code,
            'sectors'      : sectors,
            'retry_policy' : entry.get('retry_policy', 'none'),
            'async'        : entry.get('async', False),
        })

    return {'nodes': nodes, 'count': len(nodes)}