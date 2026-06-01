# engine/events.py
#
# SSE event publisher — called from graph.py at every key lifecycle point.
# Uses Redis DB 2 for pub/sub (DB 0 = Celery, DB 1 = LangGraph state).
# Publishing never raises — a Redis blip must never crash a workflow.

import json
import logging
import os

import redis

logger = logging.getLogger('nexara.engine.events')

_redis_client = None


def _get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        base = os.getenv('REDIS_URL', 'redis://localhost:6379')
        # Normalise: strip any existing DB path, force DB 2
        if base.count('/') >= 3:
            base = base.rsplit('/', 1)[0]
        _redis_client = redis.Redis.from_url(f'{base}/2', decode_responses=True)
    return _redis_client


def publish_event(run_id: str, event_type: str, payload: dict) -> None:
    """
    Publish a workflow lifecycle event to Redis pub/sub.

    Channel key:  nexara:run:<run_id>
    Consumers:    workflow_run_stream() SSE view in engine/views.py

    Event types emitted from graph.py:
        node_complete       — a node finished successfully
        node_failed         — a node raised an exception
        hitl_pause          — workflow paused, awaiting human decision
        hitl_resume         — human decision received, post-HITL nodes starting
        workflow_complete   — all nodes done, run marked COMPLETED
        workflow_failed     — run marked FAILED
    """
    channel = f'nexara:run:{run_id}'
    message = json.dumps({'type': event_type, 'run_id': run_id, **payload})
    try:
        _get_redis().publish(channel, message)
        logger.debug(f'SSE published — type={event_type} run_id={run_id}')
    except Exception as exc:
        # Non-fatal: SSE is observability, not control flow
        logger.warning(f'SSE publish failed (non-fatal) — {exc}')