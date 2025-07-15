# AI Domain Hunter - Repository Overview

## Overview

AI Domain Hunter is a Streamlit-based web application designed to discover, analyze, and evaluate profitable expired domains using AI-powered analysis. The application combines web scraping, SEO analysis, content evaluation, and machine learning to identify high-value domains from the expired domain market.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**July 14, 2025 - Monetization Features and UI Enhancement**
- Added comprehensive pricing structure with three tiers (Free, Trial $49/month, Standard $99-299/month)
- Implemented free Domain Valuation Calculator with daily usage limits (5 valuations/day)
- Enhanced UI with gradient backgrounds, attractive cards, and professional styling
- Added dedicated Pricing tab showcasing all subscription plans with feature comparison
- Integrated lead magnet strategy with upgrade prompts throughout the application
- Enhanced dashboard with feature cards and value proposition highlights
- Improved Discovery tab with better visual organization and call-to-action elements

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **Layout**: Wide layout with expandable sidebar for configuration
- **Caching**: Uses `@st.cache_resource` for component initialization to improve performance
- **User Interface**: Clean, intuitive interface with emoji icons and markdown formatting

### Backend Architecture
- **Language**: Python 3.x
- **Architecture Pattern**: Modular component-based design
- **Core Components**:
  - Database Manager for data persistence
  - Domain Scraper for data acquisition
  - SEO Analyzer for search engine optimization metrics
  - Content Analyzer for content quality assessment
  - Domain Scorer for overall domain evaluation

### Data Storage Solutions
- **Database**: SQLite for local data persistence
- **Schema Design**: Normalized relational structure with separate tables for:
  - Domains (main entity)
  - SEO metrics (domain authority, backlinks, etc.)
  - Content analysis (niche, quality scores, keywords)
- **Data Models**: Dataclasses with enums for type safety and structure

## Key Components

### 1. Domain Scraper (`domain_scraper.py`)
- **Purpose**: Scrapes expired domains from public sources
- **Sources**: ExpiredDomains.net, auction sites, sample data for development
- **Features**: Session management, user-agent rotation, duplicate removal
- **Fallback**: Includes sample domain generation for development/testing

### 2. SEO Analyzer (`seo_analyzer.py`)
- **Purpose**: Analyzes SEO metrics for domain valuation
- **API Integrations**: Ahrefs, Moz, Majestic, SEMrush
- **Metrics**: Domain authority, page authority, backlinks, organic traffic, spam scores
- **Fallback**: Mock data generation when APIs are unavailable

### 3. Content Analyzer (`content_analyzer.py`)
- **Purpose**: Evaluates content quality and relevance
- **Technologies**: NLTK for natural language processing, trafilatura for content extraction
- **Features**: Sentiment analysis, keyword extraction, readability assessment
- **Language Support**: Multi-language content analysis

### 4. Domain Scorer (`domain_scorer.py`)
- **Purpose**: Calculates overall domain value scores
- **Scoring System**: Weighted scoring algorithm combining:
  - SEO metrics (40%)
  - Content quality (30%)
  - Brandability (20%)
  - Spam penalty (10%)
- **Customization**: Supports custom weight configurations

### 5. Database Manager (`database.py`)
- **Purpose**: Handles all database operations
- **Features**: Table initialization, CRUD operations, data relationships
- **Design**: Normalized schema with foreign key relationships

## Data Flow

1. **Domain Discovery**: Domain scraper collects expired domains from multiple sources
2. **Initial Storage**: Domains are stored in SQLite database with "discovered" status
3. **SEO Analysis**: SEO analyzer fetches metrics from various APIs
4. **Content Analysis**: Content analyzer evaluates historical content and brandability
5. **Scoring**: Domain scorer calculates weighted overall scores
6. **Results**: Processed domains are displayed in Streamlit interface with export options

## External Dependencies

### API Services
- **Ahrefs**: Backlink analysis and domain authority
- **Moz**: Page authority and spam scores
- **Majestic**: Trust flow and citation flow
- **SEMrush**: Organic traffic and keyword data

### Python Libraries
- **Web Framework**: Streamlit for UI
- **HTTP Requests**: requests library with session management
- **Data Processing**: pandas for data manipulation
- **Web Scraping**: BeautifulSoup for HTML parsing
- **NLP**: NLTK for text analysis and sentiment analysis
- **Content Extraction**: trafilatura for web content extraction
- **Database**: sqlite3 for local data storage

### Development Tools
- **Logging**: Built-in Python logging with file and console output
- **Data Export**: CSV export functionality
- **Environment Variables**: API key management via environment variables

## Deployment Strategy

### Local Development
- **Database**: SQLite for local development and testing
- **Configuration**: Environment variables for API keys
- **Logging**: File-based logging with configurable levels

### Production Considerations
- **Scalability**: Component-based design allows for easy scaling
- **Database Migration**: Architecture supports migration from SQLite to PostgreSQL
- **API Management**: Graceful fallback to mock data when APIs are unavailable
- **Error Handling**: Comprehensive error handling and logging throughout

### Security
- **API Keys**: Stored as environment variables
- **Request Headers**: Proper user-agent strings to avoid blocking
- **Rate Limiting**: Built-in delays and session management for web scraping

The application follows a clean architecture pattern with clear separation of concerns, making it maintainable and extensible for future enhancements.