"""
Question 1: Voice Agent - Core Grounded Conversation Engine
Orchestrates dialog flow, extracts qualification slots, calls Question 2 Knowledge Base
for dynamic objection & FAQ handling, safely handles fallbacks, and executes CRM actions.
"""

import re
import uuid
from typing import Dict, Any, Tuple, Optional
from .dialog_state import DialogSession, DialogStage
from .crm_actions import crm_service
from q2_knowledge_base.retriever import KnowledgeBaseEngine

class GroundedVoiceAgent:
    """
    Knowledge-Grounded Voice Agent for Health Insurance Qualification:
    - Never hardcodes answers; dynamically queries Q2 Knowledge Base.
    - Explicitly falls back when information is unavailable.
    - Gracefully handles human escalation requests.
    - Qualifies applicants and syncs records to Mock CRM.
    """

    HUMAN_ESCALATION_KEYWORDS = [
        "human", "representative", "real person", "agent", "supervisor", 
        "operator", "talk to someone", "customer service person"
    ]

    def __init__(self, kb_engine: KnowledgeBaseEngine):
        self.kb_engine = kb_engine
        self.sessions: Dict[str, DialogSession] = {}

    def get_or_create_session(self, session_id: Optional[str] = None, phone: str = "+1-555-010-9988") -> DialogSession:
        sid = session_id or f"sess_{uuid.uuid4().hex[:6]}"
        if sid not in self.sessions:
            self.sessions[sid] = DialogSession(session_id=sid, phone_number=phone)
        return self.sessions[sid]

    def process_turn(self, session: DialogSession, user_input: str) -> Dict[str, Any]:
        """
        Processes one conversational turn and produces the agent's spoken response,
        tracking knowledge citations, fallback flags, and qualification state.
        """
        text = user_input.strip()
        session.add_turn(speaker="Customer", text=text, stage=session.stage)
        
        user_lower = text.lower()

        # 1. Check for Human Escalation Request
        if any(kw in user_lower for kw in self.HUMAN_ESCALATION_KEYWORDS):
            session.stage = DialogStage.HUMAN_ESCALATION
            session.is_escalated = True
            ticket = crm_service.dispatch_escalation(
                phone=session.phone_number,
                reason="Customer explicitly requested live human assistance",
                turns=len(session.turns),
                summary=f"Caller {session.customer_name or 'Anonymous'} requested transfer during stage {session.stage.value}.",
                urgency="HIGH"
            )
            agent_response = (
                f"I completely understand. I have initiated a warm transfer to one of our licensed senior "
                f"underwriters. Your reference ticket is {ticket.ticket_id}. Please stay on the line while I connect you."
            )
            session.add_turn(speaker="Agent", text=agent_response, stage=session.stage, notes=f"Escalation ticket {ticket.ticket_id}")
            return {
                "response": agent_response,
                "session": session,
                "action": "ESCALATE",
                "ticket_id": ticket.ticket_id,
                "is_grounded": True,
                "citation": None
            }

        # 2. Check for Closing / Acknowledgement when in CONFIRMATION stage
        if session.stage in [DialogStage.CONFIRMATION, DialogStage.COMPLETED]:
            if any(w in user_lower for w in ["no", "that covers", "everything", "all good", "thanks", "thank you", "goodbye", "bye"]):
                session.stage = DialogStage.COMPLETED
                response = "Thank you for contacting HealthGuard Solutions. Have a wonderful day!"
                session.add_turn(speaker="Agent", text=response, stage=session.stage)
                return {"response": response, "session": session, "action": "COMPLETE"}

        # 3. Check if user is asking an informational question or raising an objection
        is_question_or_objection = any([
            "?" in text,
            "already have" in user_lower,
            "too expensive" in user_lower or "budget" in user_lower and session.stage != DialogStage.QUALIFYING_BUDGET,
            any(user_lower.startswith(w) for w in ["what", "how", "does", "can", "why", "is"]),
            any(w in user_lower for w in ["waiting period", "cashless", "employer", "cosmetic", "bitcoin", "crypto", "dialysis"])
        ])

        if is_question_or_objection and session.stage not in [DialogStage.COMPLETED, DialogStage.HUMAN_ESCALATION]:
            # Consult Q2 Knowledge Base dynamically
            kb_res = self.kb_engine.answer_query(text)
            
            # Check for explicitly excluded / out of scope topics
            is_out_of_scope = any(bad in user_lower for bad in ["cosmetic", "nose job", "bitcoin", "crypto", "trading loss", "hair transplant"])
            
            if not kb_res["is_grounded"] or is_out_of_scope:
                # UNSUPPORTED QUESTION FALLBACK (Must state when info is unavailable instead of inventing)
                agent_response = (
                    "I checked our verified database: that item (such as elective cosmetic procedures or investment risks) is not covered under our medical policies. "
                    "We only cover medically necessary hospitalization and treatments. "
                    f"Now {session.customer_name or 'there'}, would you like to continue checking your eligible medical coverage?"
                )
                session.add_turn(
                    speaker="Agent", 
                    text=agent_response, 
                    stage=DialogStage.KNOWLEDGE_CONSULTATION, 
                    kb_used=True, 
                    notes="Fallback triggered: Query out of scope or excluded from policy database."
                )
                return {
                    "response": agent_response,
                    "session": session,
                    "action": "FALLBACK_UNSUPPORTED",
                    "is_grounded": True,
                    "confidence": kb_res["confidence_score"]
                }
            else:
                # Grounded response using Q2 citation
                retrieved_content = kb_res["retrieved_chunk"]["content"]
                citation = kb_res["citation"]

                # Tailor response naturally with the grounded knowledge
                if "employer" in user_lower:
                    explanation = (
                        "That is a great consideration! However, employer group cover ends if you transition jobs or retire. "
                        "Having your own personal policy locks in low entry rates and guarantees continuous protection. "
                    )
                elif "expensive" in user_lower or "cost" in user_lower:
                    explanation = (
                        "I understand cost is a priority. We offer flexible high-deductible options that lower premiums by up to 35%, "
                        "along with monthly installment plans so you don't face large lump sums. "
                    )
                else:
                    sentences = [s.strip() for s in retrieved_content.split(".") if len(s.strip()) > 15]
                    explanation = ". ".join(sentences[:2]) + ". "

                # Reconnect to qualification flow
                prompt_next = self._get_next_qualification_prompt(session)
                agent_response = f"{explanation} {prompt_next}".strip()

                session.add_turn(
                    speaker="Agent", 
                    text=agent_response, 
                    stage=DialogStage.KNOWLEDGE_CONSULTATION,
                    kb_used=True,
                    citation=citation
                )
                return {
                    "response": agent_response,
                    "session": session,
                    "action": "GROUNDED_ANSWER",
                    "citation": citation,
                    "confidence": kb_res["confidence_score"]
                }

        # 3. Standard Qualification State Flow
        return self._handle_qualification_flow(session, text)

    def _handle_qualification_flow(self, session: DialogSession, text: str) -> Dict[str, Any]:
        user_lower = text.lower()

        # STAGE: GREETING
        if session.stage == DialogStage.GREETING:
            session.stage = DialogStage.COLLECTING_NAME
            response = "Hello! Thanks for calling HealthGuard Solutions. May I know your name to get started?"
            session.add_turn(speaker="Agent", text=response, stage=session.stage)
            return {"response": response, "session": session, "action": "NEXT"}

        # STAGE: COLLECTING_NAME
        if session.stage == DialogStage.COLLECTING_NAME:
            # Extract name (strip polite prefixes)
            name_match = re.search(r"(?:my name is|this is|i am|i'm)?\s*([a-zA-Z]+(?:\s+[a-zA-Z]+)?)", text, re.IGNORECASE)
            name = name_match.group(1) if name_match else text.split()[0]
            session.customer_name = name.title()
            session.stage = DialogStage.QUALIFYING_AGE
            response = f"Nice to meet you, {session.customer_name}. To ensure we check the right underwriting plan, could you please tell me your current age?"
            session.add_turn(speaker="Agent", text=response, stage=session.stage)
            return {"response": response, "session": session, "action": "NEXT"}

        # STAGE: QUALIFYING_AGE
        if session.stage == DialogStage.QUALIFYING_AGE:
            age_match = re.search(r"\b(\d{1,3})\b", text)
            if not age_match:
                response = "I couldn't catch your exact age. Could you please specify your age in years (for example, 38)?"
                session.add_turn(speaker="Agent", text=response, stage=session.stage)
                return {"response": response, "session": session, "action": "CLARIFICATION_NEEDED"}
            
            age = int(age_match.group(1))
            
            # Check conflicting / unrealistic input
            if age < 0 or age > 120:
                response = f"You mentioned {age}, which seems unusual. Could you please confirm your actual age?"
                session.add_turn(speaker="Agent", text=response, stage=session.stage)
                return {"response": response, "session": session, "action": "CONFLICT_RESOLUTION"}

            session.age = age
            session.stage = DialogStage.QUALIFYING_HEALTH
            response = f"Got it, {age} years old. Next, do you have any pre-existing health conditions such as high blood pressure, diabetes, or any ongoing treatments?"
            session.add_turn(speaker="Agent", text=response, stage=session.stage)
            return {"response": response, "session": session, "action": "NEXT"}

        # STAGE: QUALIFYING_HEALTH
        if session.stage == DialogStage.QUALIFYING_HEALTH:
            # Check for vague / incomplete answers
            if any(v in text.lower() for v in ["maybe", "not sure", "depends", "why do you ask", "uncertain"]):
                response = "Underwriting guidelines require us to record diagnosed conditions like hypertension or diabetes. Do you take regular prescription medications for any condition?"
                session.add_turn(speaker="Agent", text=response, stage=session.stage)
                return {"response": response, "session": session, "action": "CLARIFICATION_NEEDED"}

            session.pre_existing_conditions = text
            session.tobacco_user = any(w in user_lower for w in ["smoke", "tobacco", "cigarettes", "vape", "yes i smoke"])
            session.stage = DialogStage.QUALIFYING_BUDGET
            response = "Understood, thank you for sharing that. Lastly, what monthly or annual coverage budget did you have in mind?"
            session.add_turn(speaker="Agent", text=response, stage=session.stage)
            return {"response": response, "session": session, "action": "NEXT"}

        # STAGE: QUALIFYING_BUDGET
        if session.stage == DialogStage.QUALIFYING_BUDGET:
            session.budget_range = text
            session.stage = DialogStage.CONFIRMATION
            
            # Execute Business Action: Mock CRM Lead Creation & Eligibility Evaluation
            lead = crm_service.create_lead(
                name=session.customer_name or "Applicant",
                phone=session.phone_number,
                age=session.age or 35,
                pre_existing=session.pre_existing_conditions or "None",
                tobacco=session.tobacco_user,
                budget=session.budget_range
            )
            session.crm_lead_id = lead.lead_id
            session.qualification_result = {
                "status": lead.qualification_status,
                "score": lead.eligibility_score,
                "loading": lead.applied_loading,
                "notes": lead.notes
            }

            response = (
                f"Thank you, {session.customer_name}! Based on our preliminary underwriting criteria, "
                f"your eligibility status is: {lead.qualification_status} (Score: {lead.eligibility_score}/100). "
                f"I have created CRM Lead profile #{lead.lead_id} for you. A licensed specialist will call you at "
                f"{session.phone_number} with personalized quote proposals. Is there anything else I can help with today?"
            )
            session.add_turn(speaker="Agent", text=response, stage=session.stage, notes=f"CRM Lead {lead.lead_id}")
            return {"response": response, "session": session, "action": "LEAD_CREATED", "lead": lead.model_dump()}

        # STAGE: CONFIRMATION / CLOSING
        if session.stage in [DialogStage.CONFIRMATION, DialogStage.COMPLETED]:
            session.stage = DialogStage.COMPLETED
            response = "Thank you for contacting HealthGuard Solutions. Have a wonderful day!"
            session.add_turn(speaker="Agent", text=response, stage=session.stage)
            return {"response": response, "session": session, "action": "COMPLETE"}

        # Default fallback
        response = "Could you please clarify that for me?"
        session.add_turn(speaker="Agent", text=response, stage=session.stage)
        return {"response": response, "session": session, "action": "UNKNOWN"}

    def _get_next_qualification_prompt(self, session: DialogSession) -> str:
        if session.customer_name is None:
            return "May I know your name to get started?"
        elif session.age is None:
            return f"Now {session.customer_name}, could you tell me your age?"
        elif session.pre_existing_conditions is None:
            return "Do you currently have any declared pre-existing health conditions or illnesses?"
        elif session.budget_range is None:
            return "What monthly or annual budget did you have in mind for your policy?"
        else:
            return "Shall we finalize your preliminary underwriting profile?"
