# sectors/registry.py
"""
Sector registry — maps each sector to its workflows, nodes, and policies.
This is the single source of truth for what's available per sector.
TenantWorkflowConfig can override per-tenant, but this is the default.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class SectorConfig:
    """
    Configuration for a single sector.
    Defines which agents, nodes, and compliance drivers apply.
    """
    code:               str
    name:               str
    compliance_drivers: List[str]
    agents:             List[str]
    node_codes:         List[str]
    hitl_pause_node:    str        # last node before human_decision
    post_hitl_nodes:    List[str]  # nodes to run after HITL approval
    description:        str = ''


# ─── Sector Definitions ───────────────────────────────────────────────────────

SECTORS: dict[str, SectorConfig] = {

    'finance': SectorConfig(
        code='finance',
        name='Finance & Wealth Management',
        description='Portfolio review, client suitability, MiFID II compliance.',
        compliance_drivers=['MiFID II', 'SEBI', 'FINRA'],
        agents=['portfolio_review_agent'],
        node_codes=[
            'portfolio_import', 'compute_metrics',
            'concentration_check', 'suitability_check',
            'evaluate_policies', 'human_decision',
            'approval_gate', 'generate_report', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_report', 'extract_insights'],
    ),

    'it': SectorConfig(
        code='it',
        name='IT / Technology',
        description='Change request approval, SOC 2 evidence, ITIL compliance.',
        compliance_drivers=['ISO 27001', 'SOC 2', 'ITIL'],
        agents=['change_request_agent'],
        node_codes=[
            'validate_change_request', 'check_freeze_window',
            'evaluate_risk_level', 'evaluate_policies',
            'notify_cab', 'human_decision', 'approval_gate',
            'generate_soc2_evidence', 'extract_insights',
        ],
        hitl_pause_node='notify_cab',
        post_hitl_nodes=['generate_soc2_evidence', 'extract_insights'],
    ),

    'hr': SectorConfig(
        code='hr',
        name='HR / People Ops',
        description='Hiring approvals, payroll, PF/ESI compliance.',
        compliance_drivers=['Labour Law', 'PF/ESI'],
        agents=['hr_onboarding_agent'],
        node_codes=[
            'validate_job_requisition', 'check_headcount_budget',
            'validate_salary_band', 'evaluate_policies',
            'check_pf_esi_compliance', 'human_decision',
            'approval_gate', 'generate_offer_letter', 'extract_insights',
        ],
        hitl_pause_node='check_pf_esi_compliance',
        post_hitl_nodes=['generate_offer_letter', 'extract_insights'],
    ),

    'legal': SectorConfig(
        code='legal',
        name='Legal',
        description='Contract review, conflict checks, filing deadlines.',
        compliance_drivers=['Bar regulations', 'Filing deadlines'],
        agents=['contract_review_agent'],
        node_codes=[
            'validate_contract', 'conflict_of_interest_check',
            'legal_risk_assessment', 'evaluate_policies',
            'human_decision', 'approval_gate',
            'generate_legal_summary', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_legal_summary', 'extract_insights'],
    ),

    'healthcare': SectorConfig(
        code='healthcare',
        name='Healthcare',
        description='Patient approvals, prescription limits, HIPAA compliance.',
        compliance_drivers=['HIPAA', 'FDA', 'IRB'],
        agents=['patient_approval_agent'],
        node_codes=[
            'validate_patient_record', 'check_prescription_limits',
            'insurance_eligibility_check', 'evaluate_policies',
            'human_decision', 'approval_gate',
            'generate_clinical_summary', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_clinical_summary', 'extract_insights'],
    ),

    'insurance': SectorConfig(
        code='insurance',
        name='Insurance',
        description='Claims processing, fraud detection, settlement calculation.',
        compliance_drivers=['IRDAI', 'NAIC'],
        agents=['claim_processing_agent'],
        node_codes=[
            'validate_claim', 'fraud_detection_check',
            'calculate_settlement', 'evaluate_policies',
            'human_decision', 'approval_gate',
            'generate_claim_decision', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_claim_decision', 'extract_insights'],
    ),

    'education': SectorConfig(
        code='education',
        name='Education',
        description='Admissions, grants, FERPA and NAAC compliance.',
        compliance_drivers=['FERPA', 'NAAC', 'IRB'],
        agents=['admission_review_agent'],
        node_codes=[
            'validate_admission_application', 'check_eligibility_criteria',
            'grant_compliance_check', 'evaluate_policies',
            'human_decision', 'approval_gate',
            'generate_admission_decision', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_admission_decision', 'extract_insights'],
    ),

    'government': SectorConfig(
        code='government',
        name='Government',
        description='Tenders, grants, public procurement compliance.',
        compliance_drivers=['CAG', 'Public Procurement Rules'],
        agents=['tender_approval_agent'],
        node_codes=[
            'validate_tender', 'check_procurement_policy',
            'evaluate_policies', 'human_decision',
            'approval_gate', 'generate_tender_report', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_tender_report', 'extract_insights'],
    ),

    'energy': SectorConfig(
        code='energy',
        name='Energy',
        description='ESG reporting, carbon credits, emission compliance.',
        compliance_drivers=['SEBI ESG', 'GRI', 'CERT-In'],
        agents=['esg_review_agent'],
        node_codes=[
            'validate_esg_report', 'check_emission_limits',
            'evaluate_policies', 'human_decision',
            'approval_gate', 'generate_esg_certificate', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_esg_certificate', 'extract_insights'],
    ),

    'telecom': SectorConfig(
        code='telecom',
        name='Telecom',
        description='Spectrum licenses, subscriber data, TRAI compliance.',
        compliance_drivers=['TRAI', 'FCC', 'Data Localisation'],
        agents=['license_approval_agent'],
        node_codes=[
            'validate_license_application', 'check_spectrum_availability',
            'evaluate_policies', 'human_decision',
            'approval_gate', 'generate_license_decision', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_license_decision', 'extract_insights'],
    ),

    'manufacturing': SectorConfig(
        code='manufacturing',
        name='Manufacturing',
        description='Quality control, ISO certifications, GMP compliance.',
        compliance_drivers=['ISO 9001', 'GMP'],
        agents=['quality_review_agent'],
        node_codes=[
            'validate_quality_inspection', 'check_defect_rate',
            'evaluate_policies', 'human_decision',
            'approval_gate', 'generate_quality_certificate', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_quality_certificate', 'extract_insights'],
    ),

    'logistics': SectorConfig(
        code='logistics',
        name='Logistics',
        description='Shipment clearance, customs compliance, supply chain.',
        compliance_drivers=['Customs Act', 'ISO Supply Chain'],
        agents=['shipment_clearance_agent'],
        node_codes=[
            'validate_shipment', 'check_customs_compliance',
            'evaluate_policies', 'human_decision',
            'approval_gate', 'generate_shipping_clearance', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_shipping_clearance', 'extract_insights'],
    ),

    'retail': SectorConfig(
        code='retail',
        name='Retail / E-commerce',
        description='Vendor onboarding, fraud, GST compliance.',
        compliance_drivers=['Consumer Protection', 'GST'],
        agents=['vendor_onboarding_agent'],
        node_codes=[
            'validate_vendor_onboarding', 'check_return_policy_compliance',
            'evaluate_policies', 'human_decision',
            'approval_gate', 'generate_vendor_approval', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_vendor_approval', 'extract_insights'],
    ),

    'cybersecurity': SectorConfig(
        code='cybersecurity',
        name='Cybersecurity',
        description='Incident response, vulnerability approvals, CERT-In.',
        compliance_drivers=['ISO 27001', 'CERT-In'],
        agents=['incident_response_agent'],
        node_codes=[
            'validate_security_incident', 'assess_threat_level',
            'check_regulatory_notification', 'evaluate_policies',
            'human_decision', 'approval_gate',
            'generate_incident_report', 'extract_insights',
        ],
        hitl_pause_node='evaluate_policies',
        post_hitl_nodes=['generate_incident_report', 'extract_insights'],
    ),
}


# ─── Registry API ─────────────────────────────────────────────────────────────

def get_sector(code: str) -> SectorConfig:
    """Returns SectorConfig for a given sector code. Raises ValueError if not found."""
    config = SECTORS.get(code)
    if not config:
        raise ValueError(f'No sector registered for code: {code}')
    return config


def get_all_sectors() -> list[SectorConfig]:
    """Returns all registered sectors."""
    return list(SECTORS.values())


def get_hitl_pause_node(sector_code: str) -> str:
    """Returns the last node before human_decision for a sector."""
    return get_sector(sector_code).hitl_pause_node


def get_post_hitl_nodes(sector_code: str) -> list[str]:
    """Returns the nodes to execute after HITL approval for a sector."""
    return get_sector(sector_code).post_hitl_nodes


def sector_exists(code: str) -> bool:
    return code in SECTORS