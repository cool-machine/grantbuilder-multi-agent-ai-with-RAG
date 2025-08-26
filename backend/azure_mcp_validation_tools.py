"""
Azure-Powered MCP Validation Tools for DeepSeek R1 Multi-Agent System
Budget checking and compliance validation using Azure services
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import os
from decimal import Decimal, ROUND_HALF_UP
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

class ValidationResult(Enum):
    """Validation results"""
    PASS = "pass"
    WARNING = "warning" 
    FAIL = "fail"
    ERROR = "error"

class ComplianceCategory(Enum):
    """Compliance categories"""
    BUDGET_LIMITS = "budget_limits"
    ELIGIBILITY = "eligibility"
    FORMATTING = "formatting"
    CONTENT_REQUIREMENTS = "content_requirements"
    DEADLINES = "deadlines"
    DOCUMENTATION = "documentation"

@dataclass
class ValidationIssue:
    """Structure for validation issues"""
    category: ComplianceCategory
    severity: ValidationResult
    description: str
    recommendation: str
    field: Optional[str] = None
    current_value: Optional[str] = None
    expected_value: Optional[str] = None
    auto_fixable: bool = False

@dataclass
class BudgetValidation:
    """Budget validation results"""
    total_budget: Decimal
    budget_breakdown: Dict[str, Decimal]
    funding_limit: Optional[Decimal]
    within_limits: bool
    cost_per_deliverable: Dict[str, Decimal]
    budget_justification_score: float
    issues: List[ValidationIssue]

@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""
    grant_id: str
    funder_name: str
    validation_timestamp: datetime
    overall_score: float  # 0-100
    issues: List[ValidationIssue]
    budget_validation: Optional[BudgetValidation]
    content_compliance: Dict[str, ValidationResult]
    recommendations: List[str]
    auto_fixes_applied: List[str]

class AzureMCPValidationTools:
    """MCP Validation Tools powered by Azure AI services"""
    
    def __init__(self):
        # Azure AI services configuration (using your credits)
        self.language_endpoint = os.getenv('AZURE_LANGUAGE_ENDPOINT', '')
        self.language_key = os.getenv('AZURE_LANGUAGE_KEY', '')
        self.qa_endpoint = os.getenv('AZURE_QA_ENDPOINT', '')
        self.qa_key = os.getenv('AZURE_QA_KEY', '')
        
        # Initialize Azure AI clients
        self.text_analytics_client = None
        self.qa_client = None
        
        # Compliance rules database (loaded from Azure or local)
        self.compliance_rules = self._load_compliance_rules()
        self.budget_rules = self._load_budget_rules()
        
        self._initialize_azure_services()
    
    def _initialize_azure_services(self):
        """Initialize Azure AI services for validation"""
        try:
            # Azure AI Language for text analysis (covered by credits)
            if self.language_endpoint and self.language_key:
                credential = AzureKeyCredential(self.language_key)
                self.text_analytics_client = TextAnalyticsClient(
                    endpoint=self.language_endpoint,
                    credential=credential
                )
                print("✅ Azure AI Language initialized for content analysis")
            
            # Azure AI Question Answering for compliance checking (covered by credits)  
            if self.qa_endpoint and self.qa_key:
                credential = AzureKeyCredential(self.qa_key)
                self.qa_client = QuestionAnsweringClient(
                    endpoint=self.qa_endpoint,
                    credential=credential
                )
                print("✅ Azure AI Question Answering initialized for compliance")
                
        except Exception as e:
            print(f"⚠️ Warning: Some Azure validation services not available: {e}")
    
    def validate_budget(self, budget_data: Dict[str, Any], funder_requirements: Dict[str, Any]) -> BudgetValidation:
        """
        MCP Tool: Comprehensive Budget Validation
        Uses advanced financial analysis and Azure AI
        """
        print(f"💰 Validating budget for {funder_requirements.get('funder_name', 'Unknown Funder')}")
        
        issues = []
        
        # Extract budget components
        total_budget = Decimal(str(budget_data.get('total', 0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        budget_breakdown = {}
        
        for category, amount in budget_data.get('breakdown', {}).items():
            budget_breakdown[category] = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Check funding limits
        funding_limit = None
        within_limits = True
        
        if 'max_funding' in funder_requirements:
            funding_limit = Decimal(str(funder_requirements['max_funding']))
            if total_budget > funding_limit:
                within_limits = False
                issues.append(ValidationIssue(
                    category=ComplianceCategory.BUDGET_LIMITS,
                    severity=ValidationResult.FAIL,
                    description=f"Budget ${total_budget:,} exceeds maximum funding limit",
                    recommendation=f"Reduce budget to ${funding_limit:,} or below",
                    current_value=str(total_budget),
                    expected_value=str(funding_limit),
                    auto_fixable=False
                ))
        
        # Validate budget breakdown ratios
        issues.extend(self._validate_budget_ratios(budget_breakdown, funder_requirements))
        
        # Check required budget categories
        issues.extend(self._validate_required_categories(budget_breakdown, funder_requirements))
        
        # Calculate cost per deliverable
        cost_per_deliverable = self._calculate_cost_per_deliverable(
            total_budget, budget_data.get('deliverables', [])
        )
        
        # Budget justification analysis using Azure AI
        justification_score = self._analyze_budget_justification(
            budget_data.get('justification', ''), budget_breakdown
        )
        
        return BudgetValidation(
            total_budget=total_budget,
            budget_breakdown=budget_breakdown,
            funding_limit=funding_limit,
            within_limits=within_limits,
            cost_per_deliverable=cost_per_deliverable,
            budget_justification_score=justification_score,
            issues=issues
        )
    
    def validate_compliance(self, grant_content: Dict[str, Any], 
                          funder_requirements: Dict[str, Any]) -> ComplianceReport:
        """
        MCP Tool: Comprehensive Compliance Validation
        Uses Azure AI services for intelligent compliance checking
        """
        print(f"📋 Validating compliance for {funder_requirements.get('funder_name', 'Unknown Funder')}")
        
        grant_id = grant_content.get('id', f"grant_{int(datetime.now().timestamp())}")
        funder_name = funder_requirements.get('funder_name', 'Unknown')
        
        all_issues = []
        content_compliance = {}
        auto_fixes_applied = []
        
        # 1. Content Requirements Validation
        content_issues, content_scores = self._validate_content_requirements(
            grant_content, funder_requirements
        )
        all_issues.extend(content_issues)
        content_compliance.update(content_scores)
        
        # 2. Formatting Validation
        format_issues, format_fixes = self._validate_formatting(
            grant_content, funder_requirements
        )
        all_issues.extend(format_issues)
        auto_fixes_applied.extend(format_fixes)
        
        # 3. Eligibility Validation using Azure AI
        eligibility_issues = self._validate_eligibility(
            grant_content, funder_requirements
        )
        all_issues.extend(eligibility_issues)
        
        # 4. Deadline Validation
        deadline_issues = self._validate_deadlines(
            grant_content, funder_requirements
        )
        all_issues.extend(deadline_issues)
        
        # 5. Documentation Completeness
        doc_issues = self._validate_documentation(
            grant_content, funder_requirements
        )
        all_issues.extend(doc_issues)
        
        # 6. Budget Validation (if budget data provided)
        budget_validation = None
        if 'budget' in grant_content:
            budget_validation = self.validate_budget(
                grant_content['budget'], funder_requirements
            )
            all_issues.extend(budget_validation.issues)
        
        # Calculate overall compliance score
        overall_score = self._calculate_compliance_score(all_issues, content_compliance)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_issues)
        
        return ComplianceReport(
            grant_id=grant_id,
            funder_name=funder_name,
            validation_timestamp=datetime.now(),
            overall_score=overall_score,
            issues=all_issues,
            budget_validation=budget_validation,
            content_compliance=content_compliance,
            recommendations=recommendations,
            auto_fixes_applied=auto_fixes_applied
        )
    
    def quick_compliance_check(self, text_content: str, funder_name: str) -> Dict[str, Any]:
        """
        MCP Tool: Quick Compliance Check
        Fast validation using Azure AI Language services
        """
        print(f"⚡ Quick compliance check for {funder_name}")
        
        results = {
            "funder": funder_name,
            "timestamp": datetime.now().isoformat(),
            "text_length": len(text_content),
            "issues": [],
            "score": 0.0
        }
        
        try:
            if self.text_analytics_client:
                # Use Azure AI for key phrase extraction and sentiment
                documents = [{"id": "1", "text": text_content[:5000]}]  # Limit for API
                
                # Extract key phrases
                key_phrases_result = self.text_analytics_client.extract_key_phrases(documents)
                key_phrases = []
                for doc in key_phrases_result:
                    if not doc.is_error:
                        key_phrases.extend(doc.key_phrases)
                
                # Analyze sentiment (professional tone check)
                sentiment_result = self.text_analytics_client.analyze_sentiment(documents)
                sentiment_score = 0.5  # neutral default
                
                for doc in sentiment_result:
                    if not doc.is_error:
                        sentiment_scores = doc.confidence_scores
                        # Professional grants should be neutral to slightly positive
                        if sentiment_scores.positive > 0.7:
                            sentiment_score = 0.9
                        elif sentiment_scores.neutral > 0.5:
                            sentiment_score = 0.8
                        else:
                            sentiment_score = 0.6
                
                # Quick compliance checks
                compliance_score = self._quick_compliance_analysis(
                    text_content, key_phrases, funder_name
                )
                
                results["key_phrases"] = key_phrases[:10]  # Top 10
                results["sentiment_score"] = sentiment_score
                results["compliance_score"] = compliance_score
                results["score"] = (sentiment_score + compliance_score) / 2
                
                print(f"✅ Quick check complete - Score: {results['score']:.2f}")
                
        except Exception as e:
            print(f"❌ Quick compliance check error: {e}")
            results["error"] = str(e)
        
        return results
    
    def validate_budget_math(self, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Tool: Mathematical Budget Validation
        Precise financial calculations and consistency checks
        """
        print("🔢 Validating budget mathematics")
        
        validation = {
            "timestamp": datetime.now().isoformat(),
            "math_errors": [],
            "inconsistencies": [],
            "calculations": {},
            "total_valid": False
        }
        
        try:
            breakdown = budget_data.get('breakdown', {})
            stated_total = Decimal(str(budget_data.get('total', 0)))
            
            # Calculate actual total from breakdown
            calculated_total = sum(Decimal(str(amount)) for amount in breakdown.values())
            
            validation["calculations"]["stated_total"] = float(stated_total)
            validation["calculations"]["calculated_total"] = float(calculated_total)
            validation["calculations"]["difference"] = float(abs(stated_total - calculated_total))
            
            # Check if totals match (allowing for small rounding differences)
            if abs(stated_total - calculated_total) > Decimal('0.02'):
                validation["math_errors"].append({
                    "type": "total_mismatch",
                    "description": f"Stated total ${stated_total} doesn't match calculated total ${calculated_total}",
                    "severity": "high"
                })
            else:
                validation["total_valid"] = True
            
            # Check for reasonable percentages
            for category, amount in breakdown.items():
                percentage = (Decimal(str(amount)) / calculated_total * 100) if calculated_total > 0 else 0
                validation["calculations"][f"{category}_percentage"] = float(percentage)
                
                # Flag unusual percentages
                if percentage > 70:
                    validation["inconsistencies"].append({
                        "category": category,
                        "issue": f"Unusually high percentage: {percentage:.1f}%",
                        "recommendation": "Consider redistributing budget"
                    })
            
            print(f"✅ Budget math validation complete - {len(validation['math_errors'])} errors found")
            
        except Exception as e:
            validation["error"] = str(e)
            print(f"❌ Budget math validation error: {e}")
        
        return validation
    
    def _validate_budget_ratios(self, breakdown: Dict[str, Decimal], requirements: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate budget category ratios against funder requirements"""
        issues = []
        
        total = sum(breakdown.values())
        if total == 0:
            return issues
        
        # Check common ratio requirements
        ratio_rules = requirements.get('budget_ratios', {})
        
        for category, limits in ratio_rules.items():
            if category in breakdown:
                percentage = (breakdown[category] / total) * 100
                
                if 'max_percentage' in limits and percentage > limits['max_percentage']:
                    issues.append(ValidationIssue(
                        category=ComplianceCategory.BUDGET_LIMITS,
                        severity=ValidationResult.WARNING,
                        description=f"{category} budget ({percentage:.1f}%) exceeds recommended maximum ({limits['max_percentage']}%)",
                        recommendation=f"Reduce {category} to {limits['max_percentage']}% or below",
                        field=category,
                        current_value=f"{percentage:.1f}%",
                        expected_value=f"≤{limits['max_percentage']}%"
                    ))
                
                if 'min_percentage' in limits and percentage < limits['min_percentage']:
                    issues.append(ValidationIssue(
                        category=ComplianceCategory.BUDGET_LIMITS,
                        severity=ValidationResult.WARNING,
                        description=f"{category} budget ({percentage:.1f}%) below recommended minimum ({limits['min_percentage']}%)",
                        recommendation=f"Increase {category} to {limits['min_percentage']}% or above",
                        field=category,
                        current_value=f"{percentage:.1f}%",
                        expected_value=f"≥{limits['min_percentage']}%"
                    ))
        
        return issues
    
    def _validate_required_categories(self, breakdown: Dict[str, Decimal], requirements: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate required budget categories are present"""
        issues = []
        
        required_categories = requirements.get('required_budget_categories', [])
        
        for category in required_categories:
            if category not in breakdown or breakdown[category] <= 0:
                issues.append(ValidationIssue(
                    category=ComplianceCategory.BUDGET_LIMITS,
                    severity=ValidationResult.FAIL,
                    description=f"Required budget category '{category}' is missing or has zero allocation",
                    recommendation=f"Add budget allocation for {category}",
                    field=category,
                    auto_fixable=False
                ))
        
        return issues
    
    def _calculate_cost_per_deliverable(self, total_budget: Decimal, deliverables: List[str]) -> Dict[str, Decimal]:
        """Calculate cost per deliverable"""
        if not deliverables:
            return {}
        
        cost_per_deliverable = total_budget / len(deliverables)
        return {deliverable: cost_per_deliverable for deliverable in deliverables}
    
    def _analyze_budget_justification(self, justification: str, breakdown: Dict[str, Decimal]) -> float:
        """Analyze budget justification quality using Azure AI"""
        if not justification:
            return 0.0
        
        try:
            if self.text_analytics_client:
                # Use Azure AI to analyze justification quality
                documents = [{"id": "1", "text": justification}]
                
                # Extract key phrases to check coverage of budget categories
                key_phrases_result = self.text_analytics_client.extract_key_phrases(documents)
                key_phrases = []
                for doc in key_phrases_result:
                    if not doc.is_error:
                        key_phrases.extend(doc.key_phrases)
                
                # Score based on how well justification covers budget categories
                coverage_score = 0.0
                for category in breakdown.keys():
                    if any(category.lower() in phrase.lower() for phrase in key_phrases):
                        coverage_score += 1
                
                if len(breakdown) > 0:
                    coverage_score = coverage_score / len(breakdown)
                
                # Length and detail score (should be substantial but not excessive)
                length_score = min(len(justification) / 1000, 1.0)  # Optimal around 1000 chars
                
                return (coverage_score * 0.7 + length_score * 0.3)
            else:
                # Simple fallback scoring
                return min(len(justification) / 500, 1.0)
                
        except Exception as e:
            print(f"⚠️ Budget justification analysis error: {e}")
            return 0.5
    
    def _validate_content_requirements(self, content: Dict[str, Any], requirements: Dict[str, Any]) -> Tuple[List[ValidationIssue], Dict[str, ValidationResult]]:
        """Validate content against requirements using Azure AI"""
        issues = []
        scores = {}
        
        required_sections = requirements.get('required_sections', [])
        
        for section in required_sections:
            if section not in content or not content[section]:
                issues.append(ValidationIssue(
                    category=ComplianceCategory.CONTENT_REQUIREMENTS,
                    severity=ValidationResult.FAIL,
                    description=f"Required section '{section}' is missing or empty",
                    recommendation=f"Add content for {section} section",
                    field=section
                ))
                scores[section] = ValidationResult.FAIL
            else:
                # Validate section content quality
                section_content = str(content[section])
                min_words = requirements.get('min_words', {}).get(section, 50)
                
                word_count = len(section_content.split())
                if word_count < min_words:
                    issues.append(ValidationIssue(
                        category=ComplianceCategory.CONTENT_REQUIREMENTS,
                        severity=ValidationResult.WARNING,
                        description=f"Section '{section}' has {word_count} words, minimum {min_words} required",
                        recommendation=f"Expand {section} section to at least {min_words} words",
                        field=section,
                        current_value=str(word_count),
                        expected_value=f"≥{min_words}"
                    ))
                    scores[section] = ValidationResult.WARNING
                else:
                    scores[section] = ValidationResult.PASS
        
        return issues, scores
    
    def _validate_formatting(self, content: Dict[str, Any], requirements: Dict[str, Any]) -> Tuple[List[ValidationIssue], List[str]]:
        """Validate formatting requirements"""
        issues = []
        auto_fixes = []
        
        format_rules = requirements.get('formatting', {})
        
        # Check page/word limits
        if 'max_pages' in format_rules:
            # Estimate pages (rough calculation)
            total_words = sum(len(str(value).split()) for value in content.values() if isinstance(value, str))
            estimated_pages = total_words / 500  # ~500 words per page
            
            if estimated_pages > format_rules['max_pages']:
                issues.append(ValidationIssue(
                    category=ComplianceCategory.FORMATTING,
                    severity=ValidationResult.FAIL,
                    description=f"Estimated {estimated_pages:.1f} pages exceeds {format_rules['max_pages']} page limit",
                    recommendation=f"Reduce content to fit within {format_rules['max_pages']} pages",
                    current_value=f"{estimated_pages:.1f} pages",
                    expected_value=f"≤{format_rules['max_pages']} pages"
                ))
        
        return issues, auto_fixes
    
    def _validate_eligibility(self, content: Dict[str, Any], requirements: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate eligibility requirements using Azure AI"""
        issues = []
        
        eligibility_criteria = requirements.get('eligibility', [])
        
        for criterion in eligibility_criteria:
            # Use simple keyword matching (can be enhanced with Azure AI)
            criterion_met = any(
                criterion.lower() in str(value).lower() 
                for value in content.values() 
                if isinstance(value, str)
            )
            
            if not criterion_met:
                issues.append(ValidationIssue(
                    category=ComplianceCategory.ELIGIBILITY,
                    severity=ValidationResult.WARNING,
                    description=f"Eligibility criterion may not be addressed: {criterion}",
                    recommendation=f"Ensure application clearly addresses: {criterion}",
                    field="eligibility"
                ))
        
        return issues
    
    def _validate_deadlines(self, content: Dict[str, Any], requirements: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate deadline requirements"""
        issues = []
        
        deadline = requirements.get('deadline')
        if deadline:
            deadline_date = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
            days_remaining = (deadline_date - datetime.now()).days
            
            if days_remaining < 0:
                issues.append(ValidationIssue(
                    category=ComplianceCategory.DEADLINES,
                    severity=ValidationResult.FAIL,
                    description="Application deadline has passed",
                    recommendation="Cannot submit - deadline expired",
                    current_value=datetime.now().strftime("%Y-%m-%d"),
                    expected_value=deadline_date.strftime("%Y-%m-%d")
                ))
            elif days_remaining < 7:
                issues.append(ValidationIssue(
                    category=ComplianceCategory.DEADLINES,
                    severity=ValidationResult.WARNING,
                    description=f"Only {days_remaining} days remaining until deadline",
                    recommendation="Review and submit application urgently",
                    current_value=f"{days_remaining} days",
                    expected_value="≥7 days recommended"
                ))
        
        return issues
    
    def _validate_documentation(self, content: Dict[str, Any], requirements: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate required documentation"""
        issues = []
        
        required_docs = requirements.get('required_documents', [])
        provided_docs = content.get('attachments', [])
        
        for doc_type in required_docs:
            if not any(doc_type.lower() in doc.lower() for doc in provided_docs):
                issues.append(ValidationIssue(
                    category=ComplianceCategory.DOCUMENTATION,
                    severity=ValidationResult.FAIL,
                    description=f"Required document missing: {doc_type}",
                    recommendation=f"Attach {doc_type} document",
                    field="attachments"
                ))
        
        return issues
    
    def _calculate_compliance_score(self, issues: List[ValidationIssue], content_scores: Dict[str, ValidationResult]) -> float:
        """Calculate overall compliance score"""
        total_score = 100.0
        
        # Deduct points based on issue severity
        for issue in issues:
            if issue.severity == ValidationResult.FAIL:
                total_score -= 20
            elif issue.severity == ValidationResult.WARNING:
                total_score -= 10
            elif issue.severity == ValidationResult.ERROR:
                total_score -= 30
        
        # Bonus points for content that passes
        pass_count = sum(1 for score in content_scores.values() if score == ValidationResult.PASS)
        total_content = len(content_scores) if content_scores else 1
        content_bonus = (pass_count / total_content) * 20
        
        final_score = max(0, total_score + content_bonus)
        return min(100, final_score)
    
    def _generate_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Group by severity
        critical_issues = [i for i in issues if i.severity == ValidationResult.FAIL]
        warning_issues = [i for i in issues if i.severity == ValidationResult.WARNING]
        
        if critical_issues:
            recommendations.append(f"🚨 CRITICAL: Fix {len(critical_issues)} failing requirements before submission")
            for issue in critical_issues[:3]:  # Top 3 critical
                recommendations.append(f"  • {issue.recommendation}")
        
        if warning_issues:
            recommendations.append(f"⚠️ Address {len(warning_issues)} warnings to improve application quality")
        
        if not critical_issues and not warning_issues:
            recommendations.append("✅ Application meets all compliance requirements")
        
        return recommendations
    
    def _quick_compliance_analysis(self, text: str, key_phrases: List[str], funder: str) -> float:
        """Quick compliance analysis based on keywords and patterns"""
        score = 0.5  # baseline
        
        # Check for grant-specific keywords
        grant_keywords = ['objective', 'methodology', 'budget', 'timeline', 'deliverable', 'impact']
        found_keywords = sum(1 for keyword in grant_keywords if keyword in text.lower())
        keyword_score = found_keywords / len(grant_keywords)
        
        # Check text structure (paragraphs, organization)
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        structure_score = min(paragraph_count / 5, 1.0)  # Good structure has 5+ paragraphs
        
        # Combine scores
        score = (keyword_score * 0.6 + structure_score * 0.4)
        
        return score
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules (from Azure or local storage)"""
        # This would typically load from Azure Cognitive Search or Cosmos DB
        # For now, return basic rules structure
        return {
            "NSF": {
                "required_sections": ["abstract", "project_description", "budget", "timeline"],
                "max_pages": 15,
                "budget_ratios": {
                    "personnel": {"max_percentage": 70},
                    "equipment": {"max_percentage": 30},
                    "indirect": {"max_percentage": 25}
                }
            },
            "NIH": {
                "required_sections": ["specific_aims", "research_strategy", "budget"],
                "max_pages": 12,
                "budget_ratios": {
                    "personnel": {"max_percentage": 75},
                    "indirect": {"max_percentage": 30}
                }
            }
        }
    
    def _load_budget_rules(self) -> Dict[str, Any]:
        """Load budget-specific validation rules"""
        return {
            "common_categories": ["personnel", "equipment", "supplies", "travel", "indirect"],
            "percentage_limits": {
                "indirect": 30,
                "travel": 10,
                "equipment": 40
            },
            "required_justifications": ["personnel", "equipment", "supplies"]
        }

# MCP Validation Tool Registry
VALIDATION_TOOLS = {
    "validate_budget": {
        "name": "Budget Validation",
        "description": "Comprehensive budget validation with mathematical checks",
        "azure_service": "AI Language + Local calculations",
        "cost": "$0.01-0.05 per validation"
    },
    
    "validate_compliance": {
        "name": "Compliance Validation",
        "description": "Full compliance check against funder requirements",
        "azure_service": "AI Language + Question Answering",
        "cost": "$0.05-0.15 per validation"
    },
    
    "quick_check": {
        "name": "Quick Compliance Check",
        "description": "Fast validation using AI text analysis",
        "azure_service": "AI Language",
        "cost": "$0.01-0.03 per check"
    },
    
    "budget_math": {
        "name": "Budget Math Validation",
        "description": "Mathematical accuracy of budget calculations",
        "azure_service": "Local calculations",
        "cost": "$0.001 per validation"
    }
}

def create_validation_tools():
    """Initialize Azure-powered MCP validation tools"""
    tools = AzureMCPValidationTools()
    
    print("✅ Azure MCP Validation Tools initialized:")
    for tool_name, tool_info in VALIDATION_TOOLS.items():
        print(f"  ✅ {tool_info['name']} - {tool_info['azure_service']}")
    
    return tools

if __name__ == "__main__":
    # Test validation tools
    tools = create_validation_tools()
    
    print("🧪 Testing Azure MCP Validation Tools...")
    
    # Test budget validation
    sample_budget = {
        "total": 150000,
        "breakdown": {
            "personnel": 90000,
            "equipment": 30000,
            "supplies": 15000,
            "travel": 10000,
            "indirect": 5000
        },
        "justification": "Personnel costs include PI salary and graduate student support...",
        "deliverables": ["Research report", "Software prototype", "Publications"]
    }
    
    sample_requirements = {
        "funder_name": "NSF",
        "max_funding": 200000,
        "budget_ratios": {
            "personnel": {"max_percentage": 70},
            "indirect": {"max_percentage": 25}
        }
    }
    
    budget_result = tools.validate_budget(sample_budget, sample_requirements)
    print(f"✅ Budget validation complete - {len(budget_result.issues)} issues found")
    
    # Test quick compliance check
    sample_text = "This project aims to develop innovative AI algorithms for healthcare applications..."
    quick_result = tools.quick_compliance_check(sample_text, "NSF")
    print(f"✅ Quick compliance check complete - Score: {quick_result['score']:.2f}")
    
    print("🚀 Azure MCP Validation Tools ready!")