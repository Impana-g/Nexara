# engine/tasks.py

import logging
from celery import shared_task

logger = logging.getLogger('nexara.engine.tasks')


@shared_task(bind=True, max_retries=3)
def execute_workflow_task(self, workflow_run_id: str):
    """
    Celery task that executes a WorkflowRun.
    Picks up the run from DB, sets tenant context, runs the graph.
    """
    from engine.models import WorkflowRun, AgentRun
    from engine.services import WorkflowExecutionService
    from core.middleware import set_current_tenant
    from django.utils import timezone

    logger.info(f'execute_workflow_task started — run_id={workflow_run_id}')

    try:
        run = WorkflowRun.all_objects.select_related(
            'tenant', 'template', 'agent'
        ).get(id=workflow_run_id)

        set_current_tenant(run.tenant)

        run.status     = WorkflowRun.Status.RUNNING
        run.started_at = timezone.now()
        run.save()

        AgentRun.all_objects.filter(workflow_run=run).update(
            status     = AgentRun.Status.RUNNING,
            started_at = timezone.now(),
        )

        from engine.graph import execute_graph
        output = execute_graph(run)

        AgentRun.all_objects.filter(workflow_run=run).update(
            status         = AgentRun.Status.COMPLETED,
            completed_at   = timezone.now(),
            output_summary = output,
        )

        logger.info(f'execute_workflow_task completed — run_id={workflow_run_id}')
        return {'status': 'completed', 'run_id': workflow_run_id}

    except Exception as exc:
        logger.error(f'execute_workflow_task failed — run_id={workflow_run_id} — {exc}')
        try:
            WorkflowRun.all_objects.filter(id=workflow_run_id).update(
                status        = WorkflowRun.Status.FAILED,
                error_message = str(exc),
            )
            AgentRun.all_objects.filter(
                workflow_run_id=workflow_run_id
            ).update(status=AgentRun.Status.FAILED)
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def resume_workflow_task(self, workflow_run_id: str, action: str,
                         actor: str, reason_code: str, justification: str):
    """
    Resumes a paused WorkflowRun after a human decision is submitted.
    """
    from engine.models import WorkflowRun
    from engine.graph import resume_graph
    from core.middleware import set_current_tenant

    logger.info(f'resume_workflow_task started — run_id={workflow_run_id}')

    try:
        run = WorkflowRun.all_objects.select_related(
            'tenant', 'template'
        ).get(id=workflow_run_id)

        set_current_tenant(run.tenant)

        resume_graph(run, action, actor, reason_code, justification)

        logger.info(f'resume_workflow_task completed — run_id={workflow_run_id}')

    except Exception as exc:
        logger.error(f'resume_workflow_task failed — {exc}')
        raise self.retry(exc=exc, countdown=60)