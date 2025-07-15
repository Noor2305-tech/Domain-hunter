from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DomainStatus(Enum):
    DISCOVERED = "discovered"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    HIGH_VALUE = "high_value"
    SPAM = "spam"
    ERROR = "error"

@dataclass
class Domain:
    id: Optional[int] = None
    name: str = ""
    discovered_at: Optional[datetime] = None
    score: float = 0.0
    status: DomainStatus = DomainStatus.DISCOVERED
    notes: str = ""

@dataclass
class SEOMetrics:
    id: Optional[int] = None
    domain_id: Optional[int] = None
    domain_authority: Optional[int] = None
    page_authority: Optional[int] = None
    backlinks: Optional[int] = None
    referring_domains: Optional[int] = None
    organic_traffic: Optional[int] = None
    trust_flow: Optional[int] = None
    citation_flow: Optional[int] = None
    spam_score: Optional[int] = None
    analyzed_at: Optional[datetime] = None

@dataclass
class ContentAnalysis:
    id: Optional[int] = None
    domain_id: Optional[int] = None
    niche: str = ""
    content_quality: Optional[int] = None
    spam_score: Optional[int] = None
    brandability_score: Optional[int] = None
    historical_content: str = ""
    keywords: List[str] = None
    analyzed_at: Optional[datetime] = None
    language: str = "unknown"
    readability: Optional[int] = None
    sentiment: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.sentiment is None:
            self.sentiment = {}

@dataclass
class HistoricalData:
    id: Optional[int] = None
    domain_id: Optional[int] = None
    snapshot_date: str = ""
    title: str = ""
    content: str = ""
    language: str = "en"

@dataclass
class DomainAnalysisResult:
    domain: Domain
    seo_metrics: Optional[SEOMetrics] = None
    content_analysis: Optional[ContentAnalysis] = None
    historical_data: List[HistoricalData] = None
    
    def __post_init__(self):
        if self.historical_data is None:
            self.historical_data = []

@dataclass
class ScoreBreakdown:
    domain_name: str
    overall_score: float
    seo_score: float
    content_score: float
    brandability_score: float
    spam_penalty: float
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

@dataclass
class DomainValueEstimate:
    domain_name: str
    estimated_value: float
    value_range: str
    confidence: float = 0.0
    value_components: Dict[str, float] = None
    
    def __post_init__(self):
        if self.value_components is None:
            self.value_components = {}

@dataclass
class FilterCriteria:
    min_score: float = 0.0
    max_score: float = 100.0
    min_domain_authority: int = 0
    max_domain_authority: int = 100
    min_backlinks: int = 0
    max_backlinks: int = 1000000
    min_referring_domains: int = 0
    max_referring_domains: int = 10000
    niches: List[str] = None
    exclude_spam: bool = True
    min_content_quality: int = 0
    max_spam_score: int = 100
    
    def __post_init__(self):
        if self.niches is None:
            self.niches = []

@dataclass
class AnalysisSettings:
    enable_seo_analysis: bool = True
    enable_content_analysis: bool = True
    enable_historical_analysis: bool = True
    enable_spam_detection: bool = True
    max_domains_per_batch: int = 50
    api_timeout: int = 30
    enable_mock_data: bool = True
    
    # Scoring weights
    seo_weight: float = 0.4
    content_weight: float = 0.3
    brandability_weight: float = 0.2
    spam_penalty_weight: float = 0.1

@dataclass
class APIConfiguration:
    ahrefs_api_key: str = ""
    moz_api_key: str = ""
    majestic_api_key: str = ""
    semrush_api_key: str = ""
    wayback_api_timeout: int = 30
    rate_limit_delay: float = 1.0
    max_retries: int = 3

@dataclass
class ProcessingStats:
    total_domains: int = 0
    processed_domains: int = 0
    successful_analyses: int = 0
    failed_analyses: int = 0
    high_value_domains: int = 0
    spam_domains: int = 0
    processing_time: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class NicheInfo:
    name: str
    keywords: List[str]
    value_multiplier: float = 1.0
    spam_indicators: List[str] = None
    
    def __post_init__(self):
        if self.spam_indicators is None:
            self.spam_indicators = []

# Predefined niche configurations
NICHE_CONFIGS = {
    'Technology': NicheInfo(
        name='Technology',
        keywords=['technology', 'software', 'programming', 'development', 'tech', 'app', 'digital', 'code', 'computer', 'internet'],
        value_multiplier=1.5,
        spam_indicators=['cheap software', 'cracked', 'free download']
    ),
    'Health': NicheInfo(
        name='Health',
        keywords=['health', 'medical', 'fitness', 'wellness', 'nutrition', 'doctor', 'medicine', 'healthcare', 'diet', 'exercise'],
        value_multiplier=1.8,
        spam_indicators=['miracle cure', 'lose weight fast', 'guaranteed results']
    ),
    'Finance': NicheInfo(
        name='Finance',
        keywords=['finance', 'money', 'investment', 'banking', 'trading', 'cryptocurrency', 'financial', 'loan', 'credit', 'insurance'],
        value_multiplier=2.0,
        spam_indicators=['get rich quick', 'guaranteed profit', 'no risk']
    ),
    'Travel': NicheInfo(
        name='Travel',
        keywords=['travel', 'vacation', 'hotel', 'flight', 'tourism', 'destination', 'trip', 'adventure', 'explore', 'journey'],
        value_multiplier=1.1,
        spam_indicators=['cheapest deals', 'too good to be true']
    ),
    'Education': NicheInfo(
        name='Education',
        keywords=['education', 'learning', 'school', 'university', 'course', 'student', 'teaching', 'academic', 'study', 'knowledge'],
        value_multiplier=1.2,
        spam_indicators=['fake degree', 'buy diploma', 'instant certification']
    ),
    'Entertainment': NicheInfo(
        name='Entertainment',
        keywords=['entertainment', 'movie', 'music', 'game', 'celebrity', 'news', 'sports', 'fun', 'show', 'media'],
        value_multiplier=1.0,
        spam_indicators=['free movies', 'illegal download', 'pirated']
    ),
    'Business': NicheInfo(
        name='Business',
        keywords=['business', 'entrepreneur', 'startup', 'company', 'marketing', 'sales', 'corporate', 'management', 'strategy', 'success'],
        value_multiplier=1.3,
        spam_indicators=['make money fast', 'no experience required', 'overnight success']
    ),
    'Food': NicheInfo(
        name='Food',
        keywords=['food', 'recipe', 'cooking', 'restaurant', 'cuisine', 'chef', 'meal', 'ingredients', 'kitchen', 'dining'],
        value_multiplier=1.0,
        spam_indicators=['lose weight eating', 'magic ingredient']
    ),
    'Fashion': NicheInfo(
        name='Fashion',
        keywords=['fashion', 'style', 'clothing', 'designer', 'trend', 'outfit', 'beauty', 'accessories', 'brand', 'wardrobe'],
        value_multiplier=1.2,
        spam_indicators=['fake designer', 'replica', 'knockoff']
    )
}

@dataclass
class DomainDiscoveryConfig:
    max_pages_per_source: int = 3
    max_domains_per_run: int = 100
    sources: List[str] = None
    enable_expired_domains: bool = True
    enable_auction_domains: bool = True
    enable_parked_domains: bool = False
    min_domain_age: int = 1
    max_domain_age: int = 20
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = ['expireddomains.net', 'sample_data']

# Utility functions for models
def create_domain_from_dict(data: Dict[str, Any]) -> Domain:
    """Create Domain object from dictionary"""
    return Domain(
        id=data.get('id'),
        name=data.get('name', ''),
        discovered_at=data.get('discovered_at'),
        score=data.get('score', 0.0),
        status=DomainStatus(data.get('status', 'discovered')),
        notes=data.get('notes', '')
    )

def create_seo_metrics_from_dict(data: Dict[str, Any]) -> SEOMetrics:
    """Create SEOMetrics object from dictionary"""
    return SEOMetrics(
        id=data.get('id'),
        domain_id=data.get('domain_id'),
        domain_authority=data.get('domain_authority'),
        page_authority=data.get('page_authority'),
        backlinks=data.get('backlinks'),
        referring_domains=data.get('referring_domains'),
        organic_traffic=data.get('organic_traffic'),
        trust_flow=data.get('trust_flow'),
        citation_flow=data.get('citation_flow'),
        spam_score=data.get('spam_score'),
        analyzed_at=data.get('analyzed_at')
    )

def create_content_analysis_from_dict(data: Dict[str, Any]) -> ContentAnalysis:
    """Create ContentAnalysis object from dictionary"""
    return ContentAnalysis(
        id=data.get('id'),
        domain_id=data.get('domain_id'),
        niche=data.get('niche', ''),
        content_quality=data.get('content_quality'),
        spam_score=data.get('spam_score'),
        brandability_score=data.get('brandability_score'),
        historical_content=data.get('historical_content', ''),
        keywords=data.get('keywords', []),
        analyzed_at=data.get('analyzed_at'),
        language=data.get('language', 'unknown'),
        readability=data.get('readability'),
        sentiment=data.get('sentiment', {})
    )

def domain_to_dict(domain: Domain) -> Dict[str, Any]:
    """Convert Domain object to dictionary"""
    return {
        'id': domain.id,
        'name': domain.name,
        'discovered_at': domain.discovered_at,
        'score': domain.score,
        'status': domain.status.value,
        'notes': domain.notes
    }

def seo_metrics_to_dict(metrics: SEOMetrics) -> Dict[str, Any]:
    """Convert SEOMetrics object to dictionary"""
    return {
        'id': metrics.id,
        'domain_id': metrics.domain_id,
        'domain_authority': metrics.domain_authority,
        'page_authority': metrics.page_authority,
        'backlinks': metrics.backlinks,
        'referring_domains': metrics.referring_domains,
        'organic_traffic': metrics.organic_traffic,
        'trust_flow': metrics.trust_flow,
        'citation_flow': metrics.citation_flow,
        'spam_score': metrics.spam_score,
        'analyzed_at': metrics.analyzed_at
    }

def content_analysis_to_dict(analysis: ContentAnalysis) -> Dict[str, Any]:
    """Convert ContentAnalysis object to dictionary"""
    return {
        'id': analysis.id,
        'domain_id': analysis.domain_id,
        'niche': analysis.niche,
        'content_quality': analysis.content_quality,
        'spam_score': analysis.spam_score,
        'brandability_score': analysis.brandability_score,
        'historical_content': analysis.historical_content,
        'keywords': analysis.keywords,
        'analyzed_at': analysis.analyzed_at,
        'language': analysis.language,
        'readability': analysis.readability,
        'sentiment': analysis.sentiment
    }
