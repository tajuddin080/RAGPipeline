TEST_CASES = [
    {
        "id": "E1",
        "difficulty": "Easy",
        "source": "financial_policy.txt",
        "question": "What is the maximum reimbursement for a domestic flight?",
        "expected_output": "The maximum domestic flight reimbursement is INR 25,000.",
    },
    {
        "id": "E2",
        "difficulty": "Easy",
        "source": "financial_policy.txt",
        "question": "Within how much time must a lost company device be reported?",
        "expected_output": "A lost company device must be reported within two hours.",
    },
    {
        "id": "E3",
        "difficulty": "Easy",
        "source": "hr_policy.md",
        "question": "How many goals should an employee set during each review cycle?",
        "expected_output": "Employees should set a minimum of 3 and a maximum of 7 goals per review cycle.",
    },
    {
        "id": "E4",
        "difficulty": "Easy",
        "source": "hr_policy.md",
        "question": "How soon must HR acknowledge receipt of a grievance?",
        "expected_output": "HR must acknowledge receipt of a grievance within 2 working days.",
    },
    {
        "id": "E5",
        "difficulty": "Easy",
        "source": "onboarding_policy.pdf",
        "question": "At least how long before a new employee joins must their onboarding buddy be assigned?",
        "expected_output": "The onboarding buddy must be assigned at least 5 business days before the employee's joining date.",
    },
    {
        "id": "E6",
        "difficulty": "Easy",
        "source": "resignation_policy.pdf",
        "question": "What is the standard employee notice period for a Grade G4 employee?",
        "expected_output": "The standard employee notice period for Grade G4 is 60 days.",
    },
    {
        "id": "M1",
        "difficulty": "Medium",
        "source": "financial_policy.txt",
        "question": "Who must approve vendor invoices below INR 50,000, from INR 50,000 through INR 2,00,000, and above INR 2,00,000?",
        "expected_output": (
            "Invoices below INR 50,000 require Department Manager approval. "
            "Invoices from INR 50,000 through INR 2,00,000 require Finance Manager approval. "
            "Invoices above INR 2,00,000 require CFO approval."
        ),
    },
    {
        "id": "M2",
        "difficulty": "Medium",
        "source": "financial_policy.txt",
        "question": "What are the weekly remote-work allowance and approval requirements for a request exceeding three consecutive weeks?",
        "expected_output": (
            "Employees may work remotely up to three days per week with manager approval. "
            "A request exceeding three consecutive weeks requires HR Director approval."
        ),
    },
    {
        "id": "M3",
        "difficulty": "Medium",
        "source": "hr_policy.md",
        "question": "How are employees in grades G1-G3 compensated for overtime, and what do employees in G4 and above receive instead?",
        "expected_output": (
            "Employees in G1-G3 receive overtime pay at 1.5 times their hourly rate for hours beyond 48 per week. "
            "Employees in G4 and above are exempt from overtime pay and receive compensatory time off with manager approval."
        ),
    },
    {
        "id": "M4",
        "difficulty": "Medium",
        "source": "hr_policy.md",
        "question": "When are the mid-year and annual performance review outcomes communicated?",
        "expected_output": (
            "Mid-year review outcomes are communicated by July 15. "
            "Annual review outcomes are communicated by January 20."
        ),
    },
    {
        "id": "M5",
        "difficulty": "Medium",
        "source": "onboarding_policy.pdf",
        "question": "How often is New Employee Orientation held, how long is it, and who facilitates it?",
        "expected_output": (
            "New Employee Orientation is a 2-hour group session held every Monday morning "
            "and facilitated by HR."
        ),
    },
    {
        "id": "M6",
        "difficulty": "Medium",
        "source": "resignation_policy.pdf",
        "question": "Within what period may an employee request to withdraw a resignation, and whose approval is required?",
        "expected_output": (
            "An employee may request withdrawal within 3 business days of submission, "
            "subject to management and HR approval."
        ),
    },
    {
        "id": "H1",
        "difficulty": "Hard",
        "source": "financial_policy.txt",
        "question": "What are the procurement approval thresholds, and when are competitive quotations mandatory?",
        "expected_output": (
            "Team Leads may approve purchases below INR 25,000. Purchases from INR 25,000 "
            "through INR 1,00,000 require Procurement Manager approval, and purchases above "
            "INR 1,00,000 require Procurement Director approval. Competitive quotations are "
            "mandatory for purchases above INR 50,000."
        ),
    },
    {
        "id": "H2",
        "difficulty": "Hard",
        "source": "hr_policy.md",
        "question": "What are the maternity-leave eligibility and durations for the first two children versus later children, and what nursing break is provided?",
        "expected_output": (
            "Maternity leave eligibility requires 80 days of work in the preceding 12 months. "
            "Eligible employees receive 26 fully paid weeks for the first and second child, "
            "and 12 weeks from the third child onward. A nursing break of two 15-minute periods "
            "per day is provided until the child turns 15 months."
        ),
    },
    {
        "id": "H3",
        "difficulty": "Hard",
        "source": "financial_policy.txt",
        "question": "What are the acknowledgement deadlines for critical and high-priority incidents, and when is the RCA due?",
        "expected_output": (
            "Critical incidents must be acknowledged within 15 minutes, high-priority incidents "
            "within 30 minutes, and the Root Cause Analysis document must be completed within "
            "5 business days."
        ),
    },
    {
        "id": "H4",
        "difficulty": "Hard",
        "source": "onboarding_policy.pdf",
        "question": "How long is probation, which grades are exempt, and what limits apply to an extension?",
        "expected_output": (
            "Probation lasts 90 calendar days for new employees, except employees joining at "
            "Grade G5 or above, who have no probation period. Probation may be extended only "
            "once, for a maximum of 30 additional days, and the employee must be informed at "
            "least 10 business days before the original probation end date."
        ),
    },
    {
        "id": "H5",
        "difficulty": "Hard",
        "source": "resignation_policy.pdf",
        "question": "List the standard employee notice periods for G1-G2, G3, G4, and G5-G6, including probation, and explain how a longer contract notice period is treated.",
        "expected_output": (
            "The employee notice periods are 30 days for G1-G2, 45 days for G3, 60 days "
            "for G4, and 90 days for G5-G6. During probation, the period is 7 days for any "
            "grade. An employment contract may set a longer notice period, but not a shorter one."
        ),
    },
    {
        "id": "H6",
        "difficulty": "Hard",
        "source": "hr_policy.md",
        "question": "Give the grievance process deadlines for acknowledgement, initial review, investigation, resolution, and appeal.",
        "expected_output": (
            "HR acknowledges receipt within 2 working days, completes the initial review within "
            "5 working days, investigates within 15 working days, and communicates the resolution "
            "within 20 working days. The employee may appeal within 5 days of the decision."
        ),
    },
    {
        "id": "B1",
        "difficulty": "Bonus",
        "source": "onboarding_policy.pdf",
        "question": "Return a Markdown table showing the lead times for configuring a laptop, creating a corporate email ID, issuing an access badge, and creating the Payroll profile.",
        "expected_output": (
            "| Item | Lead time required |\n"
            "|---|---|\n"
            "| Laptop / Desktop configured | 7 business days |\n"
            "| Corporate email ID created | 5 business days |\n"
            "| Access badge / building pass | 3 business days |\n"
            "| Payroll profile created | 7 business days |"
        ),
    },
    {
        "id": "B2",
        "difficulty": "Bonus",
        "source": "financial_policy.txt",
        "question": "List the travel reimbursement caps for domestic flights, international flights, hotels, meals, and taxis, and state the late-claim rule.",
        "expected_output": (
            "The caps are INR 25,000 for domestic flights, INR 1,50,000 for international "
            "flights, INR 8,000 per hotel night, INR 2,000 per day for meals, and INR 3,000 "
            "per taxi trip. Expense claims submitted after 30 calendar days are automatically rejected."
        ),
    },
]
