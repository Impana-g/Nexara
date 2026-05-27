# engine/nodes/base.py

import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod

logger = logging.getLogger('nexara.engine.nodes')


class BaseNode(ABC):
    """
    Abstract base class for all Nexara nodes.

    Every node must implement execute(input_data, context) and return a dict.
    The engine wraps every execution with audit record creation automatically.

    Subclass example:
        @register_node(code='my_node', sectors=['finance'])
        class MyNode(BaseNode):
            def execute(self, input_data, context):
                # do work
                return {'result': 'done'}
    """

    node_code    = None     # set by @register_node decorator
    node_sectors = []       # set by @register_node decorator

    def run(self, input_data: dict, context: dict) -> dict:
        """
        Called by the engine. Wraps execute() with timing and error handling.
        Do not override this — override execute() instead.
        """
        start = time.time()
        logger.info(f'[{self.node_code}] starting — input_hash={self._hash(input_data)}')

        try:
            output = self.execute(input_data, context)
            duration_ms = int((time.time() - start) * 1000)
            logger.info(f'[{self.node_code}] completed in {duration_ms}ms')
            return {
                'success':     True,
                'output':      output,
                'duration_ms': duration_ms,
                'input_ref':   self._hash(input_data),
                'output_ref':  self._hash(output),
            }
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            logger.error(f'[{self.node_code}] failed after {duration_ms}ms — {e}')
            return {
                'success':     False,
                'error':       str(e),
                'duration_ms': duration_ms,
                'input_ref':   self._hash(input_data),
                'output_ref':  '',
            }

    @abstractmethod
    def execute(self, input_data: dict, context: dict) -> dict:
        """
        Implement your node logic here.

        Args:
            input_data: dict of inputs for this node
            context:    workflow context (tenant, run_id, sector, etc.)

        Returns:
            dict of outputs — will be stored in MemoryPayload
        """
        pass

    @staticmethod
    def _hash(data: dict) -> str:
        """SHA-256 hash of a dict — used as content address for MemoryPayload."""
        serialised = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialised.encode()).hexdigest()