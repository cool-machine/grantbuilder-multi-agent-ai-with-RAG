import requests
import time
import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Optional
import asyncio
import aiohttp
from config import CrawlerConfig, FUNDING_SOURCES, FRENCH_NGO_ELIGIBILITY_CRITERIA

@dataclass
class FundingOpportunity:
    title: str
    description: str
    source: str
    url: str
    deadline: Optional[str] = None
    amount: Optional[str] = None
    eligibility: List[str] = None
    categories: List[str] = None
    extracted_date: str = None

class RobotsTxtChecker:
    def __init__(self):
        self.robots_cache = {}
    
    def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        """Check if URL can be fetched according to robots.txt"""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = urljoin(base_url, '/robots.txt')
        
        if robots_url not in self.robots_cache:
            try:
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                self.robots_cache[robots_url] = rp
                logging.info(f"Loaded robots.txt from {robots_url}")
            except Exception as e:
                logging.warning(f"Could not load robots.txt from {robots_url}: {e}")
                return True  # If can't load robots.txt, assume allowed
        
        robots_parser = self.robots_cache.get(robots_url)
        if robots_parser:
            return robots_parser.can_fetch(user_agent, url)
        return True

class RateLimiter:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.last_request = {}
    
    async def wait(self, domain: str):
        """Wait appropriate time before making request to domain"""
        now = time.time()
        if domain in self.last_request:
            elapsed = now - self.last_request[domain]
            if elapsed < self.delay:
                sleep_time = self.delay - elapsed
                await asyncio.sleep(sleep_time)
        self.last_request[domain] = time.time()

class FundingCrawler:
    def __init__(self, config: CrawlerConfig = None):
        self.config = config or CrawlerConfig()
        self.robots_checker = RobotsTxtChecker()
        self.rate_limiter = RateLimiter(self.config.request_delay)
        self.session = None
        self.opportunities = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=self.config.max_concurrent_requests)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': self.config.user_agent}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def check_robots_txt_compliance(self, url: str) -> bool:
        """Check if URL can be crawled according to robots.txt"""
        if not self.config.respect_robots_txt:
            return True
        return self.robots_checker.can_fetch(url, self.config.user_agent)
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single page with rate limiting and robots.txt compliance"""
        if not self.check_robots_txt_compliance(url):
            self.logger.warning(f"Robots.txt disallows crawling: {url}")
            return None
        
        domain = urlparse(url).netloc
        await self.rate_limiter.wait(domain)
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    self.logger.info(f"Successfully fetched: {url}")
                    return content
                else:
                    self.logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_funding_opportunities(self, html: str, source_url: str, source_name: str) -> List[FundingOpportunity]:
        """Extract funding opportunities from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        opportunities = []
        
        # Enhanced extraction patterns for different types of funding sites
        opportunity_selectors = [
            # Generic patterns
            'div.opportunity', 'div.funding-item', 'article', 'div.grant', 'div.call', 'div.tender',
            # EU-specific patterns
            'div.topic-item', 'div.call-item', 'tr.call-row', 'div.funding-opportunity',
            # News/announcement patterns
            'div.news-item', 'div.press-release', 'article.announcement',
            # French government patterns  
            'div.aide', 'div.subvention', 'div.dispositif', 'section.demarche',
            # Foundation patterns
            'div.grant-listing', 'div.grant-item', 'div.programme-item',
            # Generic content blocks
            'div[class*="item"]', 'div[class*="card"]', 'div[class*="block"]',
            'li[class*="item"]', 'section[class*="content"]'
        ]
        
        for selector in opportunity_selectors:
            items = soup.select(selector)
            if items:
                for item in items[:10]:  # Limit to first 10 per page
                    opportunity = self.parse_opportunity_item(item, source_url, source_name)
                    if opportunity and self.is_eligible_for_french_ngos(opportunity):
                        opportunities.append(opportunity)
                break  # Use first successful selector
        
        # Fallback: look for links that might be opportunities
        if not opportunities:
            links = soup.find_all('a', href=True)
            for link in links[:50]:  # Check more links
                text = link.get_text(strip=True)
                # Enhanced keyword matching
                funding_keywords = [
                    'grant', 'funding', 'call', 'opportunity', 'programme', 'scheme',
                    'subvention', 'aide', 'financement', 'appel', 'dispositif',
                    'bourse', 'prix', 'concours', 'soutien', 'allocation'
                ]
                if (len(text) > 10 and len(text) < 200 and 
                    any(keyword in text.lower() for keyword in funding_keywords)):
                    
                    # Get surrounding context for better description
                    parent = link.parent
                    description = ""
                    if parent:
                        desc_text = parent.get_text(strip=True)
                        if len(desc_text) > len(text):
                            description = desc_text[:300]
                    
                    opportunity = FundingOpportunity(
                        title=text,
                        description=description,
                        source=source_name,
                        url=urljoin(source_url, link['href'])
                    )
                    if self.is_eligible_for_french_ngos(opportunity):
                        opportunities.append(opportunity)
        
        return opportunities
    
    def parse_opportunity_item(self, item, source_url: str, source_name: str) -> Optional[FundingOpportunity]:
        """Parse individual opportunity item from HTML element"""
        try:
            # Extract title
            title_elem = item.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', '.title', '.name'])
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract description
            desc_elem = item.find(['p', '.description', '.summary', '.abstract'])
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract URL
            link_elem = item.find('a', href=True)
            url = urljoin(source_url, link_elem['href']) if link_elem else source_url
            
            # Extract deadline
            deadline_elem = item.find(text=lambda t: t and ('deadline' in t.lower() or 'due' in t.lower()))
            deadline = deadline_elem.strip() if deadline_elem else None
            
            if title:
                return FundingOpportunity(
                    title=title,
                    description=description,
                    source=source_name,
                    url=url,
                    deadline=deadline,
                    extracted_date=time.strftime('%Y-%m-%d %H:%M:%S')
                )
        except Exception as e:
            self.logger.error(f"Error parsing opportunity item: {e}")
        
        return None
    
    def is_eligible_for_french_ngos(self, opportunity: FundingOpportunity) -> bool:
        """Check if opportunity is eligible for French NGOs"""
        text_to_check = f"{opportunity.title} {opportunity.description}".lower()
        
        # Check for positive eligibility indicators
        for criterion in FRENCH_NGO_ELIGIBILITY_CRITERIA:
            if criterion.lower() in text_to_check:
                return True
        
        # Check for exclusionary terms
        exclusions = ['us only', 'usa only', 'american', 'domestic only']
        for exclusion in exclusions:
            if exclusion in text_to_check:
                return False
        
        # If no specific eligibility mentioned, assume it might be eligible
        return True
    
    async def crawl_source(self, source) -> List[FundingOpportunity]:
        """Crawl a single funding source"""
        self.logger.info(f"Starting to crawl: {source.name}")
        
        if not source.crawl_allowed:
            self.logger.warning(f"Crawling not allowed for: {source.name}")
            return []
        
        opportunities = []
        
        try:
            # Crawl main page
            html = await self.fetch_page(source.base_url)
            if html:
                page_opportunities = self.extract_funding_opportunities(
                    html, source.base_url, source.name
                )
                opportunities.extend(page_opportunities)
                self.logger.info(f"Found {len(page_opportunities)} opportunities on main page of {source.name}")
            
        except Exception as e:
            self.logger.error(f"Error crawling {source.name}: {e}")
        
        return opportunities
    
    async def crawl_all_sources(self) -> List[FundingOpportunity]:
        """Crawl all configured funding sources"""
        all_opportunities = []
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def crawl_with_semaphore(source):
            async with semaphore:
                return await self.crawl_source(source)
        
        # Crawl all sources concurrently
        tasks = [crawl_with_semaphore(source) for source in FUNDING_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Error crawling {FUNDING_SOURCES[i].name}: {result}")
            else:
                all_opportunities.extend(result)
        
        self.opportunities = all_opportunities
        self.logger.info(f"Total opportunities found: {len(all_opportunities)}")
        return all_opportunities

# Main execution function
async def main():
    """Main crawler execution"""
    config = CrawlerConfig()
    
    async with FundingCrawler(config) as crawler:
        opportunities = await crawler.crawl_all_sources()
        
        # Print results
        print(f"\n=== FUNDING OPPORTUNITIES FOR FRENCH NGOs ===")
        print(f"Found {len(opportunities)} opportunities\n")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp.title}")
            print(f"   Source: {opp.source}")
            print(f"   URL: {opp.url}")
            if opp.deadline:
                print(f"   Deadline: {opp.deadline}")
            if opp.description:
                print(f"   Description: {opp.description[:200]}...")
            print()

if __name__ == "__main__":
    asyncio.run(main())