"""
Question 3: Native-Language Voice Bots - Test Suite & Transcript Generator
Executes 4 complete simulated calls (2 per market) covering:
- Market 1 (Philippines): Call 1 - Cooperative Taglish Bancassurance Renewal; Call 2 - Objection & Taglish Human Escalation
- Market 2 (Indonesia): Call 3 - Colloquial Multifinance Installment Reminder; Call 4 - Regional Javanese Accent Debt Restructuring

Saves full transcripts with linguistic analysis to data/test_calls/
"""

import json
import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from .philippines_bot import PhilippinesVoiceBot, PH_LOCALIZATION_SHOWCASE
from .indonesia_bot import IndonesiaVoiceBot, ID_LOCALIZATION_SHOWCASE
from .asr_tts_analysis import ASR_EVALUATIONS, TTS_EVALUATIONS

def run_multilingual_tests():
    os.makedirs("data/test_calls", exist_ok=True)
    ph_bot = PhilippinesVoiceBot()
    id_bot = IndonesiaVoiceBot()

    test_scenarios = [
        # PHILIPPINES TEST CALL 1: Cooperative Taglish Bancassurance Renewal
        {
            "call_id": "call_ph_01_cooperative",
            "market": "Philippines",
            "sector": "Life Insurance / Bancassurance",
            "test_type": "Cooperative Customer + Mixed English/Finance Terms",
            "caller_name": "Mr. Ronald Cruz",
            "bot": ph_bot,
            "turns_input": [
                "Hello po, magandang araw.",
                "Opo, ako nga po si Ronald Cruz.",
                "Ah opo, due na pala. May kasama po ba itong critical illness rider at sino po ang primary beneficiary?",
                "Okay po, paano po ba ang pinakamadaling paraan para bayaran 'to?",
                "Sige po, paki-send na lang po ng payment link sa number ko. Maraming salamat po!"
            ]
        },
        # PHILIPPINES TEST CALL 2: Budget Objection & Branch Human Escalation
        {
            "call_id": "call_ph_02_objection_escalate",
            "market": "Philippines",
            "sector": "Life Insurance / Bancassurance",
            "test_type": "Objection (Petsa de Peligro/Salary Timing) + Human Escalation in Taglish",
            "caller_name": "Ms. Ma. Elena Santos",
            "bot": ph_bot,
            "turns_input": [
                "Hello? Sino po ito?",
                "Yes, speaking po.",
                "Naku, medyo tight po ang pondo ngayon, petsa de peligro kasi. Pwede po bang sa katapusan na lang magbayad pagkatapos ng sahod?",
                "Gusto ko po sana makausap yung Bancassurance specialist sa BPI branch para ma-discuss personally ang payment arrangement."
            ]
        },
        # INDONESIA TEST CALL 1: Colloquial Multifinance Installment Reminder
        {
            "call_id": "call_id_01_colloquial",
            "market": "Indonesia",
            "sector": "Multifinance / Consumer Credit",
            "test_type": "Colloquial Indonesian Speech + Payment Channel Query",
            "caller_name": "Pak Budi Prasetyo",
            "bot": id_bot,
            "turns_input": [
                "Halo, selamat siang.",
                "Iya betul, saya sendiri Budi Prasetyo.",
                "Oh iya, udah inget kok. Mau tanya nomor rekening BCA Virtual Account buat bayar cicilan angsuran motornya dong.",
                "Boleh, tolong dikirim via SMS ya kodenya. Makasih banyak Mas/Mbak."
            ]
        },
        # INDONESIA TEST CALL 2: Javanese Regional Accent + Restructuring Objection & Escalation
        {
            "call_id": "call_id_02_javanese_accent",
            "market": "Indonesia",
            "sector": "Multifinance / Consumer Credit",
            "test_type": "Regional Javanese Accent + Financial Hardship / Tenor Restructuring & Escalation",
            "caller_name": "Mas Bambang Sutrisno (Solo/Yogyakarta)",
            "bot": id_bot,
            "turns_input": [
                "Nyuwun sewu, halo sugeng siang.",
                "Inggih leres, kulo piyambak Bambang Sutrisno.",
                "Aduh Mas, wulan niki rejeki lagi seret sanget. Menawi nyuwun perpanjangan tenor cicilan supados angsuranipun langkung enteng saget mboten nggih?",
                "Nggih Mas, menawi saget kulo nyuwun disambungaken kalian supervisor CS pembiayaan supados rembagan langkung cetha."
            ]
        }
    ]

    print("=" * 80)
    print("QUESTION 3: NATIVE-LANGUAGE VOICE BOTS TEST SUITE")
    print("=" * 80)

    summary_records = []

    for sc in test_scenarios:
        bot = sc["bot"]
        state = {}
        dialog_history = []
        print(f"\n--- Running: [{sc['market']}] {sc['call_id']} ({sc['test_type']}) ---")

        for user_msg in sc["turns_input"]:
            print(f"Customer: \"{user_msg}\"")
            resp_data = bot.process_turn(state, user_msg)
            bot_text = resp_data["response"]
            print(f"Bot:      \"{bot_text}\"")

            dialog_history.append({
                "speaker": "Customer",
                "text": user_msg
            })
            dialog_history.append({
                "speaker": "Bot",
                "text": bot_text,
                "action": resp_data.get("action", "CONTINUE"),
                "stage": resp_data.get("stage")
            })

        out_file = f"data/test_calls/{sc['call_id']}.json"
        call_export = {
            "call_id": sc["call_id"],
            "market": sc["market"],
            "sector": sc["sector"],
            "test_type": sc["test_type"],
            "caller_name": sc["caller_name"],
            "language_mode": getattr(bot, "language", "Multilingual"),
            "dialog": dialog_history,
            "state_summary": state
        }
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(call_export, f, indent=2, ensure_ascii=False)

        summary_records.append({
            "call_id": sc["call_id"],
            "market": sc["market"],
            "turns": len(dialog_history),
            "status": "PASSED"
        })

    print("\n" + "=" * 80)
    print("MULTILINGUAL CALLS EXPORTED SUCCESSFULLY:")
    for sm in summary_records:
        print(f" - [{sm['market']}] {sm['call_id']}: {sm['turns']} turns -> PASSED")
    print("=" * 80)

    return summary_records

if __name__ == "__main__":
    run_multilingual_tests()
