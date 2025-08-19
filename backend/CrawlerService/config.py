import os
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class CrawlerConfig:
    request_delay: float = 2.0
    max_concurrent_requests: int = 5
    timeout: int = 30
    max_retries: int = 3
    user_agent: str = "NGO-Funding-Crawler/1.0 (Research Purpose)"
    respect_robots_txt: bool = True
    
@dataclass 
class FundingSource:
    name: str
    base_url: str
    api_endpoint: str = None
    requires_auth: bool = False
    eligibility_keywords: List[str] = None
    crawl_allowed: bool = True

FUNDING_SOURCES = [
    FundingSource(
        name="EU Funding Calls - Current",
        base_url="https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/calls-for-proposals",
        eligibility_keywords=["EU", "European", "civil society", "NGO", "non-profit"]
    ),
    FundingSource(
        name="European Foundation Centre",
        base_url="https://www.efc.be/funding-opportunities/",
        eligibility_keywords=["foundation", "grant", "funding", "civil society"]
    ),
    FundingSource(
        name="French Government Grants",
        base_url="https://www.associations.gouv.fr/les-subventions-publiques.html",
        eligibility_keywords=["subvention", "aide", "financement", "association"]
    ),
    FundingSource(
        name="LIFE Programme",
        base_url="https://cinea.ec.europa.eu/programmes/life_en",
        eligibility_keywords=["environment", "climate", "LIFE", "EU funding"]
    ),
    FundingSource(
        name="Erasmus Plus Calls",
        base_url="https://erasmus-plus.ec.europa.eu/opportunities/calls-for-proposals",
        eligibility_keywords=["education", "training", "youth", "sport"]
    ),
    FundingSource(
        name="French Ministry Culture",
        base_url="https://www.culture.gouv.fr/Aides-demarches",
        eligibility_keywords=["culture", "patrimoine", "art", "subvention"]
    )
]

FRENCH_NGO_ELIGIBILITY_CRITERIA = [
    "EU member state",
    "European Union",
    "France eligible",
    "international organizations",
    "civil society organizations",
    "non-governmental organizations",
    "associations",
    "charitable organizations",
    "non-profit",
    "ONG française"
]

OUTPUT_CONFIG = {
    "database_path": "funding_opportunities.db",
    "csv_export_path": "funding_export.csv",
    "json_export_path": "funding_export.json"
}