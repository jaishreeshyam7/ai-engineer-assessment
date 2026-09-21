"""
Question 1: Voice Agent - Dialog State Machine & Qualification Model
Manages conversation state, customer qualification slots, and escalation triggers.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class DialogStage(str, Enum):
    GREETING = "GREETING"
    COLLECTING_NAME = "COLLECTING_NAME"
    QUALIFYING_AGE = "QUALIFYING_AGE"
    QUALIFYING_HEALTH = "QUALIFYING_HEALTH"
    QUALIFYING_BUDGET = "QUALIFYING_BUDGET"
    OBJECTION_HANDLING = "OBJECTION_HANDLING"
    KNOWLEDGE_CONSULTATION = "KNOWLEDGE_CONSULTATION"
    CONFIRMATION = "CONFIRMATION"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"
    COMPLETED = "COMPLETED"

class TurnRecord(BaseModel):
    speaker: str  # "Agent" or "Customer"
    text: str
    stage: DialogStage
    timestamp: str
    kb_retrieval_used: bool = False
    retrieved_citation: Optional[str] = None
    notes: Optional[str] = None

class DialogSession(BaseModel):
    session_id: str
    stage: DialogStage = DialogStage.GREETING
    customer_name: Optional[str] = None
    phone_number: str = "+1-555-010-9988"
    age: Optional[int] = None
    pre_existing_conditions: Optional[str] = None
    tobacco_user: bool = False
    budget_range: Optional[str] = None
    turns: List[TurnRecord] = Field(default_factory=list)
    pending_objection: Optional[str] = None
    is_escalated: bool = False
    crm_lead_id: Optional[str] = None
    qualification_result: Optional[Dict[str, Any]] = None

    def add_turn(self, speaker: str, text: str, stage: Optional[DialogStage] = None, 
                 kb_used: bool = False, citation: Optional[str] = None, notes: Optional[str] = None):
        import datetime
        cur_stage = stage or self.stage
        self.turns.append(TurnRecord(
            speaker=speaker,
            text=text,
            stage=cur_stage,
            timestamp=datetime.datetime.utcnow().strftime("%H:%M:%S"),
            kb_retrieval_used=kb_used,
            retrieved_citation=citation,
            notes=notes
        ))
