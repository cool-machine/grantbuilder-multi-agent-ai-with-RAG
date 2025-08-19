"""
Crawler Manager with Mock and Real Crawler Support
Provides unified interface for both mock and real crawling modes
"""

import json
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import random

from config import CrawlerConfig
from crawler import FundingCrawler, FundingOpportunity
from database import FundingDatabase

logger = logging.getLogger(__name__)

@dataclass
class CrawlerResult:
    success: bool
    total_found: int
    saved_count: int
    errors: List[str]
    opportunities: List[Dict[str, Any]]
    duration_seconds: float
    mode: str  # 'mock' or 'real'
    timestamp: str

class CrawlerManager:
    """Unified crawler manager supporting both mock and real crawling"""
    
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.config = CrawlerConfig()
        self.db = FundingDatabase()
        self.logger = logging.getLogger(__name__)
    
    async def start_crawl(self, config_overrides: Dict = None) -> CrawlerResult:
        """Start crawling with either mock or real implementation"""
        start_time = time.time()
        
        try:
            if self.use_mock:
                result = await self._mock_crawl(config_overrides or {})
            else:
                result = await self._real_crawl(config_overrides or {})
            
            # Calculate duration
            result.duration_seconds = time.time() - start_time
            result.timestamp = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Crawling failed: {str(e)}")
            return CrawlerResult(
                success=False,
                total_found=0,
                saved_count=0,
                errors=[str(e)],
                opportunities=[],
                duration_seconds=time.time() - start_time,
                mode='mock' if self.use_mock else 'real',
                timestamp=datetime.now().isoformat()
            )
    
    async def _real_crawl(self, config_overrides: Dict) -> CrawlerResult:
        """Execute real web crawling"""
        self.logger.info("Starting real web crawling")
        
        # Update configuration
        config = CrawlerConfig(
            request_delay=config_overrides.get('request_delay', self.config.request_delay),
            max_concurrent_requests=config_overrides.get('max_concurrent_requests', self.config.max_concurrent_requests),
            respect_robots_txt=config_overrides.get('respect_robots_txt', self.config.respect_robots_txt)
        )
        
        errors = []
        opportunities = []
        
        try:
            # Run the actual crawler
            async with FundingCrawler(config) as crawler:
                raw_opportunities = await crawler.crawl_all_sources()
                
                # Convert to dictionaries for serialization
                opportunities = [
                    {
                        'title': opp.title,
                        'description': opp.description,
                        'source': opp.source,
                        'url': opp.url,
                        'deadline': opp.deadline,
                        'amount': opp.amount,
                        'eligibility': opp.eligibility or [],
                        'categories': opp.categories or [],
                        'extracted_date': opp.extracted_date
                    }
                    for opp in raw_opportunities
                ]
                
                # Save to database
                saved_count = self.db.save_opportunities(raw_opportunities) if raw_opportunities else 0
                
                return CrawlerResult(
                    success=True,
                    total_found=len(opportunities),
                    saved_count=saved_count,
                    errors=errors,
                    opportunities=opportunities,
                    duration_seconds=0,  # Will be set by caller
                    mode='real',
                    timestamp=''  # Will be set by caller
                )
                
        except Exception as e:
            self.logger.error(f"Real crawl error: {str(e)}")
            errors.append(f"Real crawler error: {str(e)}")
            
            return CrawlerResult(
                success=False,
                total_found=0,
                saved_count=0,
                errors=errors,
                opportunities=[],
                duration_seconds=0,
                mode='real',
                timestamp=''
            )
    
    async def _mock_crawl(self, config_overrides: Dict) -> CrawlerResult:
        """Execute mock crawling with simulated data"""
        self.logger.info("Starting mock crawling (simulated data)")
        
        # Simulate processing time
        await self._simulate_delay(1.0, 3.0)
        
        # Generate mock opportunities
        mock_opportunities = self._generate_mock_opportunities()
        
        # Convert to FundingOpportunity objects for database compatibility
        funding_objects = []
        for opp in mock_opportunities:
            funding_objects.append(FundingOpportunity(
                title=opp['title'],
                description=opp['description'],
                source=opp['source'],
                url=opp['url'],
                deadline=opp['deadline'],
                amount=opp['amount'],
                eligibility=opp['eligibility'],
                categories=opp['categories'],
                extracted_date=opp['extracted_date']
            ))
        
        # Save to database
        saved_count = self.db.save_opportunities(funding_objects) if funding_objects else 0
        
        return CrawlerResult(
            success=True,
            total_found=len(mock_opportunities),
            saved_count=saved_count,
            errors=[],
            opportunities=mock_opportunities,
            duration_seconds=0,  # Will be set by caller
            mode='mock',
            timestamp=''  # Will be set by caller
        )
    
    def _generate_mock_opportunities(self) -> List[Dict[str, Any]]:
        """Generate realistic mock funding opportunities"""
        mock_sources = [
            "European Commission",
            "Fondation de France", 
            "French Ministry of Culture",
            "Horizon Europe",
            "LIFE Programme",
            "Creative Europe"
        ]
        
        mock_categories = [
            ["environment", "climate"],
            ["education", "social"],
            ["culture", "heritage"],
            ["innovation", "technology"],
            ["health", "community"],
            ["sport", "youth"]
        ]
        
        mock_templates = [
            {
                "title_template": "{source} Grant for {category} Projects 2025",
                "description_template": "Funding opportunity for {category} initiatives supporting French NGOs and associations. This program aims to strengthen civil society organizations working in the {category} sector."
            },
            {
                "title_template": "Innovation Fund - {category} Track",
                "description_template": "Open call for innovative {category} projects. Priority given to associations and NGOs with proven track record in community engagement."
            },
            {
                "title_template": "{category} Development Programme",
                "description_template": "Multi-year funding scheme supporting sustainable {category} development. Eligible organizations must be based in France or EU member states."
            }
        ]
        
        opportunities = []
        num_opportunities = random.randint(8, 15)
        
        for i in range(num_opportunities):
            source = random.choice(mock_sources)
            categories = random.choice(mock_categories)
            template = random.choice(mock_templates)
            category_text = " & ".join(categories)
            
            # Generate amounts
            min_amount = random.randint(5000, 50000)
            max_amount = random.randint(min_amount + 10000, min_amount + 500000)
            
            # Generate deadline (2-12 months from now)
            deadline_days = random.randint(60, 365)
            deadline = datetime.now().replace(
                day=min(28, datetime.now().day + deadline_days % 30),
                month=((datetime.now().month + deadline_days // 30 - 1) % 12) + 1
            ).strftime('%Y-%m-%d')
            
            opportunity = {
                'title': template['title_template'].format(source=source, category=category_text),
                'description': template['description_template'].format(category=category_text),
                'source': source,
                'url': f"https://mock-funding-source.com/grants/{i+1}",
                'deadline': deadline,
                'amount': f"€{min_amount:,} - €{max_amount:,}",
                'eligibility': ["French NGOs", "EU associations", "Civil society organizations"],
                'categories': categories,
                'extracted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _simulate_delay(self, min_seconds: float, max_seconds: float):
        """Simulate processing delay for realistic mock behavior"""
        import asyncio
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    def get_status(self) -> Dict[str, Any]:
        """Get crawler status and database statistics"""
        try:
            db_stats = self.db.get_statistics()
            
            return {
                'mode': 'mock' if self.use_mock else 'real',
                'database_connected': True,
                'total_opportunities': db_stats['total_opportunities'],
                'sources': db_stats['by_source'],
                'recent_additions': db_stats['recent_additions'],
                'last_updated': db_stats['last_updated'],
                'config': {
                    'request_delay': self.config.request_delay,
                    'max_concurrent_requests': self.config.max_concurrent_requests,
                    'respect_robots_txt': self.config.respect_robots_txt
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting status: {str(e)}")
            return {
                'mode': 'mock' if self.use_mock else 'real',
                'database_connected': False,
                'error': str(e)
            }
    
    def toggle_mode(self):
        """Toggle between mock and real crawling modes"""
        self.use_mock = not self.use_mock
        self.logger.info(f"Switched to {'mock' if self.use_mock else 'real'} crawling mode")
        return self.use_mock
    
    def set_mode(self, use_mock: bool):
        """Explicitly set crawling mode"""
        self.use_mock = use_mock
        self.logger.info(f"Set crawling mode to {'mock' if self.use_mock else 'real'}")
    
    def get_results(self, limit: int = 50, source: str = None, query: str = None) -> Dict[str, Any]:
        """Get crawling results from database"""
        try:
            if source or query:
                opportunities = self.db.search_opportunities(query=query, source=source)
            else:
                opportunities = self.db.get_all_opportunities()
            
            # Apply limit
            opportunities = opportunities[:limit]
            
            return {
                'success': True,
                'count': len(opportunities),
                'limit_applied': limit,
                'opportunities': opportunities
            }
        except Exception as e:
            self.logger.error(f"Error getting results: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }