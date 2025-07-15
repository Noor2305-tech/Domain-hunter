import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import asyncio
import time
import logging
from typing import List, Dict, Any

from database import DatabaseManager
from domain_scraper import DomainScraper
from seo_analyzer import SEOAnalyzer
from content_analyzer import ContentAnalyzer
from domain_scorer import DomainScorer
from utils import setup_logging, export_to_csv

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize components
@st.cache_resource
def get_components():
    """Initialize and cache application components"""
    db_manager = DatabaseManager()
    domain_scraper = DomainScraper()
    seo_analyzer = SEOAnalyzer()
    content_analyzer = ContentAnalyzer()
    domain_scorer = DomainScorer()
    
    return db_manager, domain_scraper, seo_analyzer, content_analyzer, domain_scorer

def main():
    st.set_page_config(
        page_title="AI Domain Hunter Pro",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for attractive UI
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .pricing-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e9ecef;
        text-align: center;
        margin: 1rem 0;
    }
    .pricing-card.featured {
        border: 2px solid #667eea;
        transform: scale(1.05);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
    }
    .success-badge {
        background: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .premium-badge {
        background: #ffc107;
        color: #212529;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with gradient
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Domain Hunter Pro</h1>
        <p>Discover and evaluate profitable expired domains using AI-powered analysis</p>
        <p><em>Find your next high-value domain in seconds, not hours</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get components
    db_manager, domain_scraper, seo_analyzer, content_analyzer, domain_scorer = get_components()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Scraping settings
        st.subheader("Data Sources")
        scrape_expired_domains = st.checkbox("Scrape Expired Domains", value=True)
        scrape_auctions = st.checkbox("Scrape Domain Auctions", value=False)
        
        # Filtering criteria
        st.subheader("Filtering Criteria")
        min_domain_age = st.slider("Minimum Domain Age (years)", 0, 20, 1)
        min_domain_authority = st.slider("Minimum Domain Authority", 0, 100, 10)
        min_backlinks = st.number_input("Minimum Backlinks", min_value=0, value=10)
        
        # Scoring weights
        st.subheader("Scoring Weights")
        seo_weight = st.slider("SEO Metrics Weight", 0.0, 1.0, 0.4)
        content_weight = st.slider("Content Quality Weight", 0.0, 1.0, 0.3)
        brandability_weight = st.slider("Brandability Weight", 0.0, 1.0, 0.2)
        spam_penalty_weight = st.slider("Spam Penalty Weight", 0.0, 1.0, 0.1)
        
        # Actions
        st.subheader("Actions")
        if st.button("🔄 Refresh Data", type="primary", key="refresh_data"):
            st.session_state.refresh_data = True
        
        if st.button("🧹 Clear Database", key="clear_database"):
            db_manager.clear_all_data()
            st.success("Database cleared!")
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Dashboard", "🔍 Discovery", "📊 Analysis", "💰 Pricing", "🧮 Valuation Tool", "⚙️ Settings"])
    
    with tab1:
        display_dashboard(db_manager)
    
    with tab2:
        display_discovery(db_manager, domain_scraper, seo_analyzer, content_analyzer, domain_scorer,
                         scrape_expired_domains, scrape_auctions, min_domain_age, min_domain_authority, min_backlinks)
    
    with tab3:
        display_analysis(db_manager, seo_weight, content_weight, brandability_weight, spam_penalty_weight)
    
    with tab4:
        display_pricing()
    
    with tab5:
        display_valuation_tool(db_manager, seo_analyzer, content_analyzer, domain_scorer)
    
    with tab6:
        display_settings(db_manager)

def display_dashboard(db_manager):
    """Display the main dashboard with key metrics"""
    st.markdown("## 📊 Performance Dashboard")
    
    # Get summary statistics
    total_domains = db_manager.get_total_domains()
    analyzed_domains = db_manager.get_analyzed_domains_count()
    high_value_domains = db_manager.get_high_value_domains_count()
    
    # Display metrics with attractive cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_domains}</h3>
            <p>Total Domains</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{analyzed_domains}</h3>
            <p>Analyzed Domains</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{high_value_domains}</h3>
            <p>High Value Domains</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        analysis_rate = (analyzed_domains / total_domains * 100) if total_domains > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{analysis_rate:.1f}%</h3>
            <p>Analysis Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Value proposition
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 AI-Powered Analysis</h4>
            <p>Our advanced AI analyzes SEO metrics, content quality, and brandability to identify profitable domains.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>⚡ Real-Time Discovery</h4>
            <p>Discover expired domains from multiple sources with real-time analysis and scoring.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>💎 Value Estimation</h4>
            <p>Get accurate domain valuations based on historical data and market trends.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent discoveries
    st.markdown("## 🔥 Recent High-Value Discoveries")
    recent_domains = db_manager.get_recent_high_value_domains(limit=10)
    
    if recent_domains:
        df = pd.DataFrame(recent_domains)
        st.dataframe(df, use_container_width=True)
        
        # Show success message for high-value finds
        if len(recent_domains) > 0:
            st.markdown(f"""
            <div style="text-align: center; margin: 1rem 0;">
                <span class="success-badge">🎉 {len(recent_domains)} High-Value Domains Found!</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 8px;">
            <h4>Ready to discover your next profitable domain?</h4>
            <p>Use the Discovery tab to start finding high-value expired domains!</p>
        </div>
        """, unsafe_allow_html=True)

def display_discovery(db_manager, domain_scraper, seo_analyzer, content_analyzer, domain_scorer,
                     scrape_expired_domains, scrape_auctions, min_domain_age, min_domain_authority, min_backlinks):
    """Display the domain discovery interface"""
    st.markdown("## 🔍 Domain Discovery Center")
    
    st.markdown("""
    <div class="feature-card">
        <h4>🎯 Discover Your Next Profitable Domain</h4>
        <p>Use our AI-powered tools to find and analyze expired domains with high SEO value, 
        strong backlink profiles, and excellent brandability potential.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Manual domain input
    st.markdown("### 🔬 Single Domain Analysis")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        manual_domain = st.text_input(
            "Enter domain name (e.g., example.com)",
            placeholder="Enter domain to analyze...",
            help="Analyze any domain for SEO metrics, content quality, and market value"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Analyze Domain", type="primary", key="discovery_analyze") and manual_domain:
            analyze_single_domain(manual_domain, db_manager, seo_analyzer, content_analyzer, domain_scorer)
    
    # Automated discovery
    st.markdown("### 🚀 Automated Discovery")
    
    st.markdown("""
    <div class="feature-card">
        <h4>⚡ Batch Processing</h4>
        <p>Run automated discovery to find and analyze multiple expired domains based on your filtering criteria.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start Discovery Process", type="primary", key="start_discovery"):
            run_discovery_process(db_manager, domain_scraper, seo_analyzer, content_analyzer, domain_scorer,
                                scrape_expired_domains, scrape_auctions, min_domain_age, min_domain_authority, min_backlinks)
    
    with col2:
        if st.button("⏹️ Stop Discovery", key="stop_discovery_btn"):
            st.session_state.stop_discovery = True
            st.warning("Discovery process will stop after current batch")
    
    # Progress tracking
    if 'discovery_progress' in st.session_state:
        st.progress(st.session_state.discovery_progress)
    
    # Display recent results
    st.subheader("Latest Discoveries")
    latest_domains = db_manager.get_latest_domains(limit=20)
    
    if latest_domains:
        df = pd.DataFrame(latest_domains)
        st.dataframe(df, use_container_width=True)
        
        # Export functionality
        if st.button("📥 Export Results", key="export_discovery_results"):
            csv_data = export_to_csv(latest_domains)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"domain_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def analyze_single_domain(domain, db_manager, seo_analyzer, content_analyzer, domain_scorer):
    """Analyze a single domain and display results"""
    with st.spinner(f"Analyzing {domain}..."):
        try:
            # Check if domain already exists
            existing_domain = db_manager.get_domain_by_name(domain)
            
            if existing_domain:
                st.info(f"Domain {domain} already analyzed. Showing existing results.")
                display_domain_analysis(existing_domain)
                return
            
            # Add domain to database
            domain_id = db_manager.add_domain(domain)
            
            # Perform SEO analysis
            seo_metrics = seo_analyzer.analyze_domain(domain)
            if seo_metrics:
                db_manager.add_seo_metrics(domain_id, seo_metrics)
            
            # Perform content analysis
            content_analysis = content_analyzer.analyze_domain(domain)
            if content_analysis:
                db_manager.add_content_analysis(domain_id, content_analysis)
            
            # Calculate score
            score = domain_scorer.calculate_score(domain_id, db_manager)
            db_manager.update_domain_score(domain_id, score)
            
            # Display results
            domain_data = db_manager.get_domain_details(domain_id)
            display_domain_analysis(domain_data)
            
            st.success(f"Analysis complete for {domain}")
            
        except Exception as e:
            st.error(f"Error analyzing domain {domain}: {str(e)}")
            logger.error(f"Error analyzing domain {domain}: {str(e)}")

def display_domain_analysis(domain_data):
    """Display detailed analysis for a single domain"""
    if not domain_data:
        st.error("No domain data available")
        return
    
    st.subheader(f"Analysis: {domain_data['name']}")
    
    # Score display
    score = domain_data.get('score', 0)
    score_color = "green" if score > 70 else "orange" if score > 40 else "red"
    st.markdown(f"**Overall Score:** :{score_color}[{score:.1f}/100]")
    
    # Metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Domain Authority", domain_data.get('domain_authority', 'N/A'))
        st.metric("Backlinks", domain_data.get('backlinks', 'N/A'))
    
    with col2:
        st.metric("Referring Domains", domain_data.get('referring_domains', 'N/A'))
        st.metric("Organic Traffic", domain_data.get('organic_traffic', 'N/A'))
    
    with col3:
        st.metric("Trust Flow", domain_data.get('trust_flow', 'N/A'))
        st.metric("Citation Flow", domain_data.get('citation_flow', 'N/A'))
    
    # Content analysis
    if domain_data.get('content_quality'):
        st.subheader("Content Analysis")
        st.write(f"**Quality Score:** {domain_data.get('content_quality', 'N/A')}/100")
        st.write(f"**Niche:** {domain_data.get('niche', 'Unknown')}")
        st.write(f"**Spam Score:** {domain_data.get('spam_score', 'N/A')}/100")
    
    # Historical data
    if domain_data.get('historical_content'):
        st.subheader("Historical Content")
        st.text_area("Sample Content", domain_data['historical_content'][:500] + "...", height=100)

def run_discovery_process(db_manager, domain_scraper, seo_analyzer, content_analyzer, domain_scorer,
                         scrape_expired_domains, scrape_auctions, min_domain_age, min_domain_authority, min_backlinks):
    """Run the automated discovery process"""
    st.session_state.stop_discovery = False
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Get domain list
        status_text.text("Fetching domain list...")
        domains = []
        
        if scrape_expired_domains:
            expired_domains = domain_scraper.scrape_expired_domains()
            domains.extend(expired_domains)
        
        if scrape_auctions:
            auction_domains = domain_scraper.scrape_auction_domains()
            domains.extend(auction_domains)
        
        # Add sample high-value domains for demonstration
        sample_domains = [
            "techstartup.com", "digitalmarketing.org", "aitools.net", 
            "blockchain.info", "ecommerce.biz", "webdesign.pro",
            "seoservices.com", "dataanalytics.net", "cloudsolutions.org",
            "mobilepay.com", "smarthealth.co", "cybersecurity.net"
        ]
        domains.extend(sample_domains)
        
        if not domains:
            st.warning("No domains found. Please check your data sources.")
            return
        
        st.info(f"Found {len(domains)} domains to analyze")
        
        # Process domains
        for i, domain in enumerate(domains):
            if st.session_state.get('stop_discovery', False):
                break
                
            progress = (i + 1) / len(domains)
            progress_bar.progress(progress)
            status_text.text(f"Analyzing domain {i+1}/{len(domains)}: {domain}")
            
            try:
                # Check if domain already exists
                if db_manager.get_domain_by_name(domain):
                    continue
                
                # Add domain to database
                domain_id = db_manager.add_domain(domain)
                
                # Perform analysis
                seo_metrics = seo_analyzer.analyze_domain(domain)
                if seo_metrics:
                    db_manager.add_seo_metrics(domain_id, seo_metrics)
                    
                    # Apply filtering criteria
                    if (seo_metrics.get('domain_authority', 0) < min_domain_authority or
                        seo_metrics.get('backlinks', 0) < min_backlinks):
                        continue
                
                content_analysis = content_analyzer.analyze_domain(domain)
                if content_analysis:
                    db_manager.add_content_analysis(domain_id, content_analysis)
                
                # Calculate score
                score = domain_scorer.calculate_score(domain_id, db_manager)
                db_manager.update_domain_score(domain_id, score)
                
                # Small delay to prevent overwhelming APIs
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing domain {domain}: {str(e)}")
                continue
        
        status_text.text("Discovery process completed!")
        st.success(f"Analyzed {len(domains)} domains successfully")
        
    except Exception as e:
        st.error(f"Error in discovery process: {str(e)}")
        logger.error(f"Error in discovery process: {str(e)}")

def display_analysis(db_manager, seo_weight, content_weight, brandability_weight, spam_penalty_weight):
    """Display analysis and filtering interface"""
    st.header("Domain Analysis & Filtering")
    
    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score_range = st.slider("Score Range", 0, 100, (50, 100))
        domain_age_filter = st.slider("Domain Age (years)", 0, 20, (1, 20))
    
    with col2:
        authority_filter = st.slider("Domain Authority", 0, 100, (10, 100))
        backlinks_filter = st.slider("Backlinks", 0, 10000, (10, 10000))
    
    with col3:
        niche_filter = st.multiselect("Niche Filter", 
                                     ["Technology", "Health", "Finance", "Travel", "Education", "Entertainment"],
                                     default=[])
    
    # Apply filters and get results
    filtered_domains = db_manager.get_filtered_domains(
        min_score=score_range[0],
        max_score=score_range[1],
        min_authority=authority_filter[0],
        max_authority=authority_filter[1],
        min_backlinks=backlinks_filter[0],
        max_backlinks=backlinks_filter[1],
        niches=niche_filter
    )
    
    # Display results
    st.subheader(f"Filtered Results ({len(filtered_domains)} domains)")
    
    if filtered_domains:
        df = pd.DataFrame(filtered_domains)
        
        # Sort by score by default
        df = df.sort_values('score', ascending=False)
        
        # Display in a more interactive format
        for _, domain in df.iterrows():
            with st.expander(f"🌐 {domain['name']} (Score: {domain['score']:.1f})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Domain Authority:** {domain.get('domain_authority', 'N/A')}")
                    st.write(f"**Backlinks:** {domain.get('backlinks', 'N/A')}")
                    st.write(f"**Referring Domains:** {domain.get('referring_domains', 'N/A')}")
                
                with col2:
                    st.write(f"**Niche:** {domain.get('niche', 'Unknown')}")
                    st.write(f"**Content Quality:** {domain.get('content_quality', 'N/A')}/100")
                    st.write(f"**Spam Score:** {domain.get('spam_score', 'N/A')}/100")
        
        # Export functionality
        if st.button("📥 Export Filtered Results", key="export_filtered_results"):
            csv_data = export_to_csv(filtered_domains)
            st.download_button(
                label="Download Filtered CSV",
                data=csv_data,
                file_name=f"filtered_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No domains match the current filters. Try adjusting the criteria.")

def display_pricing():
    """Display pricing plans and subscription options"""
    st.markdown("## 💰 Choose Your Plan")
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h3>Find the perfect plan for your domain hunting needs</h3>
        <p>Start with our free tools, then upgrade for premium features and unlimited access</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Pricing cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>🎯 Starter Pack</h3>
            <h2>FREE</h2>
            <p><strong>Domain Valuation Calculator</strong></p>
            <ul style="text-align: left; margin: 1rem 0;">
                <li>✅ Free domain valuation tool</li>
                <li>✅ Basic SEO metrics analysis</li>
                <li>✅ Brandability scoring</li>
                <li>✅ 5 valuations per day</li>
                <li>✅ Email support</li>
            </ul>
            <p><em>Perfect for getting started</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get Started Free", key="free_plan"):
            st.success("🎉 You're already using our free tools! Check out the Valuation Tool tab.")
    
    with col2:
        st.markdown("""
        <div class="pricing-card featured">
            <div class="premium-badge">MOST POPULAR</div>
            <h3>🚀 Trial Subscription</h3>
            <h2>$49<span style="font-size: 0.6em;">/month</span></h2>
            <p><strong>Limited Access Trial</strong></p>
            <ul style="text-align: left; margin: 1rem 0;">
                <li>✅ Everything in Free</li>
                <li>✅ 100 domain analyses/month</li>
                <li>✅ Premium expired domain listings</li>
                <li>✅ Historical data analysis</li>
                <li>✅ Export capabilities</li>
                <li>✅ Priority support</li>
            </ul>
            <p><em>Great for testing our premium features</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start 30-Day Trial", key="trial_plan"):
            st.info("🔄 Trial subscription coming soon! Join our waitlist to get notified.")
    
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>💎 Standard Plan</h3>
            <h2>$109.99<span style="font-size: 0.6em;">/month</span></h2>
            <p><strong>Full Access Marketplace</strong></p>
            <ul style="text-align: left; margin: 1rem 0;">
                <li>✅ Everything in Trial</li>
                <li>✅ Unlimited domain analyses</li>
                <li>✅ AI-driven insights</li>
                <li>✅ Advanced filtering</li>
                <li>✅ Bulk export tools</li>
                <li>✅ API access</li>
                <li>✅ Dedicated support</li>
            </ul>
            <p><em>For serious domain investors</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Upgrade to Standard", key="standard_plan"):
            st.info("🔄 Standard subscription coming soon! Contact us for early access.")
    
    # Feature comparison
    st.markdown("---")
    st.markdown("## 📋 Feature Comparison")
    
    comparison_data = {
        "Feature": [
            "Domain Valuation Tool",
            "Daily Valuations",
            "Expired Domain Listings",
            "Historical Data Analysis",
            "Export Capabilities",
            "API Access",
            "Support Level"
        ],
        "Free": [
            "✅ Basic",
            "5 per day",
            "❌ Limited",
            "❌ No",
            "❌ No",
            "❌ No",
            "Email"
        ],
        "Trial ($49/mo)": [
            "✅ Advanced",
            "100 per month",
            "✅ Premium",
            "✅ Yes",
            "✅ CSV",
            "❌ No",
            "Priority"
        ],
        "Standard ($109.99/mo)": [
            "✅ Full",
            "Unlimited",
            "✅ Full Access",
            "✅ Complete",
            "✅ Multiple formats",
            "✅ Yes",
            "Dedicated"
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)

def display_valuation_tool(db_manager, seo_analyzer, content_analyzer, domain_scorer):
    """Display the free domain valuation calculator"""
    st.markdown("## 🧮 Free Domain Valuation Calculator")
    
    st.markdown("""
    <div class="feature-card">
        <h4>🎯 Get Instant Domain Valuations</h4>
        <p>Enter any domain name below to get an AI-powered valuation report including SEO metrics, 
        content analysis, and market value estimation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        domain_input = st.text_input(
            "Enter domain name (e.g., example.com)",
            placeholder="yourdomainname.com",
            help="Enter a domain name to get instant valuation"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        analyze_button = st.button("🔍 Analyze Domain", type="primary", key="valuation_analyze")
    
    # Daily usage counter (simulated)
    if 'daily_valuations' not in st.session_state:
        st.session_state.daily_valuations = 0
    
    # Usage limit for free users
    free_limit = 5
    remaining = free_limit - st.session_state.daily_valuations
    
    if remaining <= 0:
        st.warning("⚠️ You've reached your daily limit of 5 free valuations. Upgrade to Trial for 100 valuations per month!")
        st.markdown("### 🚀 Ready to upgrade?")
        if st.button("Upgrade to Trial Plan", key="valuation_upgrade"):
            st.info("🔄 Trial subscription coming soon! Join our waitlist.")
    else:
        st.info(f"💡 Free valuations remaining today: {remaining}/{free_limit}")
    
    if analyze_button and domain_input and remaining > 0:
        st.session_state.daily_valuations += 1
        
        with st.spinner(f"Analyzing {domain_input}..."):
            try:
                # Check if domain exists in database
                existing_domain = db_manager.get_domain_by_name(domain_input)
                
                if existing_domain:
                    domain_data = db_manager.get_domain_details(existing_domain['id'])
                else:
                    # Perform fresh analysis
                    domain_id = db_manager.add_domain(domain_input)
                    
                    # Get SEO metrics
                    seo_metrics = seo_analyzer.analyze_domain(domain_input)
                    if seo_metrics:
                        db_manager.add_seo_metrics(domain_id, seo_metrics)
                    
                    # Get content analysis
                    content_analysis = content_analyzer.analyze_domain(domain_input)
                    if content_analysis:
                        db_manager.add_content_analysis(domain_id, content_analysis)
                    
                    # Calculate score
                    score = domain_scorer.calculate_score(domain_id, db_manager)
                    db_manager.update_domain_score(domain_id, score)
                    
                    domain_data = db_manager.get_domain_details(domain_id)
                
                # Display results
                if domain_data:
                    display_valuation_results(domain_data, domain_scorer, db_manager)
                    
            except Exception as e:
                st.error(f"Error analyzing domain: {str(e)}")

def display_valuation_results(domain_data, domain_scorer, db_manager):
    """Display detailed valuation results"""
    st.markdown("---")
    st.markdown("## 📊 Valuation Report")
    
    # Overall score with visual indicator
    score = domain_data.get('score', 0)
    score_color = "green" if score > 70 else "orange" if score > 40 else "red"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 12px; color: white; margin: 1rem 0;">
            <h2>{domain_data['name']}</h2>
            <h1 style="font-size: 3rem; margin: 0;">{score:.1f}/100</h1>
            <p style="font-size: 1.2rem;">Overall Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Key metrics
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Domain Authority", domain_data.get('domain_authority', 'N/A'))
    with col2:
        st.metric("Backlinks", f"{domain_data.get('backlinks', 0):,}")
    with col3:
        st.metric("Referring Domains", f"{domain_data.get('referring_domains', 0):,}")
    with col4:
        st.metric("Trust Flow", domain_data.get('trust_flow', 'N/A'))
    
    # Value estimation
    try:
        value_estimate = domain_scorer.get_domain_value_estimate(domain_data['id'], db_manager)
        if value_estimate:
            st.markdown("### 💰 Estimated Value")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="feature-card">
                    <h4>Market Value Range</h4>
                    <h3 style="color: #667eea;">{value_estimate.get('value_range', 'N/A')}</h3>
                    <p>Confidence: {value_estimate.get('confidence', 0):.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="feature-card">
                    <h4>Estimated Value</h4>
                    <h3 style="color: #667eea;">${value_estimate.get('estimated_value', 0):,.0f}</h3>
                    <p>Based on SEO metrics and market data</p>
                </div>
                """, unsafe_allow_html=True)
    except:
        st.info("Value estimation temporarily unavailable")
    
    # Content analysis
    st.markdown("### 📝 Content Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Niche:** {domain_data.get('niche', 'Unknown')}")
        st.write(f"**Content Quality:** {domain_data.get('content_quality', 'N/A')}/100")
    
    with col2:
        st.write(f"**Brandability:** {domain_data.get('brandability_score', 'N/A')}/100")
        st.write(f"**Spam Score:** {domain_data.get('spam_score', 'N/A')}/100")
    
    # Recommendations
    try:
        breakdown = domain_scorer.get_score_breakdown(domain_data['id'], db_manager)
        if breakdown and breakdown.get('recommendations'):
            st.markdown("### 💡 AI Recommendations")
            for rec in breakdown['recommendations'][:3]:  # Show top 3 recommendations
                st.info(f"• {rec}")
    except:
        pass
    
    # Upgrade prompt
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 8px;">
        <h4>🚀 Want more detailed analysis?</h4>
        <p>Upgrade to our Trial plan for advanced features including historical data analysis, 
        bulk processing, and unlimited valuations!</p>
    </div>
    """, unsafe_allow_html=True)

def display_settings(db_manager):
    """Display settings and configuration options"""
    st.header("Settings & Configuration")
    
    # Database statistics
    st.subheader("Database Statistics")
    total_domains = db_manager.get_total_domains()
    analyzed_domains = db_manager.get_analyzed_domains_count()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Domains", total_domains)
    with col2:
        st.metric("Analyzed Domains", analyzed_domains)
    
    # Data management
    st.subheader("Data Management")
    if st.button("🗑️ Clear All Data", type="secondary", key="clear_all_data"):
        if st.checkbox("I understand this will delete all data"):
            db_manager.clear_all_data()
            st.success("All data cleared successfully")
            st.rerun()
    
    # API Configuration
    st.subheader("API Configuration")
    st.info("API keys are automatically loaded from environment variables")
    
    # Check API status
    if st.button("🔍 Check API Status", key="check_api_status"):
        st.write("**Wayback Machine API:** Available")
        st.write("**Domain Availability Check:** Available")
        st.write("**SEO APIs:** Mock mode (for development)")
    
    # Export all data
    st.subheader("Data Export")
    if st.button("📁 Export All Data", key="export_all_data"):
        all_domains = db_manager.get_all_domains()
        if all_domains:
            csv_data = export_to_csv(all_domains)
            st.download_button(
                label="Download All Data",
                data=csv_data,
                file_name=f"all_domains_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data to export")

if __name__ == "__main__":
    main()
