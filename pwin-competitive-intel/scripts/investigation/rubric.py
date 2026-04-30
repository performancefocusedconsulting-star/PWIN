# pwin-competitive-intel/scripts/investigation/rubric.py
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Five departments sampled to span the expected quality spread
SAMPLE_DEPARTMENTS = {
    "hmt": {
        "name": "HM Treasury",
        "data_gov_uk_query": "HM Treasury organogram senior staff salaries",
        "gov_uk_people_url": "https://www.gov.uk/government/organisations/hm-treasury/about/our-governance",
        "expected_scs_approx": 60,   # approximate SCS headcount from Cabinet Office stats
        "notes": "Small, central, organisationally tidy. Best-case baseline.",
    },
    "mod": {
        "name": "Ministry of Defence",
        "data_gov_uk_query": "Ministry of Defence organogram senior staff salaries",
        "gov_uk_people_url": "https://www.gov.uk/government/organisations/ministry-of-defence/about/our-governance",
        "expected_scs_approx": 500,
        "notes": "Large, complex, multiple agencies. Worst-case central government.",
    },
    "dfe": {
        "name": "Department for Education",
        "data_gov_uk_query": "Department for Education organogram senior staff salaries",
        "gov_uk_people_url": "https://www.gov.uk/government/organisations/department-for-education/about/our-governance",
        "expected_scs_approx": 200,
        "notes": "Middle-of-the-road; known sub-org dark spot in FTS data.",
    },
    "nhse": {
        "name": "NHS England",
        "data_gov_uk_query": "NHS England organogram senior staff",
        "gov_uk_people_url": "https://www.england.nhs.uk/about/our-people/nhs-england-executive/",
        "expected_scs_approx": None,   # different regime — ODS not Cabinet Office stats
        "notes": "Different publishing regime. Tests generalisation beyond Whitehall.",
    },
    "bcc": {
        "name": "Birmingham City Council",
        "data_gov_uk_query": "Birmingham City Council organogram senior staff",
        "gov_uk_people_url": "https://www.birmingham.gov.uk/about-the-council",
        "expected_scs_approx": None,   # no organogram requirement for local gov
        "notes": "No organogram regime. Tests what local government data exists.",
    },
}

# Standard columns in the Cabinet Office organogram CSV format (since ~2011)
STANDARD_ORGANOGRAM_COLUMNS = [
    "Post Unique Reference",
    "Name",
    "Grade",
    "Job Title",
    "Parent Department",
    "Organisation",
    "Unit",
    "Contact Phone",
    "Contact Email",
    "Reports To Senior Post",
    "Salary Cost of Reports",
    "FTE",
    "Actual Pay Floor",
    "Actual Pay Ceiling",
    "Professional/Occupational Group",
    "Notes",
    "Valid?",
]

# Thresholds for the four verdict criteria
VERDICT_THRESHOLDS = {
    "senior_coverage_pct": {
        "build_as_scoped": 90,
        "build_narrower":  70,
        # below 70 for central gov -> don't build
    },
    "evaluator_source_buyer_pct": {
        # fraction of sampled departments with >= 1 useful evaluator-level source
        "build_as_scoped": 70,
        "build_narrower":  0,   # central gov only is acceptable
    },
    "max_currency_lag_days": {
        "build_as_scoped": 180,
        "build_narrower":  365,
        # above 365 even for central gov -> don't build
    },
    "distinct_formats": {
        "build_as_scoped": 2,
        "build_narrower":  5,
        # above 5 -> don't build
    },
}

# Alternative sources to score in Track 2
ALTERNATIVE_SOURCES = [
    {
        "id": "gov_uk_people",
        "name": "GOV.UK People pages",
        "url_pattern": "https://www.gov.uk/government/organisations/{dept}/about/our-governance",
        "test": "Pull 3 departments, compare named SCS to organogram count",
        "automated": False,
    },
    {
        "id": "gov_uk_appointments_rss",
        "name": "GOV.UK appointments RSS",
        "url_pattern": "https://www.gov.uk/government/announcements.atom?announcement_filter_option=appointments",
        "test": "Download feed, count usable appointment signals in last 30 days",
        "automated": True,
    },
    {
        "id": "companies_house",
        "name": "Companies House — ALB officers",
        "url_pattern": "https://api.company-information.service.gov.uk/company/{company_number}/officers",
        "test": "Pick 3 ALBs (UKHSA, Homes England, UKRI), check officer filings",
        "automated": True,
    },
    {
        "id": "nao_reports",
        "name": "NAO published reports",
        "url_pattern": "https://www.nao.org.uk/reports/",
        "test": "Sample 3 recent VFM reports, extract named SROs and accountable officers",
        "automated": False,
    },
    {
        "id": "pac_witnesses",
        "name": "Public Accounts Committee witness lists",
        "url_pattern": "https://committees.parliament.uk/committee/127/public-accounts-committee/",
        "test": "Last 12 months of sessions — count distinct named officials by department",
        "automated": False,
    },
    {
        "id": "civil_service_jobs",
        "name": "Civil Service Jobs vacancies",
        "url_pattern": "https://www.civilservicejobs.service.gov.uk/",
        "test": "Sample one week of vacancies at Grade 7 and above — count named hiring units",
        "automated": False,
    },
    {
        "id": "linkedin_manual",
        "name": "LinkedIn (manual search)",
        "url_pattern": "https://www.linkedin.com/search/results/people/",
        "test": "Search 3 departments for Grade 7 commercial leads with public profiles; count and assess profile completeness",
        "automated": False,
    },
    {
        "id": "trade_press",
        "name": "Trade press (Civil Service World, Computer Weekly, Public Sector Executive)",
        "url_pattern": "https://www.civilserviceworld.com/",
        "test": "Last 30 days — count usable named-official mentions with role and unit",
        "automated": False,
    },
    {
        "id": "fts_contact_names",
        "name": "Procurement notice contacts in bid_intel.db",
        "url_pattern": None,
        "test": "SQL query against notices table — fraction with named contact, fraction where name looks like a real person not a team inbox",
        "automated": True,
    },
    {
        "id": "dods_people",
        "name": "Dods People (paid commercial product)",
        "url_pattern": "https://dodsgroup.com/products/dods-people/",
        "test": "Desk-only — check pricing, coverage claim, and free trial availability",
        "automated": False,
    },
]

# Score template written to findings/track2_sources.json for each source
SOURCE_SCORE_TEMPLATE = {
    "id": "",
    "name": "",
    "coverage_note": "",       # what fraction of the expected population is named
    "currency_note": "",       # how fresh; how often updated
    "structure": "",           # "structured", "semi-structured", "unstructured"
    "licence": "",             # "OGL", "public-domain", "paid", "scrape-required", "ToS-restricted"
    "useful_for_senior_tier": None,   # bool
    "useful_for_evaluator_tier": None,  # bool
    "notes": "",
}
