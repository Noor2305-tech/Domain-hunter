import requests
import logging
from typing import Dict, Any, Optional
import random
import time
import os
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # API keys from environment variables
        self.ahrefs_api_key = os.getenv('AHREFS_API_KEY')
        self.moz_api_key = os.getenv('MOZ_API_KEY')
        self.majestic_api_key = os.getenv('MAJESTIC_API_KEY')
        self.semrush_api_key = os.getenv('SEMRUSH_API_KEY')
    
    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze SEO metrics for a domain"""
        try:
            logger.info(f"Analyzing SEO metrics for domain: {domain}")
            
            # Try to get real data from APIs, fallback to mock data
            seo_data = {}
            
            # Ahrefs data
            ahrefs_data = self._get_ahrefs_data(domain)
            if ahrefs_data:
                seo_data.update(ahrefs_data)
            
            # Moz data
            moz_data = self._get_moz_data(domain)
            if moz_data:
                seo_data.update(moz_data)
            
            # Majestic data
            majestic_data = self._get_majestic_data(domain)
            if majestic_data:
                seo_data.update(majestic_data)
            
            # Semrush data
            semrush_data = self._get_semrush_data(domain)
            if semrush_data:
                seo_data.update(semrush_data)
            
            # If no real data, use mock data for development
            if not seo_data:
                seo_data = self._get_mock_seo_data(domain)
            
            return seo_data
            
        except Exception as e:
            logger.error(f"Error analyzing domain {domain}: {str(e)}")
            return self._get_mock_seo_data(domain)
    
    def _get_ahrefs_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get data from Ahrefs API"""
        if not self.ahrefs_api_key:
            logger.info("Ahrefs API key not available, using mock data")
            return None
        
        try:
            url = f"https://apiv2.ahrefs.com"
            params = {
                'token': self.ahrefs_api_key,
                'from': 'domain_rating',
                'target': domain,
                'mode': 'domain'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'domain_rating': data.get('domain_rating', 0),
                    'backlinks': data.get('backlinks', 0),
                    'referring_domains': data.get('referring_domains', 0),
                    'organic_traffic': data.get('organic_traffic', 0)
                }
            
        except Exception as e:
            logger.error(f"Error getting Ahrefs data for {domain}: {str(e)}")
        
        return None
    
    def _get_moz_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get data from Moz API"""
        if not self.moz_api_key:
            logger.info("Moz API key not available, using mock data")
            return None
        
        try:
            url = f"https://lsapi.seomoz.com/linkscape/url-metrics/{domain}"
            headers = {
                'Authorization': f'Basic {self.moz_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'domain_authority': data.get('pda', 0),
                    'page_authority': data.get('upa', 0),
                    'spam_score': data.get('spam_score', 0)
                }
            
        except Exception as e:
            logger.error(f"Error getting Moz data for {domain}: {str(e)}")
        
        return None
    
    def _get_majestic_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get data from Majestic API"""
        if not self.majestic_api_key:
            logger.info("Majestic API key not available, using mock data")
            return None
        
        try:
            url = "https://api.majestic.com/api/json"
            params = {
                'app_api_key': self.majestic_api_key,
                'cmd': 'GetIndexItemInfo',
                'items': domain,
                'datasource': 'historic'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Code') == 'OK':
                    item = data.get('DataTables', {}).get('Results', {}).get('Data', [{}])[0]
                    return {
                        'trust_flow': item.get('TrustFlow', 0),
                        'citation_flow': item.get('CitationFlow', 0),
                        'referring_domains': item.get('RefDomains', 0),
                        'backlinks': item.get('ExtBackLinks', 0)
                    }
            
        except Exception as e:
            logger.error(f"Error getting Majestic data for {domain}: {str(e)}")
        
        return None
    
    def _get_semrush_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get data from Semrush API"""
        if not self.semrush_api_key:
            logger.info("Semrush API key not available, using mock data")
            return None
        
        try:
            url = "https://api.semrush.com"
            params = {
                'type': 'domain_overview',
                'key': self.semrush_api_key,
                'domain': domain,
                'export_columns': 'Dn,Rk,Or,Ot,Oc,Ad,At,Ac'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                if len(lines) > 1:
                    data = lines[1].split(';')
                    return {
                        'organic_keywords': int(data[2]) if data[2].isdigit() else 0,
                        'organic_traffic': int(data[3]) if data[3].isdigit() else 0,
                        'organic_cost': float(data[4]) if data[4].replace('.', '').isdigit() else 0.0
                    }
            
        except Exception as e:
            logger.error(f"Error getting Semrush data for {domain}: {str(e)}")
        
        return None
    
    def _get_mock_seo_data(self, domain: str) -> Dict[str, Any]:
        """Generate mock SEO data for development"""
        # Use domain name to create consistent mock data
        domain_hash = hash(domain) % 1000000
        random.seed(domain_hash)
        
        # Generate realistic but random metrics
        domain_authority = random.randint(5, 85)
        page_authority = random.randint(5, min(domain_authority + 15, 95))
        
        # Higher authority domains tend to have more backlinks
        backlinks = random.randint(10, domain_authority * 100)
        referring_domains = random.randint(5, min(backlinks // 10, 1000))
        
        # Trust flow is generally lower than citation flow
        trust_flow = random.randint(5, 60)
        citation_flow = random.randint(trust_flow, min(trust_flow + 20, 80))
        
        # Organic traffic correlates with authority
        organic_traffic = random.randint(0, domain_authority * 50)
        
        # Spam score (lower is better)
        spam_score = random.randint(0, 30)
        
        return {
            'domain_authority': domain_authority,
            'page_authority': page_authority,
            'backlinks': backlinks,
            'referring_domains': referring_domains,
            'organic_traffic': organic_traffic,
            'trust_flow': trust_flow,
            'citation_flow': citation_flow,
            'spam_score': spam_score,
            'organic_keywords': random.randint(10, domain_authority * 20),
            'organic_cost': round(random.uniform(100, domain_authority * 100), 2)
        }
    
    def check_domain_penalties(self, domain: str) -> Dict[str, Any]:
        """Check for potential SEO penalties"""
        try:
            # Mock penalty detection for development
            # In production, this would analyze historical data patterns
            
            penalties = {
                'google_penalty': random.choice([True, False]) if random.random() < 0.1 else False,
                'bing_penalty': random.choice([True, False]) if random.random() < 0.05 else False,
                'manual_action': random.choice([True, False]) if random.random() < 0.03 else False,
                'algorithmic_penalty': random.choice([True, False]) if random.random() < 0.08 else False,
                'penalty_score': random.randint(0, 100)
            }
            
            return penalties
            
        except Exception as e:
            logger.error(f"Error checking penalties for {domain}: {str(e)}")
            return {
                'google_penalty': False,
                'bing_penalty': False,
                'manual_action': False,
                'algorithmic_penalty': False,
                'penalty_score': 0
            }
    
    def get_top_keywords(self, domain: str, limit: int = 10) -> list:
        """Get top organic keywords for a domain"""
        try:
            # Mock keyword data for development
            sample_keywords = [
                'technology', 'software', 'development', 'programming', 'web design',
                'digital marketing', 'SEO', 'content marketing', 'social media',
                'business', 'startup', 'entrepreneur', 'innovation', 'artificial intelligence',
                'machine learning', 'data science', 'cloud computing', 'cybersecurity'
            ]
            
            # Generate keywords based on domain name
            domain_hash = hash(domain) % len(sample_keywords)
            random.seed(domain_hash)
            
            keywords = []
            for i in range(min(limit, len(sample_keywords))):
                keyword = random.choice(sample_keywords)
                keywords.append({
                    'keyword': keyword,
                    'position': random.randint(1, 50),
                    'search_volume': random.randint(100, 10000),
                    'difficulty': random.randint(10, 90)
                })
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error getting keywords for {domain}: {str(e)}")
            return []
    
    def analyze_backlink_profile(self, domain: str) -> Dict[str, Any]:
        """Analyze backlink profile quality"""
        try:
            # Mock backlink analysis for development
            domain_hash = hash(domain) % 1000000
            random.seed(domain_hash)
            
            total_backlinks = random.randint(50, 10000)
            dofollow_ratio = random.uniform(0.3, 0.8)
            
            profile = {
                'total_backlinks': total_backlinks,
                'dofollow_links': int(total_backlinks * dofollow_ratio),
                'nofollow_links': int(total_backlinks * (1 - dofollow_ratio)),
                'unique_domains': random.randint(10, min(total_backlinks // 5, 1000)),
                'government_links': random.randint(0, 10),
                'education_links': random.randint(0, 20),
                'high_authority_links': random.randint(5, 50),
                'spam_links': random.randint(0, max(1, total_backlinks // 100)),
                'link_velocity': random.randint(-50, 100),  # links gained/lost per month
                'anchor_text_diversity': random.uniform(0.2, 0.9)
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Error analyzing backlink profile for {domain}: {str(e)}")
            return {}
