"""
Question 1: Voice Agent - Mock CRM Actions, Preliminary Eligibility, and Escalation Webhook
Implements business actions: lead storage, qualification scoring, and escalation dispatch.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class LeadData(BaseModel):
    lead_id: str = Field(default_factory=lambda: f"lead_{uuid.uuid4().hex[:8]}")
    customer_name: str
    phone_number: str
    age: int
    pre_existing_conditions: str
    tobacco_user: bool
    budget_range: str
    qualification_status: str  # QUALIFIED, PENDING_UNDERWRITING, DISQUALIFIED
    eligibility_score: int     # 0 to 100
    applied_loading: float     # e.g. 0.15 for 15% loading
    notes: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class EscalationTicket(BaseModel):
    ticket_id: str = Field(default_factory=lambda: f"esc_{uuid.uuid4().hex[:8]}")
    caller_phone: str
    reason: str
    urgency: str  # NORMAL, HIGH, CRITICAL
    dialog_turn_count: int
    conversation_summary: str
    escalation_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class MockCRMService:
    """
    Mock CRM and Webhook dispatch service for voice agent.
    """
    def __init__(self):
        self.leads_db: Dict[str, LeadData] = {}
        self.escalations_db: Dict[str, EscalationTicket] = {}

    def calculate_eligibility(self, age: int, pre_existing: str, tobacco: bool) -> Dict[str, Any]:
        """
        Applies Q2 Underwriting Policy Rules:
        - Entry age: 18-65
        - Disqualifications: renal dialysis, active chemotherapy
        - Controlled conditions: hypertension / diabetes get 15% loading
        - Non-smoker: preferred pricing
        """
        score = 85
        status = "QUALIFIED"
        loading = 0.0
        notes = []

        # Age qualification check
        if age < 18 or age > 65:
            status = "DISQUALIFIED"
            score = 0
            notes.append(f"Age {age} is outside the standard enrollment bracket (18-65).")
            return {"status": status, "score": score, "loading": loading, "notes": "; ".join(notes)}

        if age >= 55:
            notes.append("Tele-medical screening mandatory (applicant aged >= 55).")
            score -= 10

        # Pre-existing condition check
        pre_lower = pre_existing.lower()
        if any(bad in pre_lower for bad in ["dialysis", "chemotherapy", "cancer", "organ transplant"]):
            status = "PENDING_SPECIALIST_UNDERWRITING"
            score = 30
            notes.append("Active severe condition detected; requires high-risk medical board review.")
        elif any(ctrl in pre_lower for ctrl in ["diabetes", "hypertension", "bp", "blood pressure"]):
            status = "QUALIFIED_WITH_LOADING"
            score = 75
            loading = 0.15
            notes.append("Standard 15% premium loading applied for controlled condition.")
        else:
            notes.append("Standard risk profile.")

        if tobacco:
            score -= 10
            notes.append("Tobacco user rates apply (ineligible for preferred 12% non-smoker discount).")
        else:
            notes.append("Preferred non-smoker discount applied.")

        return {
            "status": status,
            "score": max(0, min(100, score)),
            "loading": loading,
            "notes": "; ".join(notes)
        }

    def create_lead(self, name: str, phone: str, age: int, pre_existing: str, tobacco: bool, budget: str) -> LeadData:
        """
        Registers qualified lead into Mock CRM.
        """
        eval_res = self.calculate_eligibility(age, pre_existing, tobacco)
        lead = LeadData(
            customer_name=name,
            phone_number=phone,
            age=age,
            pre_existing_conditions=pre_existing,
            tobacco_user=tobacco,
            budget_range=budget,
            qualification_status=eval_res["status"],
            eligibility_score=eval_res["score"],
            applied_loading=eval_res["loading"],
            notes=eval_res["notes"]
        )
        self.leads_db[lead.lead_id] = lead
        return lead

    def dispatch_escalation(self, phone: str, reason: str, turns: int, summary: str, urgency: str = "NORMAL") -> EscalationTicket:
        """
        Dispatches escalation webhook and creates immediate human callback/transfer ticket.
        """
        ticket = EscalationTicket(
            caller_phone=phone,
            reason=reason,
            urgency=urgency,
            dialog_turn_count=turns,
            conversation_summary=summary
        )
        self.escalations_db[ticket.ticket_id] = ticket
        return ticket

crm_service = MockCRMService()
