# Replit Configuration

## Overview

CharlyNet Crypto API is a Flask-based web application that provides real-time cryptocurrency price tracking and visualization. The application fetches data from the CoinGecko API and presents it through both a web dashboard and RESTful API endpoints. It features automated price updates, responsive web interface, and comprehensive API documentation.

## System Architecture

### Backend Framework
- **Flask**: Python web framework serving as the main application server
- **Architecture Pattern**: MVC (Model-View-Controller) with service layer abstraction
- **API Design**: RESTful endpoints under `/api/` namespace
- **Background Processing**: APScheduler for periodic cryptocurrency price updates

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default) for server-side rendering
- **CSS Framework**: Bootstrap with dark theme for responsive UI
- **JavaScript**: Vanilla JavaScript with Chart.js for data visualization
- **CORS**: Enabled for API endpoints to support external consumption

### Data Layer
- **External API**: CoinGecko API v3 for cryptocurrency market data
- **Caching Strategy**: In-memory caching with timestamp-based invalidation
- **Data Models**: Service layer abstraction (CryptoService) for data operations

## Key Components

### Core Services
1. **CryptoService** (`crypto_service.py`): 
   - Handles all cryptocurrency data operations
   - Manages API rate limiting and error handling
   - Implements caching mechanism for performance
   - Supports 10 major cryptocurrencies (Bitcoin, Ethereum, BNB, etc.)

2. **Flask Application** (`app.py`):
   - Web server and API endpoint definitions
   - Background scheduler integration
   - CORS configuration for cross-origin requests

3. **Web Interface**:
   - Dashboard (`templates/index.html`): Real-time price visualization
   - API Documentation (`templates/api_docs.html`): Complete endpoint reference
   - Custom styling (`static/css/custom.css`): Dark theme with modern UI
   - Interactive JavaScript (`static/js/app.js`): Chart rendering and auto-refresh

### API Endpoints Structure
- `/api/crypto/prices`: Get all current cryptocurrency prices
- `/api/crypto/supported`: List all supported cryptocurrencies
- Additional endpoints for individual crypto data and historical prices

## Data Flow

1. **Initialization**: Flask app starts and initializes CryptoService
2. **Background Updates**: APScheduler triggers price updates every 60 seconds
3. **API Requests**: CryptoService makes HTTP requests to CoinGecko API
4. **Data Processing**: Raw API data is processed and cached locally
5. **Client Requests**: Web dashboard and API consumers receive cached data
6. **Real-time Updates**: Frontend polls API endpoints for live price updates

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **Flask-CORS**: Cross-origin resource sharing
- **APScheduler**: Background task scheduling
- **Requests**: HTTP client for external API calls
- **Gunicorn**: WSGI HTTP server for production deployment

### External Services
- **CoinGecko API**: Primary data source for cryptocurrency prices
- **CDN Resources**: Bootstrap CSS framework and Font Awesome icons

### Development Tools
- **PostgreSQL**: Database system (configured but not yet implemented)
- **OpenSSL**: SSL/TLS support for secure connections

## Deployment Strategy

### Production Environment
- **Server**: Gunicorn WSGI server with auto-scaling deployment target
- **Port Configuration**: Application runs on port 5000
- **Process Management**: Gunicorn handles multiple worker processes
- **Reloading**: Hot reload enabled for development workflows

### Development Environment
- **Debug Mode**: Flask debug mode enabled for development
- **Auto-reload**: File watching for automatic server restarts
- **Environment Variables**: Support for configuration via environment variables

### Infrastructure
- **Platform**: Replit with Nix package management
- **Python Version**: Python 3.11
- **System Packages**: OpenSSL and PostgreSQL pre-installed
- **Deployment**: Automated deployment with workflow configuration

## Changelog

- June 22, 2025: Initial setup - Basic crypto API and dashboard
- June 22, 2025: Advanced features implemented:
  * Auto-scheduler with 60-minute analysis loops
  * Intelligent alert system with multiple severity levels
  * Voice synthesis integration (pyttsx3 + gTTS)
  * External sources integration (Reddit, CryptoPanic, RSS feeds)
  * Interactive dashboard with multi-function control panel
  * Real-time sentiment analysis and market monitoring
  * Collaborative AI Network EXPANDED with 9 specialized AIs:
    - charly_news: Current crypto news analysis and summarization
    - price_tracer: Real price verification from CoinMarketCap
    - technical_analyst: Technical analysis and trading patterns
    - market_correlation: Market correlations and macro-economy analysis
    - onchain_analyst: On-chain metrics and blockchain activity
    - sentinella: Headline reliability and bias analysis
    - charly_alert: Real alert evaluation and validity assessment
    - charly_plan: Action plan suggestions based on market conditions
    - ia_opinion: Second opinion validation for uncertain results

## User Preferences

Preferred communication style: Simple, everyday language.

## Deployment Options

The user is interested in extending this service for free due to budget constraints. Multiple free deployment options have been documented in `deployment_guide.md` and `export_guide.md` with Railway being the recommended platform for its generous free tier and automatic configuration.