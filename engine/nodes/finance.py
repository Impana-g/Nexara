# engine/nodes/finance.py

import logging
from engine.nodes import register_node
from engine.nodes.base import BaseNode

logger = logging.getLogger('nexara.engine.nodes')


@register_node(
    code='portfolio_import',
    sectors=['finance'],
    retry_policy='bounded'      # 1-2 retries, idempotent
)
class PortfolioImportNode(BaseNode):
    """
    Imports portfolio holdings from an uploaded file or external feed.
    Validates structure, assigns ingestion_batch_id, stores raw records.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        portfolio_id = input_data.get('portfolio_id')
        holdings     = input_data.get('holdings', [])

        if not portfolio_id:
            raise ValueError('portfolio_id is required')

        import uuid
        batch_id = str(uuid.uuid4())

        logger.info(f'Importing {len(holdings)} holdings for portfolio {portfolio_id}, batch={batch_id}')

        return {
            'portfolio_id':       portfolio_id,
            'ingestion_batch_id': batch_id,
            'holdings_count':     len(holdings),
            'status':             'imported',
        }


@register_node(
    code='concentration_check',
    sectors=['finance'],
    retry_policy='none'         # deterministic policy check — never retry
)
class ConcentrationCheckNode(BaseNode):
    """
    Checks if any single holding exceeds the concentration limit (default 20%).
    Returns PASS or FAIL with the breaching positions listed.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        holdings = input_data.get('holdings', [])
        limit    = input_data.get('concentration_limit', 0.20)   # 20% default

        total_value = sum(h.get('value', 0) for h in holdings)
        breaches    = []

        if total_value > 0:
            for h in holdings:
                weight = h.get('value', 0) / total_value
                if weight > limit:
                    breaches.append({
                        'instrument': h.get('instrument_uid', 'unknown'),
                        'weight':     round(weight, 4),
                        'limit':      limit,
                    })

        status = 'FAIL' if breaches else 'PASS'
        logger.info(f'Concentration check: {status} — {len(breaches)} breach(es)')

        return {
            'status':   status,
            'breaches': breaches,
            'total_positions': len(holdings),
        }


@register_node(
    code='suitability_check',
    sectors=['finance'],
    retry_policy='none'
)
class SuitabilityCheckNode(BaseNode):
    """
    Checks if the portfolio matches the client's risk profile.
    Compares portfolio risk score against client's declared risk tolerance.
    Returns PASS, WARN, or REQUIRES_APPROVAL.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        portfolio_risk  = input_data.get('portfolio_risk_score', 0)
        client_tolerance = input_data.get('client_risk_tolerance', 0)
        threshold       = input_data.get('warn_threshold', 10)

        delta = portfolio_risk - client_tolerance

        if delta <= 0:
            status = 'PASS'
        elif delta <= threshold:
            status = 'WARN'
        else:
            status = 'REQUIRES_APPROVAL'

        logger.info(f'Suitability check: {status} — delta={delta}')

        return {
            'status':            status,
            'portfolio_risk':    portfolio_risk,
            'client_tolerance':  client_tolerance,
            'delta':             delta,
        }


@register_node(
    code='compute_metrics',
    sectors=['finance'],
    retry_policy='none'         # deterministic compute
)
class ComputeMetricsNode(BaseNode):
    """
    Computes portfolio performance metrics:
    total value, daily P&L, weighted average risk score.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        holdings = input_data.get('holdings', [])

        total_value     = sum(h.get('value', 0) for h in holdings)
        total_cost      = sum(h.get('cost', 0) for h in holdings)
        pnl             = total_value - total_cost
        pnl_pct         = round((pnl / total_cost * 100), 2) if total_cost else 0

        weighted_risk = 0
        if total_value > 0:
            weighted_risk = sum(
                h.get('value', 0) / total_value * h.get('risk_score', 0)
                for h in holdings
            )

        logger.info(f'Metrics computed: total_value={total_value}, pnl={pnl}')

        return {
            'total_value':        round(total_value, 2),
            'total_cost':         round(total_cost, 2),
            'pnl':                round(pnl, 2),
            'pnl_pct':            pnl_pct,
            'weighted_risk_score': round(weighted_risk, 4),
            'positions_count':    len(holdings),
        }


@register_node(
    code='generate_report',
    sectors=['finance'],
    retry_policy='bounded'
)
class GenerateReportNode(BaseNode):
    """
    Claude-powered portfolio review report generator.
    Uses metrics, policy outcomes, and human decision to produce
    a structured narrative report with risk summary and recommendations.
    """
    def execute(self, input_data: dict, context: dict) -> dict:
        import os
        import json
        import anthropic

        metrics        = input_data.get('metrics', {})
        policy_results = input_data.get('policy_results', [])
        human_action   = input_data.get('human_action', {})

        passed = sum(1 for r in policy_results if r.get('status') == 'PASS')
        failed = sum(1 for r in policy_results if r.get('status') == 'FAIL')
        warned = sum(1 for r in policy_results if r.get('status') == 'WARN')

        # safe fallback if Claude is unavailable
        report = {
            'report_type':    'portfolio_review',
            'total_value':    metrics.get('total_value', 0),
            'pnl':            metrics.get('pnl', 0),
            'pnl_pct':        metrics.get('pnl_pct', 0),
            'policy_summary': {'passed': passed, 'warned': warned, 'failed': failed},
            'decision':       human_action.get('action', 'N/A'),
            'decided_by':     human_action.get('actor', 'N/A'),
            'narrative':      '',
            'risk_summary':   '',
            'recommendations': [],
            'llm_powered':    False,
            'status':         'complete',
        }

        try:
            api_key = os.environ.get('ANTHROPIC_API_KEY', '')
            if not api_key:
                logger.warning('[generate_report] ANTHROPIC_API_KEY not set — returning fallback report')
                return report

            client = anthropic.Anthropic(api_key=api_key)

            prompt = f"""You are a senior portfolio analyst writing a concise investment review report.

Portfolio Metrics:
{json.dumps(metrics, indent=2, default=str)}

Policy Check Results:
- Passed: {passed}
- Warned: {warned}
- Failed: {failed}
Policy details: {json.dumps(policy_results, indent=2, default=str)}

Human Decision:
- Action: {human_action.get('action', 'N/A')}
- By: {human_action.get('actor', 'N/A')}
- Justification: {human_action.get('justification', '')}

Write a structured portfolio review report. Respond ONLY with a valid JSON object. No markdown, no code fences.
Use exactly this structure:
{{
  "narrative": "2-3 sentence executive summary of the portfolio review outcome",
  "risk_summary": "1-2 sentences describing the key risk findings",
  "recommendations": ["recommendation 1", "recommendation 2"]
}}

Rules:
- narrative: factual, professional tone, reference actual numbers from metrics
- risk_summary: only mention real risks from the policy results above
- recommendations: 1-3 specific, actionable items for the portfolio manager"""

            message = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=512,
                messages=[{'role': 'user', 'content': prompt}]
            )

            raw = message.content[0].text.strip()
            if raw.startswith('```'):
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
                raw = raw.strip()

            parsed = json.loads(raw)
            report.update({
                'narrative':       parsed.get('narrative', ''),
                'risk_summary':    parsed.get('risk_summary', ''),
                'recommendations': parsed.get('recommendations', []),
                'llm_powered':     True,
            })

            logger.info(f'[generate_report] Claude report generated for portfolio {metrics.get("portfolio_id", "")}')

        except json.JSONDecodeError as e:
            logger.error(f'[generate_report] JSON parse failed — {e}')
        except Exception as e:
            logger.error(f'[generate_report] Claude call failed — {e}')

        return report