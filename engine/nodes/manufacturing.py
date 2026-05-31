# engine/nodes/manufacturing.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(code='validate_quality_inspection', sectors=['manufacturing'], retry_policy='none')
class ValidateQualityInspectionNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        required = ['batch_id', 'product_name', 'inspection_date', 'inspector']
        missing  = [f for f in required if not input_data.get(f)]
        return {'status': 'FAIL' if missing else 'PASS', 'missing_fields': missing,
                'batch_id': input_data.get('batch_id', '')}


@register_node(code='check_defect_rate', sectors=['manufacturing'], retry_policy='none')
class CheckDefectRateNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        defects      = int(input_data.get('defect_count', 0))
        total        = int(input_data.get('total_units', 1))
        threshold    = float(input_data.get('defect_threshold_pct', 2.0))
        defect_rate  = (defects / total * 100) if total else 0
        status       = 'FAIL' if defect_rate > threshold else 'PASS'
        return {'status': status, 'defect_rate_pct': round(defect_rate, 2),
                'threshold_pct': threshold, 'defect_count': defects}


@register_node(code='generate_quality_certificate', sectors=['manufacturing'], retry_policy='bounded')
class GenerateQualityCertificateNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        return {
            'status':       'generated',
            'batch_id':     input_data.get('batch_id', ''),
            'defect_rate':  input_data.get('defect_rate_pct', 0),
            'decision':     input_data.get('human_action', {}).get('action', ''),
            'approved_by':  input_data.get('human_action', {}).get('actor', ''),
        }