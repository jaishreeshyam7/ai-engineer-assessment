"""
Question 3: Native-Language Voice Bots - Philippines Bancassurance Bot
Handles natural Tagalog, English, and Taglish code-switching for Life Insurance & Bancassurance.
Adheres to cultural politeness ('po/opo'), banking referral context, and insurance terminology.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class PHLocalizationExample(BaseModel):
    scenario: str
    literal_translation: str
    localized_taglish: str
    cultural_rationale: str

# 3+ Documented Adaptation Examples showing localization vs direct translation
PH_LOCALIZATION_SHOWCASE = [
    PHLocalizationExample(
        scenario="Reminder that premium is due to prevent policy lapse",
        literal_translation="Ang inyong premium ay dapat bayaran bukas upang maiwasan ang pagka-lapse ng inyong patakaran.",
        localized_taglish="Good day po, Ma'am! Quick reminder lang po mula sa Bancassurance team tungkol sa inyong policy premium due sa Friday para continuous po ang inyong coverage at hindi mag-lapse.",
        cultural_rationale="Literal Tagalog ('patakaran', 'dapat bayaran') sounds unnervingly bureaucratic and accusatory. Taglish with 'po', 'quick reminder lang po', and maintaining English industry terms ('policy premium', 'coverage', 'lapse') matches how Philippine financial advisors converse in urban and provincial branches."
    ),
    PHLocalizationExample(
        scenario="Handling customer objection regarding tight budget / salary timing",
        literal_translation="Kung wala kayong pera, kailangan ninyong magbayad bago ang tatlumpung araw.",
        localized_taglish="Naiintindihan ko po, Sir. May 31-day grace period naman po tayo. Kung mas convenient po sa inyo sa susunod na sahod sa katapusan, pwede po nating i-set ang auto-debit sa cut-off niyo.",
        cultural_rationale="In the Philippines, personal cash flow is closely tied to bi-monthly pay cycles ('15-30 cut-off'). Localized phrasing acknowledges financial dignity ('naiintindihan ko po') and introduces the grace period with practical scheduling options like auto-debit on payday."
    ),
    PHLocalizationExample(
        scenario="Inquiring about beneficiaries and riders",
        literal_translation="Sino ang mga tao na makakatanggap ng pera kapag namatay ka kasama ang mangangabayo?",
        localized_taglish="Pwede po natin i-check ang inyong registered primary beneficiaries at kung active po ang inyong accidental death at critical illness riders.",
        cultural_rationale="A catastrophic direct machine translation translates insurance 'rider' as 'mangangabayo' (horse rider)! A localized bot retains recognized financial loanwords ('beneficiaries', 'riders', 'critical illness') in seamless Taglish syntax."
    )
]

class PhilippinesVoiceBot:
    """
    Taglish Bancassurance Assistant for Life Insurance:
    - Flow: Premium & Renewal Reminder, Coverage Check, Grace Period, Branch Referral.
    - Preserves Taglish conversational register without abrupt English switching.
    """

    FINANCE_TERMS = ["premium", "policy", "beneficiary", "rider", "lapse", "coverage", "bank referral", "grace period"]

    def __init__(self):
        self.market = "Philippines"
        self.sector = "Bancassurance & Life Insurance"
        self.language = "Taglish (Tagalog-English code-switching)"

    def process_turn(self, state: dict, user_text: str) -> dict:
        text_lower = user_text.lower()
        turn_count = state.get("turn_count", 0) + 1
        state["turn_count"] = turn_count

        # Check for Human Escalation
        if any(w in text_lower for w in ["human", "tao", "makausap", "agent", "specialist", "branch manager", "representative"]):
            response = (
                "Walang problema po, Ma'am/Sir. I-coconnect ko po kayo agad sa ating Bancassurance Specialist "
                "sa inyong partner bank branch para ma-assist po kayo nang personal. Sandali lang po, huwag po kayong bibitaw."
            )
            return {
                "response": response,
                "action": "ESCALATE_PH",
                "language_detected": "Taglish",
                "escalated": True
            }

        # Flow State Handling
        stage = state.get("stage", "GREETING")

        if stage == "GREETING":
            state["stage"] = "VERIFY_IDENTITY"
            response = (
                "Magandang araw po! Tumatawag po ako mula sa BPI-AIA Bancassurance Customer Care. "
                "Ako po ba ay nakikipag-usap kay Mr. Ronald Cruz?"
            )
            return {"response": response, "stage": state["stage"]}

        if stage == "VERIFY_IDENTITY":
            state["stage"] = "DELIVER_PURPOSE"
            response = (
                "Salamat po, Sir Ronald. Tumatawag po kami para sa inyong Life Ready Plus policy. "
                "Ang quarterly premium po ninyo na ₱4,500 ay due na po sa darating na March 25 para manatiling active ang inyong coverage."
            )
            return {"response": response, "stage": state["stage"]}

        if stage == "DELIVER_PURPOSE":
            # Check for objections or financial hardship
            if any(w in text_lower for w in ["mahal", "mahirap", "delay", "katapusan", "sahod", "petsa de peligro", "pera", "tight"]):
                state["stage"] = "OFFER_GRACE_PERIOD"
                response = (
                    "Naiintindihan po namin, Sir Ronald. May 30-day grace period naman po ang policy ninyo hanggang April 25, "
                    "kaya continuous pa rin po ang proteksyon ng inyong mga beneficiaries. Pwede rin po natin i-schedule ang payment via GCash o BPI Online sa darating na payday. Pabor po ba sa inyo 'yun?"
                )
                return {"response": response, "stage": state["stage"], "objection_handled": True}
            
            # Check for coverage / rider questions
            elif any(w in text_lower for w in ["rider", "beneficiary", "coverage", "check", "ano ba", "kasama"]):
                state["stage"] = "ANSWER_COVERAGE"
                response = (
                    "Opo, Sir. Sa inyong policy record, covered po kayo ng ₱1,000,000 basic life benefit plus may "
                    "Accidental Death & Dismemberment rider po kayo. Ang inyo pong misis ang registered primary beneficiary."
                )
                return {"response": response, "stage": state["stage"]}
            else:
                state["stage"] = "PAYMENT_METHOD"
                response = (
                    "Maraming salamat po! Pwede po ninyong bayaran ang premium conveniently gamit ang BPI Online App, "
                    "GCash bills payment, o auto-debit arrangement. Gusto niyo po bang i-send ko ang payment link sa SMS ninyo?"
                )
                return {"response": response, "stage": state["stage"]}

        if stage in ["OFFER_GRACE_PERIOD", "ANSWER_COVERAGE", "PAYMENT_METHOD"]:
            state["stage"] = "CLOSING"
            response = (
                "Maraming salamat po sa inyong tiwala, Sir Ronald! Na-send ko na po ang payment reference at branch referral "
                "details sa inyong registered mobile number. Mag-ingat po kayo at magandang araw po!"
            )
            return {"response": response, "stage": state["stage"], "completed": True}

        # Fallback in culturally polite Taglish
        response = (
            "Pasensya na po, Sir, medyo humina po ang linya. Tungkol po ba ito sa inyong premium payment o gusto niyo po bang "
            "mag-inquire tungkol sa inyong policy riders?"
        )
        return {"response": response, "stage": stage}
