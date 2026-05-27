 # engine/nodes/__init__.py

import logging

logger = logging.getLogger('nexara.engine.nodes')

# ─── Node Registry ────────────────────────────────────────────────────────────
# Global dict: { node_code: { 'class': NodeClass, 'sectors': [...] } }

NODE_REGISTRY = {}


def register_node(code, sectors=None, is_async=False, retry_policy='none'):
    """
    Decorator that registers a node class into the global NODE_REGISTRY.

    Usage:
        @register_node(code='fetch_prices', sectors=['finance'], retry_policy='transient')
        class FetchPricesNode(BaseNode):
            ...

    retry_policy options:
        'none'      — deterministic, no retry (compute nodes, policy nodes)
        'transient' — safe to retry, max 3 (I/O nodes, external API calls)
        'bounded'   — 1-2 retries, must be idempotent (mutation/persist nodes)
        'timeout'   — HITL nodes, escalation on timeout
    """
    def decorator(cls):
        if code in NODE_REGISTRY:
            logger.warning(f'Node {code} is already registered — overwriting.')

        NODE_REGISTRY[code] = {
            'class':        cls,
            'sectors':      sectors or [],      # empty = available to all sectors
            'is_async':     is_async,
            'retry_policy': retry_policy,
        }
        cls.node_code    = code
        cls.node_sectors = sectors or []
        logger.debug(f'Registered node: {code} (sectors={sectors}, async={is_async})')
        return cls

    return decorator


def get_node(code):
    """
    Returns the node entry for a given code.
    Raises KeyError if not found.
    """
    if code not in NODE_REGISTRY:
        raise KeyError(f'Node "{code}" is not registered. Run sync_nodes.')
    return NODE_REGISTRY[code]


def get_nodes_for_sector(sector):
    """
    Returns all nodes available to a given sector.
    Nodes with sectors=[] are available to everyone.
    """
    return {
        code: entry
        for code, entry in NODE_REGISTRY.items()
        if not entry['sectors'] or sector in entry['sectors']
    }


def list_nodes():
    """Returns a summary of all registered nodes — useful for debugging."""
    return [
        {
            'code':         code,
            'sectors':      entry['sectors'],
            'is_async':     entry['is_async'],
            'retry_policy': entry['retry_policy'],
            'class':        entry['class'].__name__,
        }
        for code, entry in NODE_REGISTRY.items()
    ]
