"""
SmartEdMatch — Faculty, Course, JAMB & WAEC Data
Central reference for all academic data used across the app
"""

# ── Faculty → Courses mapping ─────────────────────────────────────────────────
FACULTY_COURSES = {
    "Sciences": [
        "Computer Science", "Information Technology", "Mathematics",
        "Statistics", "Physics", "Chemistry", "Biology", "Biochemistry",
        "Microbiology", "Geology", "Zoology", "Botany", "Industrial Chemistry",
        "Marine Biology", "Environmental Science", "Data Science",
    ],
    "Engineering": [
        "Engineering (Electrical)", "Engineering (Civil)", "Engineering (Mechanical)",
        "Engineering (Chemical)", "Petroleum Engineering", "Engineering (Computer)",
        "Engineering (Agricultural)", "Engineering (Aerospace)", "Engineering (Mechatronics)",
        "Engineering (Marine)", "Engineering (Production)", "Engineering (Systems)",
        "Electrical Engineering", "Mechanical Engineering",
    ],
    "Medical Sciences": [
        "Medicine and Surgery", "Nursing Science", "Pharmacy", "Dentistry",
        "Medical Laboratory Science", "Physiotherapy", "Radiology",
        "Public Health", "Anatomy", "Physiology", "Optometry", "Nutrition and Dietetics",
    ],
    "Law": [
        "Law",
    ],
    "Management Sciences": [
        "Accounting", "Business Administration", "Banking and Finance",
        "Economics", "Marketing", "Insurance", "Entrepreneurship",
        "Accountancy", "Finance", "Management", "Public Administration",
        "Cooperative Economics", "Actuarial Science",
    ],
    "Social Sciences": [
        "Mass Communication", "Psychology", "Sociology", "Political Science",
        "International Relations", "Social Work", "Criminology",
        "Journalism", "Public Relations", "Demography", "Geography",
    ],
    "Arts & Humanities": [
        "English Language", "History", "Linguistics", "Philosophy",
        "Theatre Arts", "Music", "Christian Religious Studies",
        "Islamic Studies", "French", "Arabic", "Yoruba", "Igbo", "Hausa",
        "Fine Art", "Creative Arts",
    ],
    "Education": [
        "Computer Science Education", "Mathematics Education", "Biology Education",
        "Physics Education", "Chemistry Education", "English Education",
        "Social Studies Education", "Special Education", "Guidance and Counselling",
        "Educational Management", "Physical Education", "Technical Education",
        "Agricultural Education", "Business Education",
    ],
    "Agriculture": [
        "Agricultural Science", "Animal Science", "Crop Science",
        "Agricultural Economics", "Forestry", "Fisheries",
        "Food Science and Technology", "Soil Science", "Agricultural Engineering",
        "Home Economics", "Agricultural Extension",
    ],
    "Environmental Sciences": [
        "Architecture", "Urban and Regional Planning", "Estate Management",
        "Quantity Surveying", "Building", "Fine Arts", "Interior Design",
        "Industrial Design", "Landscape Architecture",
    ],
    "Pharmacy": [
        "Pharmacy",
    ],
}

# ── JAMB subject requirements per course ─────────────────────────────────────
# Format: [Use of English (compulsory) + 3 other subjects]
JAMB_SUBJECTS = {
    "Computer Science": ["Use of English", "Mathematics", "Physics", "Any of Chemistry/Biology/Further Maths/Economics"],
    "Information Technology": ["Use of English", "Mathematics", "Physics", "Any of Chemistry/Biology/Further Maths/Economics"],
    "Mathematics": ["Use of English", "Mathematics", "Further Mathematics", "Any of Physics/Chemistry/Economics"],
    "Statistics": ["Use of English", "Mathematics", "Physics or Chemistry", "Any of Biology/Economics/Further Maths"],
    "Physics": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Chemistry": ["Use of English", "Mathematics", "Chemistry", "Physics or Biology"],
    "Biology": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Biochemistry": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Microbiology": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Geology": ["Use of English", "Mathematics", "Physics", "Chemistry or Geography"],
    "Zoology": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Botany": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Industrial Chemistry": ["Use of English", "Chemistry", "Mathematics", "Physics or Biology"],
    "Marine Biology": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Environmental Science": ["Use of English", "Biology or Geography", "Chemistry", "Physics or Mathematics"],
    "Data Science": ["Use of English", "Mathematics", "Physics", "Statistics or Economics"],
    "Engineering (Electrical)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Engineering (Civil)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Engineering (Mechanical)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Engineering (Chemical)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Petroleum Engineering": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Engineering (Computer)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Engineering (Agricultural)": ["Use of English", "Mathematics", "Physics", "Chemistry or Biology"],
    "Engineering (Aerospace)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Engineering (Mechatronics)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Engineering (Marine)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Engineering (Production)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Engineering (Systems)": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Electrical Engineering": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Mechanical Engineering": ["Use of English", "Mathematics", "Physics", "Chemistry"],
    "Medicine and Surgery": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Nursing Science": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Pharmacy": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Dentistry": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Medical Laboratory Science": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Physiotherapy": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Radiology": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Public Health": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Anatomy": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Physiology": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Optometry": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Nutrition and Dietetics": ["Use of English", "Biology", "Chemistry", "Physics or Home Economics"],
    "Law": ["Use of English", "Literature in English", "Any two of: CRK/IRK/History/Government/Economics/French"],
    "Accounting": ["Use of English", "Mathematics", "Economics", "Any of Commerce/Government/Geography"],
    "Business Administration": ["Use of English", "Mathematics", "Economics", "Any of Commerce/Government/Geography"],
    "Banking and Finance": ["Use of English", "Mathematics", "Economics", "Any of Commerce/Government/Geography"],
    "Economics": ["Use of English", "Mathematics", "Economics", "Any of Government/Commerce/Geography/Statistics"],
    "Marketing": ["Use of English", "Mathematics", "Economics", "Any of Commerce/Government/Geography"],
    "Insurance": ["Use of English", "Mathematics", "Economics", "Any of Commerce/Government/Geography"],
    "Entrepreneurship": ["Use of English", "Mathematics", "Economics", "Any of Commerce/Government/Geography"],
    "Accountancy": ["Use of English", "Mathematics", "Economics", "Any of Commerce/Government/Geography"],
    "Finance": ["Use of English", "Mathematics", "Economics", "Any of Commerce/Government/Geography"],
    "Management": ["Use of English", "Mathematics", "Economics", "Any of Commerce/Government/Geography"],
    "Public Administration": ["Use of English", "Government", "Economics or Mathematics", "Any other subject"],
    "Actuarial Science": ["Use of English", "Mathematics", "Further Mathematics", "Economics or Statistics"],
    "Mass Communication": ["Use of English", "Literature in English or Government", "Economics or CRK", "Any other subject"],
    "Psychology": ["Use of English", "Biology", "Economics or Government", "Any other subject"],
    "Sociology": ["Use of English", "Government", "Economics", "Any other subject"],
    "Political Science": ["Use of English", "Government", "Economics", "History or CRK"],
    "International Relations": ["Use of English", "Government", "Economics", "History or Geography"],
    "Social Work": ["Use of English", "Government or Sociology", "Economics", "Any other subject"],
    "Criminology": ["Use of English", "Government", "Economics", "Any other subject"],
    "Journalism": ["Use of English", "Literature in English", "Government or History", "Any other subject"],
    "Geography": ["Use of English", "Geography", "Mathematics", "Economics or Biology"],
    "English Language": ["Use of English", "Literature in English", "Any two arts or social science subjects"],
    "History": ["Use of English", "History", "Government", "Any of Literature/CRK/IRK"],
    "Linguistics": ["Use of English", "Literature in English", "Any two of: French/Arabic/Yoruba/Igbo/Hausa"],
    "Philosophy": ["Use of English", "Literature in English or Government", "Any two other subjects"],
    "Theatre Arts": ["Use of English", "Literature in English", "Any two of: Arts subjects"],
    "Music": ["Use of English", "Music", "Any two other subjects"],
    "Christian Religious Studies": ["Use of English", "CRK", "Any two other subjects"],
    "Islamic Studies": ["Use of English", "IRK or Arabic", "Any two other subjects"],
    "Fine Art": ["Use of English", "Fine Art", "Any two other subjects"],
    "Computer Science Education": ["Use of English", "Mathematics", "Physics", "Chemistry or Economics"],
    "Mathematics Education": ["Use of English", "Mathematics", "Further Mathematics or Physics", "Any other subject"],
    "Biology Education": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Physics Education": ["Use of English", "Physics", "Mathematics", "Chemistry"],
    "Chemistry Education": ["Use of English", "Chemistry", "Mathematics", "Physics or Biology"],
    "English Education": ["Use of English", "Literature in English", "Any two arts subjects"],
    "Social Studies Education": ["Use of English", "Government", "Economics", "Any other subject"],
    "Special Education": ["Use of English", "Any three relevant subjects"],
    "Agricultural Science": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics or Agricultural Science"],
    "Animal Science": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Crop Science": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Agricultural Economics": ["Use of English", "Economics", "Mathematics", "Biology or Agricultural Science"],
    "Forestry": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Fisheries": ["Use of English", "Biology", "Chemistry", "Physics or Mathematics"],
    "Food Science and Technology": ["Use of English", "Chemistry", "Biology or Agricultural Science", "Mathematics or Physics"],
    "Architecture": ["Use of English", "Mathematics", "Physics", "Any of Chemistry/Geography/Art"],
    "Urban and Regional Planning": ["Use of English", "Geography", "Mathematics", "Economics or Physics"],
    "Estate Management": ["Use of English", "Mathematics", "Economics", "Geography or Physics"],
    "Quantity Surveying": ["Use of English", "Mathematics", "Physics", "Economics or Chemistry"],
    "Building": ["Use of English", "Mathematics", "Physics", "Chemistry or Economics"],
}

# ── WAEC subject requirements per course ─────────────────────────────────────
WAEC_REQUIREMENTS = {
    "Computer Science": "English Language, Mathematics, Physics, and any 2 of: Chemistry, Biology, Further Mathematics, Economics (minimum 5 credits including Maths & English)",
    "Medicine and Surgery": "English Language, Mathematics, Physics, Chemistry, Biology — all at Credit level (5 credits)",
    "Law": "English Language (Credit), Literature in English (Credit), and 3 other subjects at Credit level",
    "Engineering (Electrical)": "English Language, Mathematics, Physics, Chemistry — all at Credit level",
    "Accounting": "English Language, Mathematics, Economics, and 2 other subjects at Credit level",
    "Pharmacy": "English Language, Biology, Chemistry, Physics, Mathematics — all at Credit level",
    "Nursing Science": "English Language, Biology, Chemistry, Physics or Mathematics — all at Credit level",
    "Economics": "English Language, Mathematics, Economics, and 2 other subjects at Credit level",
    "Mass Communication": "English Language, Literature or Government, and 3 other subjects at Credit level",
    "Agricultural Science": "English Language, Biology/Agricultural Science, Chemistry, Mathematics, and 1 other at Credit level",
    "Architecture": "English Language, Mathematics, Physics, Fine Arts or Technical Drawing, and 1 other at Credit level",
    "Psychology": "English Language, Biology, and 3 other subjects at Credit level",
    "Default": "Minimum of 5 credits in WAEC/NECO including English Language and Mathematics",
}

# ── Simulated campus sentiment scores ────────────────────────────────────────
# In production: pull from Twitter/Facebook/Reddit APIs
# Score: 0-100 (higher = more positive sentiment)
CAMPUS_SENTIMENT = {
    "University of Lagos":              {"score": 72, "highlights": ["Strong academic reputation", "Vibrant student life", "Lagos location advantage"], "concerns": ["Overcrowding", "Some staff strike history"]},
    "University of Ibadan":             {"score": 78, "highlights": ["Best university in Nigeria ranking", "Excellent research output", "Peaceful campus"], "concerns": ["Accommodation scarcity", "Far from city centre"]},
    "Obafemi Awolowo University":       {"score": 74, "highlights": ["Beautiful campus", "Strong law and engineering programs", "Active alumni network"], "concerns": ["Occasional ASUU strikes", "Long semesters"]},
    "University of Nigeria Nsukka":     {"score": 70, "highlights": ["Strong humanities programs", "Good community spirit", "Affordable tuition"], "concerns": ["Infrastructure needs improvement", "Power supply issues"]},
    "Ahmadu Bello University":          {"score": 68, "highlights": ["Largest university in Nigeria", "Strong engineering faculty", "Diverse student body"], "concerns": ["Security concerns in region", "Overcrowded facilities"]},
    "Covenant University":              {"score": 85, "highlights": ["Excellent infrastructure", "Strong discipline and focus", "High graduate employability"], "concerns": ["Very strict rules", "Very high tuition fees", "Limited social freedom"]},
    "Babcock University":               {"score": 80, "highlights": ["Clean and serene campus", "Good medical school", "Strong Christian values"], "concerns": ["High cost of living", "Strict regulations"]},
    "University of Port Harcourt":      {"score": 66, "highlights": ["Strong petroleum engineering", "Good research facilities", "Coastal location"], "concerns": ["Regional security concerns", "Cost of living in PH"]},
    "University of Benin":              {"score": 67, "highlights": ["Strong pharmacy program", "Good law faculty", "Central location"], "concerns": ["Traffic challenges", "Campus congestion"]},
    "University of Ilorin":             {"score": 75, "highlights": ["Good CGPA culture", "Strong medical school", "Peaceful campus"], "concerns": ["Limited nightlife", "Distance from major city"]},
    "Nnamdi Azikiwe University":        {"score": 69, "highlights": ["Good engineering programs", "Active student union", "Affordable"], "concerns": ["Infrastructure challenges", "Strike history"]},
    "Baze University":                  {"score": 82, "highlights": ["Modern facilities", "Small class sizes", "Abuja location"], "concerns": ["Very high tuition", "Still growing reputation"]},
    "Nile University of Nigeria":       {"score": 79, "highlights": ["Good tech programs", "Modern infrastructure", "Abuja location"], "concerns": ["High fees", "Limited social activities"]},
    "Veritas University Abuja":         {"score": 76, "highlights": ["Catholic mission values", "Good law faculty", "Abuja location"], "concerns": ["Still building reputation", "Limited courses"]},
    "Lagos State University":           {"score": 71, "highlights": ["Lagos location advantage", "Affordable state tuition", "Good law school"], "concerns": ["Political interference risk", "Infrastructure varies"]},
    "Default":                          {"score": 65, "highlights": ["Accredited institution", "Qualified faculty", "NUC approved"], "concerns": ["Limited data available", "Visit campus before deciding"]},
}

# ── Monetisation tiers ────────────────────────────────────────────────────────
PLANS = {
    "Free": {
        "price": 0,
        "features": [
            "Up to 5 searches per day",
            "Basic institution recommendations",
            "JAMB subject combination check",
            "View top 5 results only",
        ],
        "locked": [
            "Admission probability score",
            "Campus sentiment analysis",
            "Safe / Balanced / Ambitious categorisation",
            "Unlimited searches",
            "PDF report download",
            "Compare up to 5 institutions",
            "WAEC subject verification",
            "Priority support",
        ]
    },
    "Pro": {
        "price": 2500,
        "period": "per month",
        "features": [
            "Unlimited searches",
            "Full admission probability scores",
            "Campus sentiment & social media insights",
            "Safe / Balanced / Ambitious categorisation",
            "Compare up to 5 institutions",
            "PDF recommendation report",
            "WAEC & JAMB subject verification",
            "Priority customer support",
            "Early access to new features",
        ],
        "locked": []
    },
    "School": {
        "price": 50000,
        "period": "per year",
        "features": [
            "Everything in Pro",
            "Up to 500 student accounts",
            "School counsellor dashboard",
            "Bulk student report generation",
            "Integration with school portal",
            "Dedicated account manager",
        ],
        "locked": []
    }
}

# ── Onboarding questions ──────────────────────────────────────────────────────
ONBOARDING_QUESTIONS = [
    {
        "id": "q1",
        "question": "What best describes where you are right now?",
        "type": "single",
        "options": [
            "I'm in SS3 preparing for JAMB",
            "I've written JAMB and awaiting results",
            "I have my JAMB score and choosing an institution",
            "I was not offered admission and need to reapply",
            "I'm a parent/guardian helping a student",
        ]
    },
    {
        "id": "q2",
        "question": "What is your biggest challenge right now?",
        "type": "single",
        "options": [
            "I don't know which course to study",
            "I don't know which institution to choose",
            "I'm not sure if my JAMB score is competitive",
            "I'm worried about tuition and affordability",
            "I'm unsure about my subject combination",
        ]
    },
    {
        "id": "q3",
        "question": "What kind of institution do you prefer?",
        "type": "single",
        "options": [
            "Federal University — prestige and affordability",
            "State University — close to home and cheaper",
            "Private University — better facilities and focus",
            "Polytechnic — practical and technical skills",
            "I'm open to any type",
        ]
    },
    {
        "id": "q4",
        "question": "How important is campus location to you?",
        "type": "single",
        "options": [
            "Very important — I want to stay close to home",
            "Somewhat important — I prefer a specific region",
            "Not important — I'll go anywhere for the right school",
        ]
    },
    {
        "id": "q5",
        "question": "What is your annual tuition budget?",
        "type": "single",
        "options": [
            "Under ₦100,000 (federal universities)",
            "₦100,000 – ₦500,000 (state universities)",
            "₦500,000 – ₦1,500,000 (affordable private)",
            "Above ₦1,500,000 (top private universities)",
        ]
    },
    {
        "id": "q6",
        "question": "Which of these matters most to you in an institution?",
        "type": "multi",
        "options": [
            "Academic reputation and rankings",
            "Campus safety and stability",
            "Job placement after graduation",
            "Campus facilities and infrastructure",
            "Affordability and scholarship opportunities",
            "Social life and student community",
        ]
    },
    {
        "id": "q7",
        "question": "Have you chosen a course of study?",
        "type": "single",
        "options": [
            "Yes — I know exactly what I want to study",
            "I have 2-3 options I'm considering",
            "No — I need help choosing a course",
        ]
    },
]
