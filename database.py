import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "domain_hunter.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Domains table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    score REAL DEFAULT 0,
                    status TEXT DEFAULT 'discovered',
                    notes TEXT
                )
            ''')
            
            # SEO metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS seo_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain_id INTEGER,
                    domain_authority INTEGER,
                    page_authority INTEGER,
                    backlinks INTEGER,
                    referring_domains INTEGER,
                    organic_traffic INTEGER,
                    trust_flow INTEGER,
                    citation_flow INTEGER,
                    spam_score INTEGER,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (domain_id) REFERENCES domains (id)
                )
            ''')
            
            # Content analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain_id INTEGER,
                    niche TEXT,
                    content_quality INTEGER,
                    spam_score INTEGER,
                    brandability_score INTEGER,
                    historical_content TEXT,
                    keywords TEXT,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (domain_id) REFERENCES domains (id)
                )
            ''')
            
            # Historical data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain_id INTEGER,
                    snapshot_date TEXT,
                    title TEXT,
                    content TEXT,
                    language TEXT,
                    FOREIGN KEY (domain_id) REFERENCES domains (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def add_domain(self, name: str) -> int:
        """Add a new domain to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO domains (name) VALUES (?)
            ''', (name,))
            
            if cursor.rowcount > 0:
                domain_id = cursor.lastrowid
            else:
                # Domain already exists, get its ID
                cursor.execute('SELECT id FROM domains WHERE name = ?', (name,))
                domain_id = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            return domain_id
            
        except Exception as e:
            logger.error(f"Error adding domain {name}: {str(e)}")
            raise
    
    def add_seo_metrics(self, domain_id: int, metrics: Dict[str, Any]) -> None:
        """Add SEO metrics for a domain"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO seo_metrics 
                (domain_id, domain_authority, page_authority, backlinks, referring_domains, 
                 organic_traffic, trust_flow, citation_flow, spam_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                domain_id,
                metrics.get('domain_authority'),
                metrics.get('page_authority'),
                metrics.get('backlinks'),
                metrics.get('referring_domains'),
                metrics.get('organic_traffic'),
                metrics.get('trust_flow'),
                metrics.get('citation_flow'),
                metrics.get('spam_score')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error adding SEO metrics for domain {domain_id}: {str(e)}")
            raise
    
    def add_content_analysis(self, domain_id: int, analysis: Dict[str, Any]) -> None:
        """Add content analysis for a domain"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            keywords_json = json.dumps(analysis.get('keywords', []))
            
            cursor.execute('''
                INSERT OR REPLACE INTO content_analysis 
                (domain_id, niche, content_quality, spam_score, brandability_score, 
                 historical_content, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                domain_id,
                analysis.get('niche'),
                analysis.get('content_quality'),
                analysis.get('spam_score'),
                analysis.get('brandability_score'),
                analysis.get('historical_content'),
                keywords_json
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error adding content analysis for domain {domain_id}: {str(e)}")
            raise
    
    def add_historical_data(self, domain_id: int, snapshot_date: str, title: str, content: str, language: str = 'en') -> None:
        """Add historical data for a domain"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO historical_data 
                (domain_id, snapshot_date, title, content, language)
                VALUES (?, ?, ?, ?, ?)
            ''', (domain_id, snapshot_date, title, content, language))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error adding historical data for domain {domain_id}: {str(e)}")
            raise
    
    def update_domain_score(self, domain_id: int, score: float) -> None:
        """Update the score for a domain"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE domains SET score = ? WHERE id = ?
            ''', (score, domain_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating score for domain {domain_id}: {str(e)}")
            raise
    
    def get_domain_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get domain by name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, discovered_at, score, status, notes
                FROM domains WHERE name = ?
            ''', (name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'discovered_at': result[2],
                    'score': result[3],
                    'status': result[4],
                    'notes': result[5]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting domain {name}: {str(e)}")
            return None
    
    def get_domain_details(self, domain_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a domain"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get domain info
            cursor.execute('''
                SELECT d.id, d.name, d.discovered_at, d.score, d.status, d.notes,
                       s.domain_authority, s.page_authority, s.backlinks, s.referring_domains,
                       s.organic_traffic, s.trust_flow, s.citation_flow, s.spam_score,
                       c.niche, c.content_quality, c.brandability_score, c.historical_content, c.keywords
                FROM domains d
                LEFT JOIN seo_metrics s ON d.id = s.domain_id
                LEFT JOIN content_analysis c ON d.id = c.domain_id
                WHERE d.id = ?
            ''', (domain_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                keywords = json.loads(result[18]) if result[18] else []
                return {
                    'id': result[0],
                    'name': result[1],
                    'discovered_at': result[2],
                    'score': result[3],
                    'status': result[4],
                    'notes': result[5],
                    'domain_authority': result[6],
                    'page_authority': result[7],
                    'backlinks': result[8],
                    'referring_domains': result[9],
                    'organic_traffic': result[10],
                    'trust_flow': result[11],
                    'citation_flow': result[12],
                    'spam_score': result[13],
                    'niche': result[14],
                    'content_quality': result[15],
                    'brandability_score': result[16],
                    'historical_content': result[17],
                    'keywords': keywords
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting domain details for {domain_id}: {str(e)}")
            return None
    
    def get_total_domains(self) -> int:
        """Get total number of domains in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM domains')
            result = cursor.fetchone()[0]
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting total domains: {str(e)}")
            return 0
    
    def get_analyzed_domains_count(self) -> int:
        """Get number of domains that have been analyzed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(DISTINCT d.id) 
                FROM domains d 
                JOIN seo_metrics s ON d.id = s.domain_id
            ''')
            result = cursor.fetchone()[0]
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting analyzed domains count: {str(e)}")
            return 0
    
    def get_high_value_domains_count(self) -> int:
        """Get number of high-value domains (score > 70)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM domains WHERE score > 70')
            result = cursor.fetchone()[0]
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting high-value domains count: {str(e)}")
            return 0
    
    def get_recent_high_value_domains(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent high-value domains"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT d.name, d.score, d.discovered_at,
                       s.domain_authority, s.backlinks, s.referring_domains,
                       c.niche, c.content_quality
                FROM domains d
                LEFT JOIN seo_metrics s ON d.id = s.domain_id
                LEFT JOIN content_analysis c ON d.id = c.domain_id
                WHERE d.score > 70
                ORDER BY d.discovered_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'name': row[0],
                    'score': row[1],
                    'discovered_at': row[2],
                    'domain_authority': row[3],
                    'backlinks': row[4],
                    'referring_domains': row[5],
                    'niche': row[6],
                    'content_quality': row[7]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent high-value domains: {str(e)}")
            return []
    
    def get_latest_domains(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get latest analyzed domains"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT d.name, d.score, d.discovered_at,
                       s.domain_authority, s.backlinks, s.referring_domains,
                       c.niche, c.content_quality
                FROM domains d
                LEFT JOIN seo_metrics s ON d.id = s.domain_id
                LEFT JOIN content_analysis c ON d.id = c.domain_id
                ORDER BY d.discovered_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'name': row[0],
                    'score': row[1],
                    'discovered_at': row[2],
                    'domain_authority': row[3],
                    'backlinks': row[4],
                    'referring_domains': row[5],
                    'niche': row[6],
                    'content_quality': row[7]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting latest domains: {str(e)}")
            return []
    
    def get_filtered_domains(self, min_score: float = 0, max_score: float = 100,
                           min_authority: int = 0, max_authority: int = 100,
                           min_backlinks: int = 0, max_backlinks: int = 100000,
                           niches: List[str] = None) -> List[Dict[str, Any]]:
        """Get domains based on filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT d.name, d.score, d.discovered_at,
                       s.domain_authority, s.backlinks, s.referring_domains,
                       c.niche, c.content_quality, c.spam_score
                FROM domains d
                LEFT JOIN seo_metrics s ON d.id = s.domain_id
                LEFT JOIN content_analysis c ON d.id = c.domain_id
                WHERE d.score >= ? AND d.score <= ?
                  AND (s.domain_authority IS NULL OR (s.domain_authority >= ? AND s.domain_authority <= ?))
                  AND (s.backlinks IS NULL OR (s.backlinks >= ? AND s.backlinks <= ?))
            '''
            
            params = [min_score, max_score, min_authority, max_authority, min_backlinks, max_backlinks]
            
            if niches:
                placeholders = ','.join(['?' for _ in niches])
                query += f' AND c.niche IN ({placeholders})'
                params.extend(niches)
            
            query += ' ORDER BY d.score DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'name': row[0],
                    'score': row[1],
                    'discovered_at': row[2],
                    'domain_authority': row[3],
                    'backlinks': row[4],
                    'referring_domains': row[5],
                    'niche': row[6],
                    'content_quality': row[7],
                    'spam_score': row[8]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting filtered domains: {str(e)}")
            return []
    
    def get_all_domains(self) -> List[Dict[str, Any]]:
        """Get all domains with their analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT d.name, d.score, d.discovered_at, d.status,
                       s.domain_authority, s.backlinks, s.referring_domains,
                       s.organic_traffic, s.trust_flow, s.citation_flow,
                       c.niche, c.content_quality, c.brandability_score, c.spam_score
                FROM domains d
                LEFT JOIN seo_metrics s ON d.id = s.domain_id
                LEFT JOIN content_analysis c ON d.id = c.domain_id
                ORDER BY d.score DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'name': row[0],
                    'score': row[1],
                    'discovered_at': row[2],
                    'status': row[3],
                    'domain_authority': row[4],
                    'backlinks': row[5],
                    'referring_domains': row[6],
                    'organic_traffic': row[7],
                    'trust_flow': row[8],
                    'citation_flow': row[9],
                    'niche': row[10],
                    'content_quality': row[11],
                    'brandability_score': row[12],
                    'spam_score': row[13]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting all domains: {str(e)}")
            return []
    
    def clear_all_data(self) -> None:
        """Clear all data from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM historical_data')
            cursor.execute('DELETE FROM content_analysis')
            cursor.execute('DELETE FROM seo_metrics')
            cursor.execute('DELETE FROM domains')
            
            conn.commit()
            conn.close()
            
            logger.info("All data cleared from database")
            
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            raise
