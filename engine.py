import os
from google import genai
# 1. Curated Schemes Database (Coverage)
SCHEMES_DB = [
    {
        "id": "pmegp",
        "name": "Prime Minister Employment Generation Programme (PMEGP)",
        "target_audience": "Entrepreneur",
        "min_age": 18,
        "max_age": 65,
        "gender": "All",
        "max_income": None,
        "category": ["General", "OBC", "SC", "ST"],
        "benefit": "Up to 35% project subsidy for micro-enterprises (Manufacturing up to ₹50L, Service up to ₹20L).",
        "link": "https://www.msme.gov.in"
    },
    {
        "id": "mudra_shishu",
        "name": "PM MUDRA Yojana (Shishu Loan)",
        "target_audience": "Entrepreneur",
        "min_age": 18,
        "max_age": 65,
        "gender": "All",
        "max_income": None,
        "category": ["General", "OBC", "SC", "ST"],
        "benefit": "Collateral-free loan up to ₹50,000 for starting a micro-business.",
        "link": "https://www.mudra.org.in"
    },
    {
        "id": "mudra_kishor",
        "name": "PM MUDRA Yojana (Kishor Loan)",
        "target_audience": "Entrepreneur",
        "min_age": 18,
        "max_age": 65,
        "gender": "All",
        "max_income": None,
        "category": ["General", "OBC", "SC", "ST"],
        "benefit": "Business expansion loan between ₹50,000 and ₹5,00,000.",
        "link": "https://www.mudra.org.in"
    },
    {
        "id": "standup_india",
        "name": "Stand-Up India Scheme",
        "target_audience": "Entrepreneur",
        "min_age": 18,
        "max_age": 65,
        "gender": "Female", # Either Female OR SC/ST
        "max_income": None,
        "category": ["General", "OBC", "SC", "ST"],
        "benefit": "Bank loans between ₹10 lakh and ₹1 crore for greenfield manufacturing/services.",
        "link": "https://www.standupmitra.in"
    },
    {
        "id": "post_matric_sc",
        "name": "Post-Matric Scholarship for SC Students",
        "target_audience": "Student",
        "min_age": 15,
        "max_age": 30,
        "gender": "All",
        "max_income": 250000,
        "category": ["SC"],
        "benefit": "100% tuition fees reimbursement + monthly academic allowance.",
        "link": "https://scholarships.gov.in"
    },
    {
        "id": "post_matric_obc",
        "name": "Post-Matric Scholarship for OBC Students",
        "target_audience": "Student",
        "min_age": 15,
        "max_age": 30,
        "gender": "All",
        "max_income": 150000,
        "category": ["OBC"],
        "benefit": "Maintenance allowance and fee assistance for higher education.",
        "link": "https://scholarships.gov.in"
    },
    {
        "id": "nsp_merit_means",
        "name": "National Means-cum-Merit Scholarship Scheme (NMMSS)",
        "target_audience": "Student",
        "min_age": 13,
        "max_age": 20,
        "gender": "All",
        "max_income": 350000,
        "category": ["General", "OBC", "SC", "ST"],
        "benefit": "₹12,000 per annum to support secondary and higher secondary study.",
        "link": "https://scholarships.gov.in"
    },
    {
        "id": "pragati_scholarship",
        "name": "AICTE Pragati Scholarship for Girls",
        "target_audience": "Student",
        "min_age": 16,
        "max_age": 26,
        "gender": "Female",
        "max_income": 800000,
        "category": ["General", "OBC", "SC", "ST"],
        "benefit": "₹50,000 per annum for tuition fees and equipment purchase.",
        "link": "https://www.aicte-india.org"
    },
    {
        "id": "pm_kisan",
        "name": "PM Kisan Samman Nidhi",
        "target_audience": "Farmer",
        "min_age": 18,
        "max_age": 80,
        "gender": "All",
        "max_income": None,
        "category": ["General", "OBC", "SC", "ST"],
        "benefit": "₹6,000 direct bank transfer per year in 3 installments.",
        "link": "https://pmkisan.gov.in"
    },
    {
        "id": "kcc_scheme",
        "name": "Kisan Credit Card (KCC)",
        "target_audience": "Farmer",
        "min_age": 18,
        "max_age": 75,
        "gender": "All",
        "max_income": None,
        "category": ["General", "OBC", "SC", "ST"],
        "benefit": "Agricultural credit up to ₹3 lakh at 4% subsidized interest rate.",
        "link": "https://agricoop.nic.in"
    },
    {
        "id": "pm_svanidhi",
        "name": "PM SVANidhi (Street Vendor Support)",
        "target_audience": "Entrepreneur",
        "min_age": 18,
        "max_age": 65,
        "gender": "All",
        "max_income": None,
        "category": ["General", "OBC", "SC", "ST"],
        "benefit": "Working capital loan starting from ₹10,000 up to ₹50,000 with 7% interest subsidy.",
        "link": "https://pmsvanidhi.mohua.gov.in"
    }
]

# 2. Ranking Algorithm
def rank_schemes(schemes_list: list) -> list:
    def calculate_score(item):
        benefit_text = item.get("benefit", "").lower()
        score = 0
        if "reimbursement" in benefit_text or "100%" in benefit_text:
            score += 50
        if "subsidy" in benefit_text:
            score += 40
        if "loan" in benefit_text:
            score += 30
        if "per year" in benefit_text or "per annum" in benefit_text:
            score += 20
        return score

    return sorted(schemes_list, key=calculate_score, reverse=True)

# 3. Deterministic Matching & Near-Miss Detection
def evaluate_eligibility(user_profile: dict):
    qualified = []
    near_misses = []

    user_age = user_profile.get("age", 0)
    user_gender = user_profile.get("gender", "")
    user_occ = user_profile.get("occupation", "")
    user_income = user_profile.get("annual_income", 0)
    user_category = user_profile.get("category", "")

    for scheme in SCHEMES_DB:
        mismatches = []

        # Occupation Check
        if scheme["target_audience"] != user_occ:
            mismatches.append(f"Target occupation is '{scheme['target_audience']}' (you are '{user_occ}')")

        # Age Check
        if user_age < scheme["min_age"]:
            mismatches.append(f"Minimum age requirement is {scheme['min_age']} years (you are {user_age})")
        elif scheme["max_age"] and user_age > scheme["max_age"]:
            mismatches.append(f"Maximum age limit is {scheme['max_age']} years (you are {user_age})")

        # Stand-Up India Specific Rule: Female OR (SC/ST)
        if scheme["id"] == "standup_india":
            is_valid_group = (user_gender == "Female") or (user_category in ["SC", "ST"])
            if not is_valid_group:
                mismatches.append("Only applicable for Women founders or SC/ST entrepreneurs")
        else:
            if scheme["gender"] != "All" and user_gender != scheme["gender"]:
                mismatches.append(f"Reserved exclusively for {scheme['gender']} applicants")
            if user_category not in scheme["category"]:
                mismatches.append(f"Applicable only for categories: {', '.join(scheme['category'])}")

        # Income Check
        if scheme["max_income"] is not None:
            if user_income > scheme["max_income"]:
                mismatches.append(f"Family income limit is ₹{scheme['max_income']:,} (your stated income is ₹{user_income:,})")

        # Filter Results
        if len(mismatches) == 0:
           qualified.append({
            "name": scheme["name"],
            "scheme_name": scheme["name"],
            "benefit": scheme["benefit"],
            "link": scheme["link"],
            "criteria_matched": f"Age {user_age}, Occupation {user_occ}, Category {user_category}"
        })
       elif len(mismatches) == 1:
            near_misses.append({
                "name": scheme["name"],
                "scheme_name": scheme["name"],
                "benefit": scheme["benefit"],
                "bottleneck": mismatches[0]
            })
    return rank_schemes(qualified), near_misses

# 4. LLM Reasoning Generator
def generate_conversational_explanation(user_profile: dict, qualified: list, near_misses: list) -> str:
    client = genai.Client()
    
    prompt = f"""
    You are an expert Government Scheme Advisor for citizens in India.
    
    User Profile:
    - Age: {user_profile.get('age')}
    - Gender: {user_profile.get('gender')}
    - Category: {user_profile.get('category')}
    - Occupation: {user_profile.get('occupation')}
    - Annual Income: ₹{user_profile.get('annual_income')}

    Deterministic Evaluation Result:
    Qualified Schemes: {qualified}
    Near-Miss Schemes: {near_misses}

    Task:
    Provide an empowering, clear, plain-language summary for this citizen:
    1. For QUALIFIED schemes: State clearly why they qualify and what exact benefit they get.
    2. For NEAR-MISS schemes: Explain gently the single requirement they missed and what action they can take.
    
    Keep the tone polite, supportive, and crisp.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text
