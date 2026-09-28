import urllib.request
import json
import os

def get_env_var(key, default=""):
    if key in os.environ:
        return os.environ[key]
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    return line.strip().split("=", 1)[1]
    return default

SUPABASE_TOKEN = get_env_var("SUPABASE_TOKEN")
PROJECT_REF = get_env_var("PROJECT_REF", "jhjgapijtayhsuzejbtl")

procedures_seed = [
    {
        "slug": "uscis-stem-opt",
        "title": "USCIS 24-Month STEM OPT Extension",
        "agency": "USCIS / Department of Homeland Security",
        "statutory_citation": "8 C.F.R. § 214.2(f)(10)(ii)(C) & Form I-765 Instructions",
        "original_text": "To qualify for a 24-month extension of post-completion OPT, an F-1 student must possess a degree in a STEM field...",
        "flesch_grade_before": 17.8,
        "flesch_grade_after": 5.6,
        "pruned_percent": "64%",
        "pitfall_count": 3
    },
    {
        "slug": "medicaid-appeal",
        "title": "Medicaid Notice of Termination & Fair Hearing Appeal",
        "agency": "CMS / State Department of Health",
        "statutory_citation": "42 CFR § 431.200 Subpart E & Social Security Act § 1902(a)(3)",
        "original_text": "If the beneficiary requests a fair hearing within 10 days of the date of the notice of action...",
        "flesch_grade_before": 16.4,
        "flesch_grade_after": 5.2,
        "pruned_percent": "58%",
        "pitfall_count": 2
    },
    {
        "slug": "irs-compromise",
        "title": "IRS Offer in Compromise (Form 656 & § 7122)",
        "agency": "Internal Revenue Service / Department of the Treasury",
        "statutory_citation": "26 U.S. Code § 7122 & Treasury Regulation § 301.7122-1",
        "original_text": "An Offer in Compromise (OIC) will be returned without processing if the taxpayer is not current...",
        "flesch_grade_before": 18.2,
        "flesch_grade_after": 6.0,
        "pruned_percent": "71%",
        "pitfall_count": 3
    },
    {
        "slug": "tenant-shield",
        "title": "City Housing Voucher & Eviction Defense Notice",
        "agency": "Municipal Housing Court / Housing Authority",
        "statutory_citation": "Uniform Residential Landlord and Tenant Act § 4.201",
        "original_text": "If rent is unpaid when due, landlord may deliver written notice demanding payment within 14 calendar days...",
        "flesch_grade_before": 15.9,
        "flesch_grade_after": 5.4,
        "pruned_percent": "54%",
        "pitfall_count": 2
    }
]

def main():
    if not SUPABASE_TOKEN:
        print("Error: SUPABASE_TOKEN environment variable not set.")
        return

    statements = []
    for p in procedures_seed:
        statements.append(f"""
        INSERT INTO procedures (slug, title, agency, statutory_citation, original_text, flesch_grade_before, flesch_grade_after, pruned_percent, pitfall_count)
        VALUES ('{p["slug"]}', '{p["title"]}', '{p["agency"]}', '{p["statutory_citation"]}', '{p["original_text"]}', {p["flesch_grade_before"]}, {p["flesch_grade_after"]}, '{p["pruned_percent"]}', {p["pitfall_count"]})
        ON CONFLICT (slug) DO UPDATE SET 
            title = EXCLUDED.title,
            statutory_citation = EXCLUDED.statutory_citation,
            flesch_grade_before = EXCLUDED.flesch_grade_before,
            flesch_grade_after = EXCLUDED.flesch_grade_after;
        """)

    sql = "\n".join(statements)
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    data = json.dumps({"query": sql}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {SUPABASE_TOKEN}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as resp:
        print("Seeding status:", resp.status)

if __name__ == "__main__":
    main()
