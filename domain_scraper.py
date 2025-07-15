import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any
import random
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class DomainScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_expired_domains(self, max_pages: int = 3) -> List[str]:
        """Scrape expired domains from public sources"""
        domains = []
        
        try:
            # Source 1: ExpiredDomains.net (demo scraping)
            domains.extend(self._scrape_expired_domains_net(max_pages))
            
            # Source 2: Sample domains for development
            domains.extend(self._get_sample_domains())
            
        except Exception as e:
            logger.error(f"Error scraping expired domains: {str(e)}")
            # Return sample domains if scraping fails
            domains = self._get_sample_domains()
        
        return list(set(domains))  # Remove duplicates
    
    def scrape_auction_domains(self, max_pages: int = 2) -> List[str]:
        """Scrape domains from auction sites"""
        domains = []
        
        try:
            # For development, return sample auction domains
            domains = self._get_sample_auction_domains()
            
        except Exception as e:
            logger.error(f"Error scraping auction domains: {str(e)}")
            domains = self._get_sample_auction_domains()
        
        return list(set(domains))
    
    def _scrape_expired_domains_net(self, max_pages: int = 3) -> List[str]:
        """Scrape from ExpiredDomains.net"""
        domains = []
        
        try:
            for page in range(1, max_pages + 1):
                url = f"https://www.expireddomains.net/expired-domains/?start={page * 25}"
                
                try:
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for domain links in the table
                    domain_links = soup.find_all('a', href=re.compile(r'domain\.com'))
                    
                    for link in domain_links:
                        domain = link.get('href', '').replace('http://', '').replace('https://', '')
                        if domain and self._is_valid_domain(domain):
                            domains.append(domain)
                    
                    # Add delay between requests
                    time.sleep(random.uniform(1, 3))
                    
                except requests.RequestException as e:
                    logger.warning(f"Error scraping page {page}: {str(e)}")
                    continue
                
        except Exception as e:
            logger.error(f"Error in _scrape_expired_domains_net: {str(e)}")
        
        return domains
    
    def _get_sample_domains(self) -> List[str]:
        """Get sample domains for development and testing"""
        return [
            "techblog2023.com",
            "healthtips.net",
            "financeguide.org",
            "travelblog.co",
            "educationhub.info",
            "newstoday.net",
            "sportsfan.com",
            "foodrecipes.org",
            "musicworld.net",
            "artgallery.com",
            "carreview.net",
            "homedesign.org",
            "fashiontrends.com",
            "techreview.net",
            "businesstips.org",
            "gamingworld.com",
            "photoblog.net",
            "moviereview.org",
            "sciencenews.com",
            "historybook.net"
        ]
    
    def _get_sample_auction_domains(self) -> List[str]:
        """Get sample auction domains for development"""
        return [
            "premiumdomain.com",
            "valuablesite.net",
            "brandname.org",
            "keywordrich.com",
            "shortdomain.co",
            "memorabledomain.net",
            "industryname.org",
            "brandableword.com",
            "exactmatch.net",
            "categorykeyword.org"
        ]
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Check if domain is valid format"""
        if not domain:
            return False
        
        # Remove protocol if present
        domain = domain.replace('http://', '').replace('https://', '')
        
        # Remove trailing slash
        domain = domain.rstrip('/')
        
        # Basic domain validation
        domain_pattern = re.compile(
            r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,}|[a-zA-Z]{2,}\.[a-zA-Z]{2,})$'
        )
        
        return bool(domain_pattern.match(domain))
    
    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get basic information about a domain"""
        try:
            # Check if domain is accessible
            url = f"http://{domain}"
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            info = {
                'domain': domain,
                'status_code': response.status_code,
                'accessible': response.status_code == 200,
                'redirect_url': response.url if response.url != url else None,
                'title': None,
                'description': None
            }
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title_tag = soup.find('title')
                if title_tag:
                    info['title'] = title_tag.get_text().strip()
                
                # Extract description
                desc_tag = soup.find('meta', attrs={'name': 'description'})
                if desc_tag:
                    info['description'] = desc_tag.get('content', '').strip()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting domain info for {domain}: {str(e)}")
            return {
                'domain': domain,
                'status_code': None,
                'accessible': False,
                'redirect_url': None,
                'title': None,
                'description': None,
                'error': str(e)
            }
    
    def check_domain_availability(self, domain: str) -> bool:
        """Check if domain is available for registration"""
        try:
            # For development, simulate availability check
            # In production, this would use WHOIS or domain availability APIs
            
            # Simple check: if domain responds, it's likely taken
            url = f"http://{domain}"
            response = self.session.get(url, timeout=5)
            
            # If we get a response, domain is likely taken
            return response.status_code != 200
            
        except requests.RequestException:
            # If we can't connect, domain might be available
            return True
        except Exception as e:
            logger.error(f"Error checking availability for {domain}: {str(e)}")
            return False
    
    def get_domain_whois(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information for a domain"""
        try:
            # For development, return mock WHOIS data
            # In production, this would use a WHOIS library or API
            
            import random
            from datetime import datetime, timedelta
            
            # Mock WHOIS data
            creation_date = datetime.now() - timedelta(days=random.randint(365, 3650))
            expiration_date = datetime.now() + timedelta(days=random.randint(30, 365))
            
            return {
                'domain': domain,
                'creation_date': creation_date.strftime('%Y-%m-%d'),
                'expiration_date': expiration_date.strftime('%Y-%m-%d'),
                'registrar': random.choice(['GoDaddy', 'Namecheap', 'Google Domains', 'Cloudflare']),
                'status': random.choice(['Active', 'Pending Delete', 'Redemption Period']),
                'name_servers': ['ns1.example.com', 'ns2.example.com']
            }
            
        except Exception as e:
            logger.error(f"Error getting WHOIS for {domain}: {str(e)}")
            return {
                'domain': domain,
                'error': str(e)
            }
