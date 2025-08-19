import sqlite3
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from crawler import FundingOpportunity
import logging

Base = declarative_base()

class FundingOpportunityDB(Base):
    __tablename__ = 'funding_opportunities'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    source = Column(String(200), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    deadline = Column(String(100))
    amount = Column(String(200))
    eligibility = Column(Text)  # JSON string
    categories = Column(Text)   # JSON string
    extracted_date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)

class FundingDatabase:
    def __init__(self, db_path: str = "funding_opportunities.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)
    
    def save_opportunities(self, opportunities: List[FundingOpportunity]) -> int:
        """Save funding opportunities to database"""
        session = self.Session()
        saved_count = 0
        
        try:
            for opp in opportunities:
                # Check if opportunity already exists (by URL)
                existing = session.query(FundingOpportunityDB).filter_by(url=opp.url).first()
                
                if not existing:
                    db_opp = FundingOpportunityDB(
                        title=opp.title,
                        description=opp.description,
                        source=opp.source,
                        url=opp.url,
                        deadline=opp.deadline,
                        amount=opp.amount,
                        eligibility=json.dumps(opp.eligibility) if opp.eligibility else None,
                        categories=json.dumps(opp.categories) if opp.categories else None,
                        extracted_date=datetime.strptime(opp.extracted_date, '%Y-%m-%d %H:%M:%S') if opp.extracted_date else datetime.now()
                    )
                    session.add(db_opp)
                    saved_count += 1
                else:
                    # Update existing record with new information
                    existing.description = opp.description or existing.description
                    existing.deadline = opp.deadline or existing.deadline
                    existing.amount = opp.amount or existing.amount
                    existing.extracted_date = datetime.now()
            
            session.commit()
            self.logger.info(f"Saved {saved_count} new opportunities to database")
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving to database: {e}")
            raise
        finally:
            session.close()
        
        return saved_count
    
    def get_all_opportunities(self) -> List[Dict]:
        """Retrieve all opportunities from database"""
        session = self.Session()
        try:
            opportunities = session.query(FundingOpportunityDB).all()
            result = []
            
            for opp in opportunities:
                result.append({
                    'id': opp.id,
                    'title': opp.title,
                    'description': opp.description,
                    'source': opp.source,
                    'url': opp.url,
                    'deadline': opp.deadline,
                    'amount': opp.amount,
                    'eligibility': json.loads(opp.eligibility) if opp.eligibility else [],
                    'categories': json.loads(opp.categories) if opp.categories else [],
                    'extracted_date': opp.extracted_date.isoformat() if opp.extracted_date else None,
                    'created_at': opp.created_at.isoformat() if opp.created_at else None
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error retrieving from database: {e}")
            raise
        finally:
            session.close()
    
    def search_opportunities(self, query: str = None, source: str = None, 
                           category: str = None) -> List[Dict]:
        """Search opportunities with filters"""
        session = self.Session()
        try:
            q = session.query(FundingOpportunityDB)
            
            if query:
                q = q.filter(
                    FundingOpportunityDB.title.contains(query) |
                    FundingOpportunityDB.description.contains(query)
                )
            
            if source:
                q = q.filter(FundingOpportunityDB.source == source)
            
            if category:
                q = q.filter(FundingOpportunityDB.categories.contains(category))
            
            opportunities = q.all()
            result = []
            
            for opp in opportunities:
                result.append({
                    'id': opp.id,
                    'title': opp.title,
                    'description': opp.description,
                    'source': opp.source,
                    'url': opp.url,
                    'deadline': opp.deadline,
                    'amount': opp.amount,
                    'eligibility': json.loads(opp.eligibility) if opp.eligibility else [],
                    'categories': json.loads(opp.categories) if opp.categories else [],
                    'extracted_date': opp.extracted_date.isoformat() if opp.extracted_date else None,
                    'created_at': opp.created_at.isoformat() if opp.created_at else None
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error searching database: {e}")
            raise
        finally:
            session.close()
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export opportunities to CSV file"""
        if not filename:
            filename = f"funding_opportunities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            opportunities = self.get_all_opportunities()
            
            # Flatten the data for CSV
            flattened_data = []
            for opp in opportunities:
                flattened_opp = opp.copy()
                flattened_opp['eligibility'] = ', '.join(opp['eligibility']) if opp['eligibility'] else ''
                flattened_opp['categories'] = ', '.join(opp['categories']) if opp['categories'] else ''
                flattened_data.append(flattened_opp)
            
            df = pd.DataFrame(flattened_data)
            df.to_csv(filename, index=False)
            
            self.logger.info(f"Exported {len(opportunities)} opportunities to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def export_to_json(self, filename: str = None) -> str:
        """Export opportunities to JSON file"""
        if not filename:
            filename = f"funding_opportunities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            opportunities = self.get_all_opportunities()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(opportunities, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(opportunities)} opportunities to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored opportunities"""
        session = self.Session()
        try:
            total_count = session.query(FundingOpportunityDB).count()
            
            # Count by source
            from sqlalchemy import func
            source_counts = session.query(
                FundingOpportunityDB.source,
                func.count(FundingOpportunityDB.id).label('count')
            ).group_by(FundingOpportunityDB.source).all()
            
            # Recent additions (last 7 days)
            week_ago = datetime.now().replace(day=datetime.now().day-7)
            recent_count = session.query(FundingOpportunityDB).filter(
                FundingOpportunityDB.created_at >= week_ago
            ).count()
            
            return {
                'total_opportunities': total_count,
                'by_source': {source: count for source, count in source_counts},
                'recent_additions': recent_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            raise
        finally:
            session.close()

# Utility functions
def create_sample_data():
    """Create some sample data for testing"""
    sample_opportunities = [
        FundingOpportunity(
            title="EU Innovation Fund 2025",
            description="Supporting low-carbon technology innovation across Europe",
            source="European Commission",
            url="https://ec.europa.eu/innovation-fund",
            deadline="2025-09-15",
            amount="€10M - €60M",
            eligibility=["EU member states", "innovative technology"],
            categories=["innovation", "climate", "technology"],
            extracted_date="2025-01-15 10:30:00"
        ),
        FundingOpportunity(
            title="Horizon Europe Civil Society Grant",
            description="Research funding for civil society organizations",
            source="Horizon Europe",
            url="https://ec.europa.eu/horizon-europe",
            deadline="2025-08-30",
            amount="€50K - €500K",
            eligibility=["civil society organizations", "research focus"],
            categories=["research", "civil society"],
            extracted_date="2025-01-15 11:00:00"
        )
    ]
    
    db = FundingDatabase()
    db.save_opportunities(sample_opportunities)
    print("Sample data created successfully!")

if __name__ == "__main__":
    # Create sample data and test exports
    create_sample_data()
    
    db = FundingDatabase()
    
    # Test exports
    csv_file = db.export_to_csv()
    json_file = db.export_to_json()
    
    # Show statistics
    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    print(json.dumps(stats, indent=2))