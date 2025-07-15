import logging
from typing import Dict, Any, Optional, List
from database import DatabaseManager
import math

logger = logging.getLogger(__name__)

class DomainScorer:
    def __init__(self):
        self.weights = {
            'seo': 0.4,
            'content': 0.3,
            'brandability': 0.2,
            'spam_penalty': 0.1
        }
    
    def calculate_score(self, domain_id: int, db_manager: DatabaseManager, 
                       custom_weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate overall domain score based on various factors"""
        try:
            # Use custom weights if provided
            weights = custom_weights if custom_weights else self.weights
            
            # Get domain details
            domain_details = db_manager.get_domain_details(domain_id)
            
            if not domain_details:
                return 0.0
            
            # Calculate individual scores
            seo_score = self._calculate_seo_score(domain_details)
            content_score = self._calculate_content_score(domain_details)
            brandability_score = self._calculate_brandability_score(domain_details)
            spam_penalty = self._calculate_spam_penalty(domain_details)
            
            # Calculate weighted overall score
            overall_score = (
                seo_score * weights['seo'] +
                content_score * weights['content'] +
                brandability_score * weights['brandability'] -
                spam_penalty * weights['spam_penalty']
            )
            
            # Ensure score is within bounds
            final_score = max(0, min(100, overall_score))
            
            logger.info(f"Domain {domain_details['name']} scored: {final_score:.2f} "
                       f"(SEO: {seo_score:.1f}, Content: {content_score:.1f}, "
                       f"Brandability: {brandability_score:.1f}, Spam: {spam_penalty:.1f})")
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating score for domain {domain_id}: {str(e)}")
            return 0.0
    
    def _calculate_seo_score(self, domain_details: Dict[str, Any]) -> float:
        """Calculate SEO score based on various SEO metrics"""
        try:
            seo_score = 0.0
            
            # Domain Authority (0-100, weight: 30%)
            domain_authority = domain_details.get('domain_authority', 0)
            if domain_authority:
                seo_score += (domain_authority / 100) * 30
            
            # Backlinks (logarithmic scoring, weight: 25%)
            backlinks = domain_details.get('backlinks', 0)
            if backlinks > 0:
                # Use logarithmic scale for backlinks
                backlink_score = min(100, math.log10(backlinks + 1) * 25)
                seo_score += (backlink_score / 100) * 25
            
            # Referring Domains (logarithmic scoring, weight: 20%)
            referring_domains = domain_details.get('referring_domains', 0)
            if referring_domains > 0:
                ref_domain_score = min(100, math.log10(referring_domains + 1) * 30)
                seo_score += (ref_domain_score / 100) * 20
            
            # Trust Flow (0-100, weight: 15%)
            trust_flow = domain_details.get('trust_flow', 0)
            if trust_flow:
                seo_score += (trust_flow / 100) * 15
            
            # Organic Traffic (logarithmic scoring, weight: 10%)
            organic_traffic = domain_details.get('organic_traffic', 0)
            if organic_traffic > 0:
                traffic_score = min(100, math.log10(organic_traffic + 1) * 15)
                seo_score += (traffic_score / 100) * 10
            
            return seo_score
            
        except Exception as e:
            logger.error(f"Error calculating SEO score: {str(e)}")
            return 0.0
    
    def _calculate_content_score(self, domain_details: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        try:
            content_score = 0.0
            
            # Content Quality (0-100, weight: 40%)
            content_quality = domain_details.get('content_quality', 0)
            if content_quality:
                content_score += (content_quality / 100) * 40
            
            # Niche Relevance (weight: 30%)
            niche = domain_details.get('niche', 'Unknown')
            if niche and niche != 'Unknown':
                # High-value niches get bonus points
                high_value_niches = ['Technology', 'Finance', 'Health', 'Business', 'Education']
                if niche in high_value_niches:
                    content_score += 30
                else:
                    content_score += 20
            
            # Readability (weight: 20%)
            readability = domain_details.get('readability', 0)
            if readability:
                content_score += (readability / 100) * 20
            
            # Sentiment Analysis (weight: 10%)
            sentiment = domain_details.get('sentiment', {})
            if sentiment:
                compound_sentiment = sentiment.get('compound', 0)
                if compound_sentiment > 0:
                    content_score += abs(compound_sentiment) * 10
            
            return content_score
            
        except Exception as e:
            logger.error(f"Error calculating content score: {str(e)}")
            return 0.0
    
    def _calculate_brandability_score(self, domain_details: Dict[str, Any]) -> float:
        """Calculate brandability score"""
        try:
            brandability = domain_details.get('brandability_score', 0)
            return brandability if brandability else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating brandability score: {str(e)}")
            return 0.0
    
    def _calculate_spam_penalty(self, domain_details: Dict[str, Any]) -> float:
        """Calculate spam penalty (higher is worse)"""
        try:
            spam_penalty = 0.0
            
            # Content Spam Score (0-100, higher is worse)
            content_spam = domain_details.get('spam_score', 0)
            if content_spam:
                spam_penalty += content_spam
            
            # SEO Spam Score (0-100, higher is worse)
            seo_spam = domain_details.get('spam_score', 0)  # From SEO metrics
            if seo_spam:
                spam_penalty += seo_spam * 0.5  # Weight it less than content spam
            
            # Trust Flow vs Citation Flow ratio
            trust_flow = domain_details.get('trust_flow', 0)
            citation_flow = domain_details.get('citation_flow', 0)
            
            if trust_flow and citation_flow:
                tf_cf_ratio = trust_flow / citation_flow
                if tf_cf_ratio < 0.3:  # Very low trust relative to citation
                    spam_penalty += 20
                elif tf_cf_ratio < 0.5:
                    spam_penalty += 10
            
            return min(100, spam_penalty)
            
        except Exception as e:
            logger.error(f"Error calculating spam penalty: {str(e)}")
            return 0.0
    
    def get_score_breakdown(self, domain_id: int, db_manager: DatabaseManager) -> Dict[str, Any]:
        """Get detailed breakdown of domain scoring"""
        try:
            domain_details = db_manager.get_domain_details(domain_id)
            
            if not domain_details:
                return {}
            
            seo_score = self._calculate_seo_score(domain_details)
            content_score = self._calculate_content_score(domain_details)
            brandability_score = self._calculate_brandability_score(domain_details)
            spam_penalty = self._calculate_spam_penalty(domain_details)
            
            overall_score = (
                seo_score * self.weights['seo'] +
                content_score * self.weights['content'] +
                brandability_score * self.weights['brandability'] -
                spam_penalty * self.weights['spam_penalty']
            )
            
            return {
                'domain_name': domain_details['name'],
                'overall_score': max(0, min(100, overall_score)),
                'component_scores': {
                    'seo_score': seo_score,
                    'content_score': content_score,
                    'brandability_score': brandability_score,
                    'spam_penalty': spam_penalty
                },
                'weighted_contributions': {
                    'seo_contribution': seo_score * self.weights['seo'],
                    'content_contribution': content_score * self.weights['content'],
                    'brandability_contribution': brandability_score * self.weights['brandability'],
                    'spam_penalty_contribution': spam_penalty * self.weights['spam_penalty']
                },
                'weights': self.weights,
                'recommendations': self._generate_recommendations(domain_details, seo_score, content_score, brandability_score, spam_penalty)
            }
            
        except Exception as e:
            logger.error(f"Error getting score breakdown for domain {domain_id}: {str(e)}")
            return {}
    
    def _generate_recommendations(self, domain_details: Dict[str, Any], 
                                seo_score: float, content_score: float, 
                                brandability_score: float, spam_penalty: float) -> List[str]:
        """Generate recommendations based on domain analysis"""
        recommendations = []
        
        try:
            # SEO recommendations
            if seo_score < 30:
                recommendations.append("Low SEO metrics. Consider checking for better domains with higher authority.")
            
            domain_authority = domain_details.get('domain_authority', 0)
            if domain_authority < 20:
                recommendations.append("Domain authority is low. May require significant SEO investment.")
            
            # Content recommendations
            if content_score < 40:
                recommendations.append("Content quality is low. Review historical content for spam or irrelevant material.")
            
            niche = domain_details.get('niche', 'Unknown')
            if niche == 'Unknown':
                recommendations.append("Unable to identify clear niche. May indicate diverse or unfocused content.")
            
            # Brandability recommendations
            if brandability_score < 50:
                recommendations.append("Low brandability score. Domain name may be difficult to remember or pronounce.")
            
            # Spam recommendations
            if spam_penalty > 30:
                recommendations.append("High spam indicators detected. Investigate backlink profile and content history.")
            
            # Trust flow recommendations
            trust_flow = domain_details.get('trust_flow', 0)
            citation_flow = domain_details.get('citation_flow', 0)
            if trust_flow and citation_flow and trust_flow / citation_flow < 0.3:
                recommendations.append("Low trust flow relative to citation flow. May indicate spammy backlinks.")
            
            # General recommendations
            overall_score = max(0, min(100, seo_score * self.weights['seo'] + 
                                     content_score * self.weights['content'] + 
                                     brandability_score * self.weights['brandability'] - 
                                     spam_penalty * self.weights['spam_penalty']))
            
            if overall_score > 80:
                recommendations.append("Excellent domain opportunity. Consider acquiring soon.")
            elif overall_score > 60:
                recommendations.append("Good domain potential. Suitable for most projects.")
            elif overall_score > 40:
                recommendations.append("Moderate potential. May require additional analysis.")
            else:
                recommendations.append("Low potential. Consider looking for better alternatives.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Unable to generate recommendations due to analysis error."]
    
    def update_weights(self, new_weights: Dict[str, float]) -> bool:
        """Update scoring weights"""
        try:
            # Validate weights
            required_keys = ['seo', 'content', 'brandability', 'spam_penalty']
            
            if not all(key in new_weights for key in required_keys):
                logger.error("Missing required weight keys")
                return False
            
            # Normalize weights to sum to 1.0 (excluding spam_penalty)
            weight_sum = sum(new_weights[key] for key in required_keys[:-1])
            if weight_sum > 0:
                for key in required_keys[:-1]:
                    new_weights[key] = new_weights[key] / weight_sum
            
            self.weights = new_weights
            logger.info(f"Updated scoring weights: {self.weights}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating weights: {str(e)}")
            return False
    
    def get_domain_value_estimate(self, domain_id: int, db_manager: DatabaseManager) -> Dict[str, Any]:
        """Estimate domain value based on various factors"""
        try:
            domain_details = db_manager.get_domain_details(domain_id)
            
            if not domain_details:
                return {}
            
            # Base value calculation
            base_value = 100  # Minimum value
            
            # SEO value
            domain_authority = domain_details.get('domain_authority', 0)
            backlinks = domain_details.get('backlinks', 0)
            referring_domains = domain_details.get('referring_domains', 0)
            
            seo_value = (domain_authority * 10) + (math.log10(backlinks + 1) * 50) + (math.log10(referring_domains + 1) * 30)
            
            # Content value
            content_quality = domain_details.get('content_quality', 0)
            niche = domain_details.get('niche', 'Unknown')
            
            content_value = content_quality * 2
            
            # Niche multiplier
            niche_multipliers = {
                'Technology': 1.5,
                'Finance': 2.0,
                'Health': 1.8,
                'Business': 1.3,
                'Education': 1.2,
                'Travel': 1.1,
                'Entertainment': 1.0
            }
            
            niche_multiplier = niche_multipliers.get(niche, 1.0)
            
            # Brandability value
            brandability = domain_details.get('brandability_score', 0)
            brandability_value = brandability * 3
            
            # Spam penalty
            spam_score = domain_details.get('spam_score', 0)
            spam_penalty = spam_score * 5
            
            # Calculate estimated value
            estimated_value = (base_value + seo_value + content_value + brandability_value) * niche_multiplier - spam_penalty
            
            # Value ranges
            if estimated_value < 100:
                value_range = "Under $100"
            elif estimated_value < 500:
                value_range = "$100 - $500"
            elif estimated_value < 1000:
                value_range = "$500 - $1,000"
            elif estimated_value < 2500:
                value_range = "$1,000 - $2,500"
            elif estimated_value < 5000:
                value_range = "$2,500 - $5,000"
            else:
                value_range = "$5,000+"
            
            return {
                'domain_name': domain_details['name'],
                'estimated_value': max(0, estimated_value),
                'value_range': value_range,
                'value_components': {
                    'base_value': base_value,
                    'seo_value': seo_value,
                    'content_value': content_value,
                    'brandability_value': brandability_value,
                    'niche_multiplier': niche_multiplier,
                    'spam_penalty': spam_penalty
                }
            }
            
        except Exception as e:
            logger.error(f"Error estimating domain value for {domain_id}: {str(e)}")
            return {}
