# engine/services.py

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone

from django.utils import timezone as dj_timezone

from engine.models import (
    Agent, WorkflowTemplate, WorkflowRun,
    AgentRun, NodeRun, MemoryPayload, DecisionPoint,
    PolicyEvaluation, ToolCall
)
from engine.nodes import get_node

logger = logging.getLogger('nexara.engine.services')


# ── Memory Store ──────────────────────────────────────────────────────────────

def store_payload(data: dict, pii_class: str = 'none') -> str:
    """
    Content-addressed storage for node inputs/outputs.
    Returns the content hash. Deduplicates automatically.
    """
    serialised   = json.dumps(data, sort_keys=True, default=str)
    content_hash = hashlib.sha256(serialised.encode()).hexdigest()

    MemoryPayload.objects.get_or_create(
        content_hash=content_hash,
        defaults={
            'content':   data,
            'pii_class': pii_class,
        }
    )
    return content_hash


# ── Workflow Execution ────────────────────────────────────────────────────────

class WorkflowExecutionService:
    """
    Executes a workflow graph node-by-node.
    Each node execution is fully audited — NodeRun written for every step.
    PolicyEvaluation written for every node that returns a status field.
    """

    def __init__(self, workflow_run: WorkflowRun):
        self.workflow_run = workflow_run
        self.tenant       = workflow_run.tenant
        self.context      = {
            'run_id':    str(workflow_run.id),
            'sector':    self.tenant.sector,
            'tenant_id': str(self.tenant.id),
        }

    def execute_node(self, node_code: str, input_data: dict) -> dict:
        """
        Executes a single node, writes a NodeRun audit record,
        stores input/output in MemoryPayload, and writes a
        PolicyEvaluation record if the node returns a status field.
        Returns the node's output dict.
        """
        node_entry = get_node(node_code)
        node_cls   = node_entry['class']
        node       = node_cls()

        # Store input
        input_ref = store_payload(input_data)

        # Run the node
        result = node.run(input_data, self.context)

        # Store output
        output_ref = store_payload(result.get('output', {})) if result['success'] else ''

        # Write NodeRun audit record
        NodeRun.objects.create(
            workflow_run = self.workflow_run,
            node_code    = node_code,
            status       = 'completed' if result['success'] else 'failed',
            input_ref    = input_ref,
            output_ref   = output_ref,
            duration_ms  = result.get('duration_ms'),
            error        = result.get('error', ''),
        )

        # ── Audit hook: PolicyEvaluation ──────────────────────────────────────
        # Write a policy evaluation record for every node that returns a status.
        # This gives a full compliance trail across every sector node.
        if result['success']:
            output = result.get('output', {})
            node_status = output.get('status', '')
            if node_status:
                try:
                    # Map node status to PolicyEvaluation result
                    if node_status in ('PASS', 'generated', 'completed'):
                        pe_result = PolicyEvaluation.Result.PASS
                    elif node_status in ('FAIL',):
                        pe_result = PolicyEvaluation.Result.FAIL
                    elif node_status in ('REQUIRES_APPROVAL', 'NOT_ELIGIBLE'):
                        pe_result = PolicyEvaluation.Result.WARN
                    else:
                        pe_result = PolicyEvaluation.Result.SKIPPED

                    PolicyEvaluation.objects.create(
                        workflow_run = self.workflow_run,
                        node_code    = node_code,
                        policy_code  = node_code,
                        policy_name  = node_code.replace('_', ' ').title(),
                        result       = pe_result,
                        details      = {
                            'node_status':    node_status,
                            'missing_fields': output.get('missing_fields', []),
                            'llm_powered':    output.get('llm_powered', False),
                        },
                    )
                    logger.debug(f'[audit] PolicyEvaluation written: {node_code} → {pe_result}')
                except Exception as e:
                    logger.error(f'[audit] PolicyEvaluation write failed for {node_code}: {e}')
        # ─────────────────────────────────────────────────────────────────────

        if not result['success']:
            logger.error(f'Node {node_code} failed: {result.get("error")}')
            raise RuntimeError(f'Node {node_code} failed: {result.get("error")}')

        return result.get('output', {})

    def record_decision(self, node_code: str, options: list,
                        selected: dict, basis: str = '', signals: dict = None):
        """Records a DecisionPoint for an automated choice."""
        DecisionPoint.objects.create(
            workflow_run    = self.workflow_run,
            node_code       = node_code,
            options         = options,
            selected        = selected,
            decision_basis  = basis,
            quality_signals = signals or {},
        )

    def record_tool_call(self, node_code: str, tool_name: str,
                         input_data: dict, output_data: dict,
                         status: str = 'success', error: str = '',
                         duration_ms: int = None):
        """
        Records an MCP tool invocation against this workflow run.
        Called by the MCP server after every tool execution.
        """
        try:
            ToolCall.objects.create(
                workflow_run = self.workflow_run,
                node_code    = node_code,
                tool_name    = tool_name,
                tenant       = self.tenant,
                input_data   = input_data,
                output_data  = output_data,
                status       = status,
                error        = error,
                duration_ms  = duration_ms,
            )
            logger.debug(f'[audit] ToolCall written: {tool_name} [{status}]')
        except Exception as e:
            logger.error(f'[audit] ToolCall write failed for {tool_name}: {e}')

    def complete(self, output_data: dict):
        """Marks the WorkflowRun as completed."""
        self.workflow_run.status       = WorkflowRun.Status.COMPLETED
        self.workflow_run.output_data  = output_data
        self.workflow_run.completed_at = dj_timezone.now()
        self.workflow_run.save()
        logger.info(f'WorkflowRun {self.workflow_run.id} completed')

    def fail(self, error_message: str):
        """Marks the WorkflowRun as failed."""
        self.workflow_run.status        = WorkflowRun.Status.FAILED
        self.workflow_run.error_message = error_message
        self.workflow_run.completed_at  = dj_timezone.now()
        self.workflow_run.save()
        logger.error(f'WorkflowRun {self.workflow_run.id} failed: {error_message}')


# ── Agent Trigger Service ─────────────────────────────────────────────────────

class AgentTriggerService:
    """
    Creates and kicks off a WorkflowRun for a given agent.
    Called by AgentTriggerView (API) and Celery Beat (scheduled).
    """

    @staticmethod
    def trigger(agent_code: str, input_data: dict,
                tenant, triggered_by: str = 'api') -> AgentRun:
        """
        Creates WorkflowRun + AgentRun records and queues the Celery task.
        Returns the AgentRun record.
        """
        # Resolve agent
        try:
            agent = Agent.objects.get(code=agent_code, is_active=True)
        except Agent.DoesNotExist:
            raise ValueError(f'Agent "{agent_code}" not found or inactive.')

        # Resolve active template
        template = agent.workflow_template
        if not template.is_active:
            raise ValueError(f'Workflow template "{template.code}" is not active.')

        # Create WorkflowRun — lock template version at creation
        workflow_run = WorkflowRun.objects.create(
            tenant           = tenant,
            agent            = agent,
            template         = template,
            template_version = template.version,
            status           = WorkflowRun.Status.PENDING,
            input_data       = input_data,
        )

        # Compute input hash for audit
        input_hash = hashlib.sha256(
            json.dumps(input_data, sort_keys=True, default=str).encode()
        ).hexdigest()

        # Create AgentRun — primary audit record
        agent_run = AgentRun.objects.create(
            tenant       = tenant,
            agent        = agent,
            workflow_run = workflow_run,
            status       = AgentRun.Status.PENDING,
            triggered_by = triggered_by,
            input_hash   = input_hash,
        )

        # Queue Celery task
        from engine.tasks import execute_workflow_task
        execute_workflow_task.delay(str(workflow_run.id))

        logger.info(
            f'Agent {agent_code} triggered by {triggered_by} — '
            f'run_id={workflow_run.id}'
        )
        return agent_run