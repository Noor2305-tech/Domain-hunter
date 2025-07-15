import logging
import csv
import io
from typing import List, Dict, Any
from datetime import datetime
import os

def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('domain_hunter.log')
        ]
    )

def export_to_csv(domains: List[Dict[str, Any]]) -> str:
    """Export domain data to CSV format"""
    if not domains:
        return ""
    
    output = io.StringIO()
    
    # Get all possible fieldnames
    fieldnames = set()
    for domain in domains:
        fieldnames.update(domain.keys())
    
    fieldnames = sorted(list(fieldnames))
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for domain in domains:
        # Handle None values
        clean_domain = {k: v if v is not None else '' for k, v in domain.items()}
        writer.writerow(clean_domain)
    
    return output.getvalue()

def validate_domain_name(domain: str) -> bool:
    """Validate domain name format"""
    import re
    
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

def normalize_domain_name(domain: str) -> str:
    """Normalize domain name"""
    if not domain:
        return ""
    
    # Remove protocol
    domain = domain.replace('http://', '').replace('https://', '')
    
    # Remove www
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Remove trailing slash
    domain = domain.rstrip('/')
    
    # Convert to lowercase
    domain = domain.lower()
    
    return domain

def calculate_domain_age(creation_date: str) -> int:
    """Calculate domain age in years"""
    try:
        if not creation_date:
            return 0
        
        # Parse date string (assuming YYYY-MM-DD format)
        created = datetime.strptime(creation_date, '%Y-%m-%d')
        now = datetime.now()
        
        age = (now - created).days // 365
        return max(0, age)
        
    except Exception:
        return 0

def format_number(number: Any) -> str:
    """Format number with thousand separators"""
    try:
        if number is None:
            return "N/A"
        
        num = float(number)
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(int(num))
            
    except (ValueError, TypeError):
        return str(number) if number is not None else "N/A"

def get_score_color(score: float) -> str:
    """Get color based on score"""
    if score >= 80:
        return "green"
    elif score >= 60:
        return "orange"
    elif score >= 40:
        return "yellow"
    else:
        return "red"

def get_score_label(score: float) -> str:
    """Get label based on score"""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Poor"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    import re
    
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def parse_api_response(response_text: str, format_type: str = 'json') -> Any:
    """Parse API response based on format"""
    try:
        if format_type.lower() == 'json':
            import json
            return json.loads(response_text)
        elif format_type.lower() == 'csv':
            lines = response_text.strip().split('\n')
            return [line.split(',') for line in lines]
        else:
            return response_text
            
    except Exception as e:
        logging.error(f"Error parsing API response: {str(e)}")
        return None

def rate_limit_delay(api_name: str, delay: float = 1.0) -> None:
    """Add delay for rate limiting"""
    import time
    
    # Different delays for different APIs
    api_delays = {
        'ahrefs': 2.0,
        'moz': 1.5,
        'majestic': 1.0,
        'semrush': 2.0,
        'wayback': 0.5,
        'default': 1.0
    }
    
    actual_delay = api_delays.get(api_name.lower(), delay)
    time.sleep(actual_delay)

def batch_process(items: List[Any], batch_size: int = 10) -> List[List[Any]]:
    """Split items into batches"""
    batches = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batches.append(batch)
    return batches

def get_environment_config() -> Dict[str, str]:
    """Get environment configuration"""
    return {
        'ahrefs_api_key': os.getenv('AHREFS_API_KEY', ''),
        'moz_api_key': os.getenv('MOZ_API_KEY', ''),
        'majestic_api_key': os.getenv('MAJESTIC_API_KEY', ''),
        'semrush_api_key': os.getenv('SEMRUSH_API_KEY', ''),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'database_path': os.getenv('DATABASE_PATH', 'domain_hunter.db'),
        'max_domains_per_batch': int(os.getenv('MAX_DOMAINS_PER_BATCH', '50')),
        'api_timeout': int(os.getenv('API_TIMEOUT', '30')),
        'enable_mock_data': os.getenv('ENABLE_MOCK_DATA', 'true').lower() == 'true'
    }

def create_summary_report(domains: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create summary report of domain analysis"""
    if not domains:
        return {}
    
    total_domains = len(domains)
    
    # Score distribution
    high_score = sum(1 for d in domains if d.get('score', 0) >= 70)
    medium_score = sum(1 for d in domains if 40 <= d.get('score', 0) < 70)
    low_score = sum(1 for d in domains if d.get('score', 0) < 40)
    
    # Niche distribution
    niches = {}
    for domain in domains:
        niche = domain.get('niche', 'Unknown')
        niches[niche] = niches.get(niche, 0) + 1
    
    # Average metrics
    avg_score = sum(d.get('score', 0) for d in domains) / total_domains
    avg_domain_authority = sum(d.get('domain_authority', 0) for d in domains) / total_domains
    avg_backlinks = sum(d.get('backlinks', 0) for d in domains) / total_domains
    
    return {
        'total_domains': total_domains,
        'score_distribution': {
            'high_score': high_score,
            'medium_score': medium_score,
            'low_score': low_score
        },
        'niche_distribution': niches,
        'averages': {
            'score': round(avg_score, 2),
            'domain_authority': round(avg_domain_authority, 2),
            'backlinks': round(avg_backlinks, 2)
        },
        'top_domains': sorted(domains, key=lambda x: x.get('score', 0), reverse=True)[:10]
    }

def log_performance_metrics(operation: str, duration: float, items_processed: int = 0) -> None:
    """Log performance metrics"""
    logger = logging.getLogger(__name__)
    
    if items_processed > 0:
        rate = items_processed / duration
        logger.info(f"Performance - {operation}: {duration:.2f}s, {items_processed} items, {rate:.2f} items/sec")
    else:
        logger.info(f"Performance - {operation}: {duration:.2f}s")
