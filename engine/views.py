# engine/views.py

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from engine.models import WorkflowRun, AgentRun, HumanAction, NodeRun
from engine.services import AgentTriggerService
from core.middleware import get_current_tenant

logger = logging.getLogger('nexara.engine.views')


# ─── Agent Trigger ────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_agent(request, agent_code):
    """
    POST /api/engine/agents/<agent_code>/trigger/
    Body: { ...input_data }
    Triggers a workflow run for the given agent.
    """
    tenant = get_current_tenant()
    if not tenant:
        return Response(
            {'error': 'No tenant context. Send X-Tenant-Slug header.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        agent_run = AgentTriggerService.trigger(
            agent_code   = agent_code,
            input_data   = request.data,
            tenant       = tenant,
            triggered_by = request.user.username,
        )
        return Response({
            'agent_run_id':   str(agent_run.id),
            'workflow_run_id': str(agent_run.workflow_run.id),
            'status':          agent_run.status,
            'message':         f'Agent {agent_code} triggered successfully.',
        }, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f'trigger_agent failed: {e}')
        return Response({'error': 'Internal server error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Workflow Run Status ───────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workflow_run_status(request, run_id):
    """
    GET /api/engine/runs/<run_id>/
    Returns the current status and node run history for a workflow run.
    """
    try:
        run = WorkflowRun.objects.select_related(
            'template', 'agent', 'tenant'
        ).get(id=run_id)
    except WorkflowRun.DoesNotExist:
        return Response({'error': 'Workflow run not found.'}, status=status.HTTP_404_NOT_FOUND)

    node_runs = NodeRun.objects.filter(
        workflow_run=run
    ).order_by('created_at').values(
        'id', 'node_code', 'status',
        'duration_ms', 'retry_count', 'error', 'created_at'
    )

    return Response({
        'run_id':           str(run.id),
        'agent':            run.agent.code if run.agent else None,
        'template':         run.template.code,
        'template_version': run.template_version,
        'status':           run.status,
        'sector':           run.tenant.sector,
        'input_data':       run.input_data,
        'output_data':      run.output_data,
        'error_message':    run.error_message,
        'started_at':       run.started_at,
        'completed_at':     run.completed_at,
        'created_at':       run.created_at,
        'node_runs':        list(node_runs),
    })


# ─── List Workflow Runs ───────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_workflow_runs(request):
    """
    GET /api/engine/runs/
    Lists all workflow runs for the current tenant.
    Supports ?status=running|completed|failed|waiting_for_input filter.
    """
    tenant = get_current_tenant()
    if not tenant:
        return Response(
            {'error': 'No tenant context.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    qs = WorkflowRun.objects.select_related(
        'template', 'agent'
    ).order_by('-created_at')

    # Optional status filter
    status_filter = request.query_params.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)

    runs = qs.values(
        'id', 'status', 'template__code',
        'template_version', 'created_at',
        'started_at', 'completed_at'
    )[:50]

    return Response({
        'tenant': tenant.name,
        'count':  qs.count(),
        'runs':   list(runs),
    })


# ─── HITL Submit ──────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_human_decision(request, run_id):
    """
    POST /api/engine/runs/<run_id>/hitl/submit/
    Body: {
        "action": "APPROVED" | "REJECTED" | "ESCALATED",
        "reason_code": "RISK_ACCEPTED",
        "justification": "Reviewed and approved."
    }
    Submits a human decision and resumes the paused workflow.
    
    Example:
    curl -X POST http://localhost:8000/api/engine/runs/2776d1f0-3668-4d89-9a04-7283bffd3ed3/hitl/submit/ \
      -H "Authorization: Token YOUR_AUTH_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "action": "APPROVED",
        "reason_code": "RISK_ACCEPTED",
        "justification": "Reviewed and approved."
      }'
    """
    try:
        run = WorkflowRun.objects.select_related(
            'tenant', 'template'
        ).get(id=run_id)
    except WorkflowRun.DoesNotExist:
        return Response({'error': 'Workflow run not found.'}, status=status.HTTP_404_NOT_FOUND)

    if run.status != WorkflowRun.Status.WAITING:
        return Response(
            {'error': f'Run is not waiting for input. Current status: {run.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    action        = request.data.get('action')
    reason_code   = request.data.get('reason_code', '')
    justification = request.data.get('justification', '')

    if action not in ('APPROVED', 'REJECTED', 'ESCALATED'):
        return Response(
            {'error': 'action must be APPROVED, REJECTED, or ESCALATED'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Write immutable HumanAction record
    HumanAction.objects.create(
        workflow_run  = run,
        node_code     = 'human_decision',
        actor         = request.user.email or request.user.username,
        action        = action,
        reason_code   = reason_code,
        justification = justification,
    )

    # Resume the graph via Celery task
    from engine.tasks import resume_workflow_task
    resume_workflow_task.delay(
        workflow_run_id = str(run.id),
        action          = action,
        actor           = request.user.username,
        reason_code     = reason_code,
        justification   = justification,
    )

    logger.info(f'HITL submitted — run_id={run_id} action={action} by={request.user.username}')

    return Response({
        'run_id':  str(run.id),
        'action':  action,
        'status':  'resuming',
        'message': f'Decision recorded. Workflow resuming.',
    })


# ─── Node Execute (Internal — called by LangGraph) ────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def internal_node_execute(request, node_code):
    """
    POST /api/internal/nodes/<node_code>/execute/
    Internal endpoint called by LangGraph runtime to execute a node.
    Protected by INTERNAL_API_SECRET header.
    """
    from django.conf import settings

    secret = request.headers.get('X-Internal-Secret')
    if secret != settings.NEXARA.get('INTERNAL_API_SECRET'):
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    run_id     = request.data.get('run_id')
    input_data = request.data.get('input_data', {})

    try:
        run = WorkflowRun.all_objects.select_related('tenant').get(id=run_id)
        from core.middleware import set_current_tenant
        set_current_tenant(run.tenant)

        service = WorkflowExecutionService(run)
        output  = service.execute_node(node_code, input_data)
        return Response({'success': True, 'output': output})

    except Exception as e:
        logger.error(f'internal_node_execute failed: {e}')
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)