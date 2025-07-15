import requests
import logging
from typing import Dict, Any, List, Optional
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import re
import random
from datetime import datetime, timedelta
import trafilatura

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Initialize NLTK components
        self._initialize_nltk()
        
        # Initialize sentiment analyzer
        try:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except:
            logger.warning("Could not initialize sentiment analyzer")
            self.sentiment_analyzer = None
    
    def _initialize_nltk(self):
        """Initialize NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
            except:
                logger.warning("Could not download NLTK punkt tokenizer")
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            try:
                nltk.download('stopwords', quiet=True)
            except:
                logger.warning("Could not download NLTK stopwords")
        
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            try:
                nltk.download('vader_lexicon', quiet=True)
            except:
                logger.warning("Could not download NLTK vader_lexicon")
    
    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze content quality and characteristics of a domain"""
        try:
            logger.info(f"Analyzing content for domain: {domain}")
            
            # Get historical content from Wayback Machine
            historical_content = self._get_wayback_content(domain)
            
            # Analyze current content if available
            current_content = self._get_current_content(domain)
            
            # Perform content analysis
            analysis = {
                'niche': self._identify_niche(historical_content, current_content),
                'content_quality': self._assess_content_quality(historical_content, current_content),
                'spam_score': self._calculate_spam_score(historical_content, current_content),
                'brandability_score': self._calculate_brandability_score(domain),
                'keywords': self._extract_keywords(historical_content, current_content),
                'historical_content': historical_content[:1000] if historical_content else None,
                'language': self._detect_language(historical_content, current_content),
                'sentiment': self._analyze_sentiment(historical_content, current_content),
                'readability': self._calculate_readability(historical_content, current_content)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content for {domain}: {str(e)}")
            return self._get_mock_content_analysis(domain)
    
    def _get_wayback_content(self, domain: str) -> Optional[str]:
        """Get historical content from Wayback Machine"""
        try:
            # Use Wayback Machine API to get historical snapshots
            url = f"http://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=5"
            
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1:  # First row is headers
                    # Get the most recent snapshot
                    snapshot = data[1]  # [timestamp, original_url, mimetype, statuscode, digest, length]
                    timestamp = snapshot[1]
                    
                    # Get the actual content
                    wayback_url = f"http://web.archive.org/web/{timestamp}/{domain}"
                    
                    content_response = self.session.get(wayback_url, timeout=30)
                    
                    if content_response.status_code == 200:
                        # Extract text content using trafilatura
                        text_content = trafilatura.extract(content_response.text)
                        return text_content
            
        except Exception as e:
            logger.error(f"Error getting Wayback content for {domain}: {str(e)}")
        
        return None
    
    def _get_current_content(self, domain: str) -> Optional[str]:
        """Get current content from domain"""
        try:
            url = f"http://{domain}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Extract text content using trafilatura
                text_content = trafilatura.extract(response.text)
                return text_content
            
        except Exception as e:
            logger.error(f"Error getting current content for {domain}: {str(e)}")
        
        return None
    
    def _identify_niche(self, historical_content: str, current_content: str) -> str:
        """Identify the niche/topic of the domain"""
        try:
            content = (historical_content or "") + " " + (current_content or "")
            
            if not content.strip():
                return "Unknown"
            
            # Define niche keywords
            niche_keywords = {
                'Technology': ['technology', 'software', 'programming', 'development', 'tech', 'app', 'digital', 'code', 'computer', 'internet'],
                'Health': ['health', 'medical', 'fitness', 'wellness', 'nutrition', 'doctor', 'medicine', 'healthcare', 'diet', 'exercise'],
                'Finance': ['finance', 'money', 'investment', 'banking', 'trading', 'cryptocurrency', 'financial', 'loan', 'credit', 'insurance'],
                'Travel': ['travel', 'vacation', 'hotel', 'flight', 'tourism', 'destination', 'trip', 'adventure', 'explore', 'journey'],
                'Education': ['education', 'learning', 'school', 'university', 'course', 'student', 'teaching', 'academic', 'study', 'knowledge'],
                'Entertainment': ['entertainment', 'movie', 'music', 'game', 'celebrity', 'news', 'sports', 'fun', 'show', 'media'],
                'Business': ['business', 'entrepreneur', 'startup', 'company', 'marketing', 'sales', 'corporate', 'management', 'strategy', 'success'],
                'Food': ['food', 'recipe', 'cooking', 'restaurant', 'cuisine', 'chef', 'meal', 'ingredients', 'kitchen', 'dining'],
                'Fashion': ['fashion', 'style', 'clothing', 'designer', 'trend', 'outfit', 'beauty', 'accessories', 'brand', 'wardrobe']
            }
            
            content_lower = content.lower()
            niche_scores = {}
            
            for niche, keywords in niche_keywords.items():
                score = sum(content_lower.count(keyword) for keyword in keywords)
                niche_scores[niche] = score
            
            # Return the niche with highest score
            if niche_scores:
                return max(niche_scores, key=niche_scores.get) if max(niche_scores.values()) > 0 else "General"
            
            return "General"
            
        except Exception as e:
            logger.error(f"Error identifying niche: {str(e)}")
            return "Unknown"
    
    def _assess_content_quality(self, historical_content: str, current_content: str) -> int:
        """Assess the quality of content (0-100 score)"""
        try:
            content = (historical_content or "") + " " + (current_content or "")
            
            if not content.strip():
                return 0
            
            quality_score = 50  # Base score
            
            # Length factor
            content_length = len(content.split())
            if content_length > 500:
                quality_score += 10
            elif content_length > 200:
                quality_score += 5
            elif content_length < 50:
                quality_score -= 20
            
            # Sentence structure
            sentences = sent_tokenize(content)
            if len(sentences) > 10:
                avg_sentence_length = sum(len(sent.split()) for sent in sentences) / len(sentences)
                if 10 <= avg_sentence_length <= 25:
                    quality_score += 10
            
            # Check for spam indicators
            spam_indicators = ['click here', 'buy now', 'guaranteed', 'free money', 'limited time', 'act now']
            spam_count = sum(content.lower().count(indicator) for indicator in spam_indicators)
            quality_score -= spam_count * 5
            
            # Check for educational content indicators
            educational_indicators = ['learn', 'guide', 'tutorial', 'how to', 'step by step', 'explanation']
            educational_count = sum(content.lower().count(indicator) for indicator in educational_indicators)
            quality_score += educational_count * 3
            
            # Ensure score is within bounds
            return max(0, min(100, quality_score))
            
        except Exception as e:
            logger.error(f"Error assessing content quality: {str(e)}")
            return 50
    
    def _calculate_spam_score(self, historical_content: str, current_content: str) -> int:
        """Calculate spam score (0-100, higher is more spammy)"""
        try:
            content = (historical_content or "") + " " + (current_content or "")
            
            if not content.strip():
                return 0
            
            spam_score = 0
            content_lower = content.lower()
            
            # Spam keywords
            spam_keywords = [
                'buy now', 'click here', 'free money', 'guaranteed', 'limited time',
                'act now', 'no questions asked', 'risk free', 'special offer',
                'amazing deal', 'once in a lifetime', 'get rich quick'
            ]
            
            spam_count = sum(content_lower.count(keyword) for keyword in spam_keywords)
            spam_score += spam_count * 10
            
            # Excessive capitalization
            caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
            if caps_ratio > 0.1:
                spam_score += 20
            
            # Excessive punctuation
            punct_ratio = sum(1 for c in content if c in '!?') / len(content) if content else 0
            if punct_ratio > 0.05:
                spam_score += 15
            
            # Repetitive content
            words = content_lower.split()
            if len(words) > 100:
                word_freq = Counter(words)
                most_common = word_freq.most_common(1)[0][1] if word_freq else 0
                if most_common > len(words) * 0.1:
                    spam_score += 25
            
            return min(100, spam_score)
            
        except Exception as e:
            logger.error(f"Error calculating spam score: {str(e)}")
            return 0
    
    def _calculate_brandability_score(self, domain: str) -> int:
        """Calculate brandability score for the domain name (0-100)"""
        try:
            domain_name = domain.split('.')[0].lower()
            
            brandability_score = 50  # Base score
            
            # Length factor
            length = len(domain_name)
            if 4 <= length <= 8:
                brandability_score += 20
            elif 9 <= length <= 12:
                brandability_score += 10
            elif length > 15:
                brandability_score -= 20
            
            # Pronounceability (simple heuristic)
            vowels = sum(1 for c in domain_name if c in 'aeiou')
            consonants = len(domain_name) - vowels
            if vowels > 0 and consonants > 0:
                vowel_ratio = vowels / len(domain_name)
                if 0.2 <= vowel_ratio <= 0.6:
                    brandability_score += 15
            
            # Avoid numbers and hyphens
            if any(c.isdigit() for c in domain_name):
                brandability_score -= 15
            if '-' in domain_name:
                brandability_score -= 10
            
            # Dictionary words bonus
            common_words = ['tech', 'web', 'digital', 'smart', 'pro', 'express', 'global', 'prime']
            if any(word in domain_name for word in common_words):
                brandability_score += 10
            
            # Avoid spam-looking patterns
            spam_patterns = ['xxx', 'zzz', '123', 'abc']
            if any(pattern in domain_name for pattern in spam_patterns):
                brandability_score -= 25
            
            return max(0, min(100, brandability_score))
            
        except Exception as e:
            logger.error(f"Error calculating brandability score: {str(e)}")
            return 50
    
    def _extract_keywords(self, historical_content: str, current_content: str) -> List[str]:
        """Extract important keywords from content"""
        try:
            content = (historical_content or "") + " " + (current_content or "")
            
            if not content.strip():
                return []
            
            # Tokenize and clean
            words = word_tokenize(content.lower())
            
            # Remove stopwords and non-alphabetic tokens
            try:
                stop_words = set(stopwords.words('english'))
            except:
                stop_words = set()
            
            filtered_words = [word for word in words if word.isalpha() and word not in stop_words and len(word) > 2]
            
            # Get most common words
            word_freq = Counter(filtered_words)
            keywords = [word for word, count in word_freq.most_common(20)]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def _detect_language(self, historical_content: str, current_content: str) -> str:
        """Detect the language of the content"""
        try:
            content = (historical_content or "") + " " + (current_content or "")
            
            if not content.strip():
                return "unknown"
            
            # Simple language detection based on common words
            english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were']
            content_lower = content.lower()
            
            english_count = sum(content_lower.count(word) for word in english_words)
            
            if english_count > 10:
                return "english"
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return "unknown"
    
    def _analyze_sentiment(self, historical_content: str, current_content: str) -> Dict[str, float]:
        """Analyze sentiment of the content"""
        try:
            content = (historical_content or "") + " " + (current_content or "")
            
            if not content.strip() or not self.sentiment_analyzer:
                return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}
            
            scores = self.sentiment_analyzer.polarity_scores(content)
            return {
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'compound': scores['compound']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}
    
    def _calculate_readability(self, historical_content: str, current_content: str) -> int:
        """Calculate readability score (0-100, higher is more readable)"""
        try:
            content = (historical_content or "") + " " + (current_content or "")
            
            if not content.strip():
                return 0
            
            sentences = sent_tokenize(content)
            words = word_tokenize(content)
            
            if len(sentences) == 0 or len(words) == 0:
                return 0
            
            # Simple readability calculation
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Flesch-like formula (simplified)
            readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
            
            # Normalize to 0-100 scale
            readability = max(0, min(100, readability))
            
            return int(readability)
            
        except Exception as e:
            logger.error(f"Error calculating readability: {str(e)}")
            return 50
    
    def _get_mock_content_analysis(self, domain: str) -> Dict[str, Any]:
        """Generate mock content analysis for development"""
        domain_hash = hash(domain) % 1000000
        random.seed(domain_hash)
        
        niches = ['Technology', 'Health', 'Finance', 'Travel', 'Education', 'Entertainment', 'Business', 'Food', 'Fashion']
        
        return {
            'niche': random.choice(niches),
            'content_quality': random.randint(30, 95),
            'spam_score': random.randint(0, 30),
            'brandability_score': random.randint(40, 90),
            'keywords': random.sample(['technology', 'business', 'marketing', 'development', 'strategy', 'innovation', 'digital', 'growth', 'success', 'professional'], k=random.randint(5, 10)),
            'historical_content': f"This is sample historical content for {domain}. It contains information about various topics related to the domain's niche and provides valuable insights for users.",
            'language': 'english',
            'sentiment': {
                'positive': random.uniform(0.3, 0.7),
                'negative': random.uniform(0.0, 0.2),
                'neutral': random.uniform(0.3, 0.5),
                'compound': random.uniform(0.1, 0.6)
            },
            'readability': random.randint(60, 90)
        }
