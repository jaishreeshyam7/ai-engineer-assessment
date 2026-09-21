"""
Question 3: Native-Language Voice Bots - Indonesia Multifinance Bot
Handles consumer finance, motorcycle/auto installment reminders, restructuring,
and regional speech (Javanese polite register + Jakarta colloquial slang).
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class IDLocalizationExample(BaseModel):
    scenario: str
    literal_translation: str
    localized_bahasa: str
    cultural_rationale: str

ID_LOCALIZATION_SHOWCASE = [
    IDLocalizationExample(
        scenario="Installment due reminder with grace period notice",
        literal_translation="Uang angsuran bulanan Anda jatuh tanggal kedaluwarsa hari ini, harap bayar sebelum dikenakan denda pelanggaran.",
        localized_bahasa="Selamat siang, Pak Budi. Mengingatkan kembali untuk angsuran pembiayaan motor Honda Vario dengan nomor kontrak 8820, jatuh tempo pada tanggal 25 ini sebesar Rp 850.000 ya, Pak, agar tidak terkena denda keterlambatan.",
        cultural_rationale="Literal translation ('tanggal kedaluwarsa', 'denda pelanggaran') uses clumsy expired-food vocabulary. Standard Indonesian multifinance uses 'jatuh tempo', 'angsuran pembiayaan', 'nomor kontrak', and polite sentence-ending particles ('ya, Pak')."
    ),
    IDLocalizationExample(
        scenario="Handling borrower cash flow difficulties and offering restructuring/tenor extension",
        literal_translation="Jika Anda tidak punya uang tunai, kami akan menyita kendaraan bermotor Anda.",
        localized_bahasa="Kami memahami kondisi Bapak. Kalau saat ini perputaran usaha sedang seret, kami ada program keringanan angsuran atau perpanjangan tenor cicilan agar beban bulanan lebih ringan. Apakah berkenan kami bantu ajukan ke tim pembiayaan?",
        cultural_rationale="In Indonesian consumer finance, aggressive threats cause immediate call abandonment and default hiding. Empathetic negotiation ('kondisi sedang seret', 'keringanan angsuran', 'perpanjangan tenor') maintains connection and yields higher collection recovery."
    ),
    IDLocalizationExample(
        scenario="Regional Javanese polite greeting and loan terms",
        literal_translation="Halo laki-laki, berapa uang muka dan bunga pinjaman Anda?",
        localized_bahasa="Nyuwun sewu, Mas Bambang. Menawi badhe ngecek sisa cicilan kalian denda, angsuranipun sampun mlebet sistem nggih. Monggo saget dipun bayar lewat Alfamart utawi transfer BCA Virtual Account.",
        cultural_rationale="When engaging callers outside Jakarta (Central/East Java, Yogyakarta), addressing borrowers as 'Mas' with Javanese polite honorifics ('nyuwun sewu', 'nggih', 'monggo') establishes instant trust and respect compared to stiff automated Jakarta Indonesian."
    )
]

class IndonesiaVoiceBot:
    """
    Bahasa Indonesia Multifinance & Consumer Credit Bot:
    - Sector: Multifinance (Motorcycle / Car / Gadget installment).
    - Dual register: Standard/Colloquial Indonesian + Regional Javanese accent adaptation.
    - Natural finance vocabulary: cicilan, tenor, denda, DP, jatuh tempo, angsuran, pembiayaan.
    """

    FINANCE_TERMS = ["cicilan", "tenor", "denda", "dp", "jatuh tempo", "angsuran", "pembiayaan", "virtual account"]

    def __init__(self):
        self.market = "Indonesia"
        self.sector = "Multifinance & Consumer Credit"
        self.language = "Bahasa Indonesia (Formal & Colloquial + Javanese Regional Tone)"

    def process_turn(self, state: dict, user_text: str) -> dict:
        text_lower = user_text.lower()
        turn_count = state.get("turn_count", 0) + 1
        state["turn_count"] = turn_count

        # Check regional accent / register cues
        is_javanese_accent = any(w in text_lower for w in ["nyuwun sewu", "nggih", "mas", "monggo", "matur nuwun", "mboten", "sampun"])
        if is_javanese_accent:
            state["register"] = "JAVANESE_POLITE"

        # Check for Human Escalation
        if any(w in text_lower for w in ["orang", "manusia", "petugas", "supervisor", "cs", "operator", "ngomong sama orang"]):
            if state.get("register") == "JAVANESE_POLITE":
                response = (
                    "Nggih Mas, mangga dipun antosi sekedap. Kula sambungaken langsung dateng Petugas Customer Service "
                    "pembiayaan ingkang tugas dinten niki supados saget dipun bantu tuntas. Matur nuwun nggih."
                )
            else:
                response = (
                    "Baik, Pak/Ibu. Segera saya sambungkan ke Petugas Layanan Konsumen (Customer Service) "
                    "tim pembiayaan kami untuk penanganan langsung. Mohon tetap di telepon ya, terima kasih."
                )
            return {
                "response": response,
                "action": "ESCALATE_ID",
                "escalated": True,
                "register": state.get("register", "STANDARD")
            }

        # Flow State Handling
        stage = state.get("stage", "GREETING")

        if stage == "GREETING":
            state["stage"] = "VERIFY_IDENTITY"
            if state.get("register") == "JAVANESE_POLITE":
                response = (
                    "Sugeng siang Mas Bambang. Nyuwun sewu, kulo saking layanan pembiayaan Astra Multifinance. "
                    "Leres niki kalian Mas Bambang Sutrisno ingkang mundhut unit motor Beat?"
                )
            else:
                response = (
                    "Selamat siang, perkenalkan saya dari Customer Support Multifinance Nusantara. "
                    "Apakah benar saya terhubung dengan Bapak Budi Prasetyo?"
                )
            return {"response": response, "stage": state["stage"]}

        if stage == "VERIFY_IDENTITY":
            state["stage"] = "DELIVER_INSTALLMENT_INFO"
            if state.get("register") == "JAVANESE_POLITE":
                response = (
                    "Matur nuwun Mas Bambang. Namung ngemutaken kagem angsuran cicilan motor ing wulan niki "
                    "sebesar Rp 750.000 sampun nyaketi tanggal jatuh tempo tanggal 25 nggih Mas, supados mboten kenging denda."
                )
            else:
                response = (
                    "Terima kasih, Pak Budi. Kami ingin menginfokan bahwa cicilan angsuran ke-8 pembiayaan motor "
                    "sebesar Rp 820.000 akan jatuh tempo pada tanggal 25 bulan ini. Apakah sudah ada rencana pembayaran?"
                )
            return {"response": response, "stage": state["stage"]}

        if stage == "DELIVER_INSTALLMENT_INFO":
            # Check for financial difficulties / objection / restructuring request
            if any(w in text_lower for w in ["berat", "seret", "denda", "keringanan", "tenor", "mundur", "telat", "gaji", "gak ada duit"]):
                state["stage"] = "OFFER_RESTRUCTURING"
                if state.get("register") == "JAVANESE_POLITE":
                    response = (
                        "Kula mangertosi sanget kondisinipun Mas Bambang. Mboten usah kuwatos, wonten program pemutihan denda "
                        "utawi perpanjangan tenor cicilan supados angsuran saben wulan langkung enteng. Menawi badhe dipun ajuaken, kula bantu proses nggih Mas?"
                    )
                else:
                    response = (
                        "Kami sangat memahami kondisi Bapak Budi. Jangan khawatir, untuk keterlambatan beberapa hari "
                        "ada masa tenggang, dan kami juga memiliki opsi restrukturisasi perpanjangan tenor cicilan agar angsuran per bulan lebih terjangkau. Apakah ingin kami bantu pengajuannya?"
                    )
                return {"response": response, "stage": state["stage"], "objection_handled": True}
            
            # Check for payment channel inquiry
            elif any(w in text_lower for w in ["bayar", "transfer", "cara", "rekening", "va", "alfamart", "indomaret"]):
                state["stage"] = "PAYMENT_METHOD"
                response = (
                    "Untuk pembayaran sangat mudah, Pak. Bisa melalui transfer BCA Virtual Account dengan nomor kontrak Bapak, "
                    "atau langsung lewat kasir Indomaret dan Alfamart terdekat. Apakah ingin kami kirimkan SMS kode pembayarannya?"
                )
                return {"response": response, "stage": state["stage"]}
            else:
                state["stage"] = "PAYMENT_CONFIRMATION"
                response = (
                    "Baik Pak Budi, terima kasih banyak atas konfirmasinya. Pembayaran bisa dilakukan sebelum jam 12 malam tanggal jatuh tempo. "
                    "Ada hal lain terkait pembiayaan yang bisa kami bantu?"
                )
                return {"response": response, "stage": state["stage"]}

        if stage in ["OFFER_RESTRUCTURING", "PAYMENT_METHOD", "PAYMENT_CONFIRMATION"]:
            state["stage"] = "CLOSING"
            if state.get("register") == "JAVANESE_POLITE":
                response = (
                    "Matur nuwun sanget Mas Bambang kagem wekdalipun. Informasi rincian cicilan sampun kula kirim lewat SMS. "
                    "Sugeng siang lan mugi-mugi rejekinipun lancar sedaya nggih Mas."
                )
            else:
                response = (
                    "Terima kasih banyak atas waktu dan kerjasamanya, Pak Budi. SMS konfirmasi dan nomor Virtual Account "
                    "sudah kami kirimkan ke nomor ponsel Bapak. Selamat siang dan sukses selalu."
                )
            return {"response": response, "stage": state["stage"], "completed": True}

        # Natural Indonesian fallback
        response = (
            "Mohon maaf Pak, suaranya sempat terputus sebentar. Apakah Bapak ingin menanyakan perihal nomor Virtual Account cicilan, "
            "atau opsi keringanan tenor angsuran?"
        )
        return {"response": response, "stage": stage}
