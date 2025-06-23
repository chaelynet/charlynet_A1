import os
import logging
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from crypto_service import CryptoService
from crypto_assistant import CryptoAssistant, llamar_asistente
from alert_system import AlertSystem
from voice_system import VoiceSystem
from external_sources import ExternalSources
from auto_scheduler import AutoScheduler
from ai_network import CollaborativeAINetwork
import atexit

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Enable CORS for API endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize all systems
crypto_service = CryptoService()
crypto_assistant = CryptoAssistant(crypto_service)
alert_system = AlertSystem(crypto_service)
voice_system = VoiceSystem()
external_sources = ExternalSources()
ai_network = CollaborativeAINetwork(crypto_service)
auto_scheduler = AutoScheduler(crypto_service, alert_system, voice_system, external_sources)

# Initialize scheduler for periodic updates
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=crypto_service.update_prices,
    trigger="interval",
    seconds=60,  # Update every minute
    id='update_crypto_prices'
)
scheduler.start()

# Start auto-scheduler (60min loop)
auto_scheduler.start()

# Shut down the schedulers when exiting the app
atexit.register(lambda: scheduler.shutdown())
atexit.register(lambda: auto_scheduler.stop())

@app.route('/')
def index():
    """Main dashboard page with crypto price visualization"""
    return render_template('index.html')

@app.route('/api-docs')
def api_docs():
    """API documentation page"""
    return render_template('api_docs.html')

# API Routes
@app.route('/api/crypto/prices')
def get_all_prices():
    """Get current prices for all supported cryptocurrencies"""
    try:
        prices = crypto_service.get_all_prices()
        if not prices:
            return jsonify({
                'error': 'No price data available',
                'message': 'Unable to fetch cryptocurrency prices at this time'
            }), 503
        
        return jsonify({
            'success': True,
            'data': prices,
            'timestamp': crypto_service.get_last_update_time()
        })
    except Exception as e:
        logging.error(f"Error fetching all prices: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to fetch cryptocurrency prices'
        }), 500

@app.route('/api/crypto/prices/<symbol>')
def get_price_by_symbol(symbol):
    """Get current price for a specific cryptocurrency"""
    try:
        price_data = crypto_service.get_price_by_symbol(symbol.lower())
        if not price_data:
            return jsonify({
                'error': 'Cryptocurrency not found',
                'message': f'No data available for {symbol.upper()}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': price_data,
            'timestamp': crypto_service.get_last_update_time()
        })
    except Exception as e:
        logging.error(f"Error fetching price for {symbol}: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': f'Failed to fetch price for {symbol.upper()}'
        }), 500

@app.route('/api/crypto/history/<symbol>')
def get_price_history(symbol):
    """Get price history for a specific cryptocurrency"""
    try:
        days = request.args.get('days', '7', type=int)
        if days > 365:
            days = 365  # Limit to 1 year
        
        history = crypto_service.get_price_history(symbol.lower(), days)
        if not history:
            return jsonify({
                'error': 'History data not available',
                'message': f'No historical data available for {symbol.upper()}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': history,
            'symbol': symbol.upper(),
            'days': days
        })
    except Exception as e:
        logging.error(f"Error fetching history for {symbol}: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': f'Failed to fetch history for {symbol.upper()}'
        }), 500

@app.route('/api/crypto/supported')
def get_supported_cryptos():
    """Get list of supported cryptocurrencies"""
    try:
        supported = crypto_service.get_supported_cryptocurrencies()
        return jsonify({
            'success': True,
            'data': supported,
            'count': len(supported)
        })
    except Exception as e:
        logging.error(f"Error fetching supported cryptos: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to fetch supported cryptocurrencies'
        }), 500

@app.route('/api/crypto/analysis')
def get_crypto_analysis():
    """Get AI analysis of cryptocurrency movements"""
    try:
        analysis = crypto_assistant.analizar_movimientos_extraños()
        return jsonify({
            'success': True,
            'analysis': analysis,
            'timestamp': crypto_service.get_last_update_time()
        })
    except Exception as e:
        logging.error(f"Error generating crypto analysis: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'message': 'Unable to generate cryptocurrency analysis'
        }), 500

@app.route('/api/assistant')
def crypto_assistant_endpoint():
    """General crypto assistant endpoint"""
    try:
        query = request.args.get('q', '¿Cuáles son las criptomonedas con movimientos extraños hoy?')
        response = llamar_asistente(query)
        return jsonify({
            'success': True,
            'query': query,
            'response': response,
            'timestamp': crypto_service.get_last_update_time()
        })
    except Exception as e:
        logging.error(f"Error with crypto assistant: {str(e)}")
        return jsonify({
            'error': 'Assistant error',
            'message': 'Unable to process assistant query'
        }), 500

@app.route('/api/alerts')
def get_alerts():
    """Get active alerts"""
    try:
        active_alerts = alert_system.get_active_alerts()
        critical_alerts = alert_system.get_critical_alerts()
        alert_summary = alert_system.generate_alert_summary()
        
        return jsonify({
            'success': True,
            'active_alerts': len(active_alerts),
            'critical_alerts': len(critical_alerts),
            'summary': alert_summary,
            'timestamp': crypto_service.get_last_update_time()
        })
    except Exception as e:
        logging.error(f"Error fetching alerts: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch alerts',
            'message': str(e)
        }), 500

@app.route('/api/external-sources')
def get_external_sources():
    """Get external market sentiment"""
    try:
        sentiment_summary = external_sources.get_market_sentiment_summary()
        return jsonify({
            'success': True,
            'sentiment_analysis': sentiment_summary,
            'timestamp': crypto_service.get_last_update_time()
        })
    except Exception as e:
        logging.error(f"Error fetching external sources: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch external sources',
            'message': str(e)
        }), 500

@app.route('/api/voice/speak', methods=['POST'])
def speak_text():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        success = voice_system.speak_text(text, async_mode=True)
        return jsonify({
            'success': success,
            'message': 'Speech synthesis initiated' if success else 'Speech synthesis failed'
        })
    except Exception as e:
        logging.error(f"Error in speech synthesis: {str(e)}")
        return jsonify({
            'error': 'Speech synthesis failed',
            'message': str(e)
        }), 500

@app.route('/api/voice/toggle', methods=['POST'])
def toggle_voice():
    """Toggle voice system on/off"""
    try:
        enabled = voice_system.toggle_voice()
        return jsonify({
            'success': True,
            'voice_enabled': enabled,
            'message': f"Voice system {'enabled' if enabled else 'disabled'}"
        })
    except Exception as e:
        logging.error(f"Error toggling voice: {str(e)}")
        return jsonify({
            'error': 'Failed to toggle voice',
            'message': str(e)
        }), 500

@app.route('/api/scheduler/status')
def get_scheduler_status():
    """Get scheduler status"""
    try:
        status = auto_scheduler.get_scheduler_status()
        return jsonify({
            'success': True,
            'scheduler_status': status,
            'voice_status': voice_system.get_voice_status()
        })
    except Exception as e:
        logging.error(f"Error getting scheduler status: {str(e)}")
        return jsonify({
            'error': 'Failed to get scheduler status',
            'message': str(e)
        }), 500

@app.route('/api/ai-network/collaborative-analysis', methods=['POST'])
def collaborative_analysis():
    """Execute collaborative AI network analysis"""
    try:
        analysis_result = ai_network.execute_collaborative_analysis()
        return jsonify({
            'success': True,
            'collaborative_analysis': analysis_result,
            'timestamp': crypto_service.get_last_update_time()
        })
    except Exception as e:
        logging.error(f"Error in collaborative analysis: {str(e)}")
        return jsonify({
            'error': 'Collaborative analysis failed',
            'message': str(e)
        }), 500

@app.route('/api/scheduler/force-analysis', methods=['POST'])
def force_analysis():
    """Force immediate analysis"""
    try:
        success = auto_scheduler.force_analysis()
        return jsonify({
            'success': success,
            'message': 'Analysis completed' if success else 'Analysis failed'
        })
    except Exception as e:
        logging.error(f"Error forcing analysis: {str(e)}")
        return jsonify({
            'error': 'Failed to force analysis',
            'message': str(e)
        }), 500

@app.route('/api/status')
def api_status():
    """API health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'CharlyNet Crypto API',
        'last_update': crypto_service.get_last_update_time(),
        'supported_coins': len(crypto_service.get_supported_cryptocurrencies()),
        'auto_scheduler_running': auto_scheduler.is_running,
        'voice_enabled': voice_system.voice_enabled
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Initial price update
    crypto_service.update_prices()
    app.run(host='0.0.0.0', port=5000, debug=True)
