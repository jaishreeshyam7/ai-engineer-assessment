"""
Question 2: Production-Ready Knowledge Base - Raw Business Corpus
Contains realistic raw business inputs (including web scrape boilerplate, PII,
duplicate entries, and qualification rule tables) representing Health Insurance & Lead Underwriting.
"""

RAW_BUSINESS_DOCUMENTS = [
    {
        "id": "raw_doc_001",
        "title": "Prime Care Health Shield - Product Specifications",
        "source": "https://company.example.com/products/prime-care-health-shield",
        "category": "product",
        "raw_text": """
        Skip to main content | Navigation Menu: Home About Products Contact
        Prime Care Health Shield provides comprehensive family and individual health coverage.
        Sum Insured options range from $50,000 to $1,000,000.
        Key Benefits:
        - 100% Cashless hospitalization across 12,500+ network hospitals.
        - 24-hour claim pre-authorization support.
        - Pre-hospitalization expenses covered up to 60 days before admission.
        - Post-hospitalization medical expenses covered up to 180 days after discharge.
        - 540+ Daycare procedures included (surgeries requiring < 24 hrs hospitalization).
        - Annual preventive health check-up voucher included for all insured adults.
        - Cumulative No-Claim Discount: 10% increase in sum insured for every claim-free year, up to a maximum of 50%.
        Cookie policy: We use cookies to enhance your experience. Accept all cookies.
        All rights reserved. Copyright 2026 HealthGuard Inc.
        """,
        "version": "1.2"
    },
    {
        "id": "raw_doc_002",
        "title": "Underwriting Qualification & Eligibility Guidelines",
        "source": "internal_policy_doc_v2.pdf",
        "category": "qualification",
        "raw_text": """
        CONFIDENTIAL - INTERNAL UNDERWRITING RULES
        Applicant Qualification Criteria:
        1. Age Bracket: Minimum entry age is 18 years; maximum entry age for new enrollment is 65 years. Children aged 91 days to 25 years can be included as dependents.
        2. Geographic Scope: Available to all legal residents of eligible states and provinces.
        3. Medical Underwriting:
           - Applicants with controlled hypertension or controlled Type-2 diabetes are eligible subject to a standard 15% premium loading and underwriting review.
           - Automatic Disqualifications: Applicants currently undergoing active chemotherapy, renal dialysis, or organ transplant surgery are not eligible for automated lead qualification; must be referred to high-risk specialist underwriting.
           - Tele-medical screening is mandatory for applicants aged 55 and above.
        4. Smoker Classification: Non-smokers receive a preferred 12% discount. Nicotine users must disclose usage.
        For internal inquiries contact compliance officer john.smith@healthguard.internal or phone (555) 019-2834.
        """,
        "version": "2.0"
    },
    {
        "id": "raw_doc_003",
        "title": "Policy Exclusions & Waiting Periods",
        "source": "policy_wording_terms_2026.pdf",
        "category": "policy",
        "raw_text": """
        Terms of Service | Privacy Policy | Contact Us
        Policy Wording Section 4: Waiting Periods and Exclusions
        1. Initial Waiting Period: A strict 30-day waiting period applies from policy commencement, during which claims for any illness or disease are not covered, except for accidental injuries which are covered from Day 1.
        2. Pre-Existing Conditions Waiting Period: A mandatory 24-month continuous coverage waiting period applies to declared pre-existing diseases (e.g. asthma, hypertension, arthritis).
        3. Specific Named Ailments: Cataract, hernia, joint replacement, and kidney stones have a 24-month specific waiting period.
        4. Permanent Exclusions: Elective cosmetic surgery, experimental stem-cell therapies, self-inflicted injuries, and non-prescription vitamins are permanently excluded.
        5. Copayment: A standard 10% copayment applies for insured members aged 61 and above at the time of claim. Zero copayment for members under 60.
        All rights reserved. Copyright 2026.
        """,
        "version": "2.1"
    },
    {
        "id": "raw_doc_004",
        "title": "Customer FAQs - Claims, Billing, and Cancellations",
        "source": "https://company.example.com/faqs",
        "category": "faq",
        "raw_text": """
        Navigation menu: Home FAQs Support
        Q: How does cashless claims processing work at network hospitals?
        A: Present your HealthGuard digital health card and government ID at the hospital's TPA / insurance helpdesk. Pre-authorization is approved within 60 minutes for planned admissions and within 30 minutes for emergency admissions.

        Q: What is the Free-Look cancellation period?
        A: Policyholders are granted a 15-day free-look period from the date of policy document receipt. If unsatisfied, the policy can be cancelled for a full refund minus stamp duty and proportionate risk premium.

        Q: Can I pay premiums in monthly installments?
        A: Yes, premiums can be paid annually, semi-annually, quarterly, or via monthly auto-debit (ACH/credit card).
        Sample test customer record: Customer ID: Jane Doe, SSN: 123-45-6789, Card: 4111-2222-3333-4444.
        """,
        "version": "1.0"
    },
    {
        "id": "raw_doc_005",
        "title": "Objection Handling: Existing Employer Insurance & Cost Concerns",
        "source": "sales_enablement_playbook_2026.pdf",
        "category": "objection",
        "raw_text": """
        SALES PLAYBOOK - HANDLING COMMON CUSTOMER OBJECTIONS
        Objection 1: "I already have health insurance through my employer/company."
        Response Strategy:
        - Validate: Acknowledge that employer group insurance is a great perk.
        - Risk Highlight: Explain that employer coverage is tied to employment. If you change jobs, get laid off, or retire, coverage terminates immediately, leaving you uninsured when older and harder to insure.
        - Solution: A dedicated personal policy or super top-up locks in entry age pricing, provides continuous no-claim bonus, and stays active regardless of career transitions.

        Objection 2: "Health insurance is too expensive / not in my budget right now."
        Response Strategy:
        - Break down the cost: Explain that a $250,000 family cover equates to approximately $3.50 a day.
        - Cost-saving options: Highlight high-deductible options (e.g. $1,000 deductible lowers premium by 35%), and mention monthly installment payments to avoid lump-sum financial strain.
        - High medical inflation: Without cover, a single ICU admission or cardiac procedure averages $25,000+, risking personal savings.
        """,
        "version": "1.1"
    },
    {
        "id": "raw_doc_006",
        "title": "Branch Partnership Benefits",
        "source": "website section",
        "category": "partnership_benefits",
        "raw_text": """
        Operational, marketing, and technology support is provided to branch partners.
        Our enterprise partner portal enables real-time quotation generation, instant policy issuance,
        automated commission settlements, and co-branded marketing assets for regional distribution agencies.
        """,
        "version": "1.0"
    },
    # Duplicate doc to test deduplication
    {
        "id": "raw_doc_007_duplicate",
        "title": "Branch Partnership Benefits (Duplicate Scrape)",
        "source": "website section duplicate mirror",
        "category": "partnership_benefits",
        "raw_text": """
        Skip to main content
        Operational, marketing, and technology support is provided to branch partners.
        Our enterprise partner portal enables real-time quotation generation, instant policy issuance,
        automated commission settlements, and co-branded marketing assets for regional distribution agencies.
        Cookie policy: accept all cookies.
        """,
        "version": "1.0"
    }
]
