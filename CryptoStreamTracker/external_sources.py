import requests
import feedparser
import praw
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import time

class ExternalSources:
    """Integración con fuentes externas de noticias cripto"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CharlyNet-Crypto-Bot/1.0'
        })
        self.reddit = None
        self.initialize_reddit()
    
    def initialize_reddit(self):
        """Inicializa conexión con Reddit"""
        try:
            # Reddit requiere credenciales - se configurará después
            self.reddit = None
            logging.info("Reddit initialization pending credentials")
        except Exception as e:
            logging.warning(f"Reddit initialization failed: {str(e)}")
    
    def get_cryptopanic_news(self, limit: int = 10) -> List[Dict]:
        """Obtiene noticias de CryptoPanic"""
        try:
            # CryptoPanic API pública (limitada)
            url = "https://cryptopanic.com/api/v1/posts/"
            params = {
                'auth_token': 'free',  # Token público limitado
                'currencies': 'BTC,ETH,BNB,ADA,SOL,XRP,DOT,DOGE,AVAX,LINK',
                'filter': 'hot',
                'public': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for post in data.get('results', [])[:limit]:
                    news_items.append({
                        'title': post.get('title', ''),
                        'url': post.get('url', ''),
                        'published': post.get('published_at', ''),
                        'source': post.get('source', {}).get('title', 'CryptoPanic'),
                        'currencies': [c.get('code') for c in post.get('currencies', [])],
                        'votes': post.get('votes', {}).get('positive', 0) - post.get('votes', {}).get('negative', 0),
                        'sentiment': self.analyze_sentiment(post.get('title', ''))
                    })
                
                return news_items
                
        except Exception as e:
            logging.error(f"Error fetching CryptoPanic news: {str(e)}")
        
        return []
    
    def get_reddit_sentiment(self, subreddits: List[str] = None) -> Dict:
        """Obtiene sentimiento de Reddit"""
        if not subreddits:
            subreddits = ['cryptocurrency', 'bitcoin', 'ethereum', 'cryptomarkets']
        
        sentiment_data = {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'total_posts': 0,
            'trending_topics': [],
            'summary': ''
        }
        
        try:
            if self.reddit:
                for subreddit_name in subreddits:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Obtener posts populares
                    for post in subreddit.hot(limit=20):
                        sentiment = self.analyze_sentiment(post.title + ' ' + post.selftext)
                        sentiment_data[sentiment] += 1
                        sentiment_data['total_posts'] += 1
                        
                        # Extraer menciones de cryptos
                        crypto_mentions = self.extract_crypto_mentions(post.title)
                        sentiment_data['trending_topics'].extend(crypto_mentions)
            
            # Generar resumen
            if sentiment_data['total_posts'] > 0:
                pos_pct = (sentiment_data['positive'] / sentiment_data['total_posts']) * 100
                neg_pct = (sentiment_data['negative'] / sentiment_data['total_posts']) * 100
                
                if pos_pct > 60:
                    mood = "optimista"
                elif neg_pct > 60:
                    mood = "pesimista"
                else:
                    mood = "neutral"
                
                sentiment_data['summary'] = f"Sentimiento Reddit: {mood} ({pos_pct:.1f}% positivo, {neg_pct:.1f}% negativo)"
            else:
                sentiment_data['summary'] = "Datos de Reddit no disponibles"
                
        except Exception as e:
            logging.error(f"Error getting Reddit sentiment: {str(e)}")
            sentiment_data['summary'] = "Error accediendo a Reddit"
        
        return sentiment_data
    
    def get_crypto_feeds(self) -> List[Dict]:
        """Obtiene feeds RSS de sitios cripto"""
        feeds = [
            'https://cointelegraph.com/rss',
            'https://coindesk.com/arc/outboundfeeds/rss/',
            'https://decrypt.co/feed'
        ]
        
        all_news = []
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # 5 por feed
                    published = entry.get('published_parsed')
                    if published:
                        pub_date = datetime(*published[:6])
                    else:
                        pub_date = datetime.now()
                    
                    # Solo noticias de las últimas 24 horas
                    if pub_date > datetime.now() - timedelta(hours=24):
                        all_news.append({
                            'title': entry.get('title', ''),
                            'url': entry.get('link', ''),
                            'published': pub_date.isoformat(),
                            'source': feed.feed.get('title', 'RSS Feed'),
                            'summary': entry.get('summary', ''),
                            'sentiment': self.analyze_sentiment(entry.get('title', '') + ' ' + entry.get('summary', ''))
                        })
                        
            except Exception as e:
                logging.error(f"Error parsing feed {feed_url}: {str(e)}")
        
        # Ordenar por fecha
        all_news.sort(key=lambda x: x['published'], reverse=True)
        return all_news[:15]  # Retornar las 15 más recientes
    
    def analyze_sentiment(self, text: str) -> str:
        """Análisis básico de sentimiento"""
        if not text:
            return 'neutral'
        
        text_lower = text.lower()
        
        # Palabras positivas
        positive_words = [
            'bullish', 'moon', 'pump', 'rally', 'surge', 'breakthrough', 'adoption',
            'partnership', 'upgrade', 'launch', 'success', 'milestone', 'growth',
            'positive', 'gain', 'rise', 'increase', 'buy', 'bull', 'rocket'
        ]
        
        # Palabras negativas
        negative_words = [
            'bearish', 'crash', 'dump', 'drop', 'fall', 'decline', 'hack', 'scam',
            'regulation', 'ban', 'fear', 'uncertainty', 'sell', 'bear', 'panic',
            'negative', 'loss', 'decrease', 'risk', 'warning', 'concern'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def extract_crypto_mentions(self, text: str) -> List[str]:
        """Extrae menciones de criptomonedas del texto"""
        crypto_symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK']
        crypto_names = ['bitcoin', 'ethereum', 'cardano', 'solana', 'ripple', 'polkadot', 'dogecoin', 'avalanche', 'chainlink']
        
        mentions = []
        text_upper = text.upper()
        text_lower = text.lower()
        
        for symbol in crypto_symbols:
            if symbol in text_upper:
                mentions.append(symbol)
        
        for name in crypto_names:
            if name in text_lower:
                mentions.append(name.upper())
        
        return list(set(mentions))  # Eliminar duplicados
    
    def get_market_sentiment_summary(self) -> str:
        """Genera resumen completo del sentimiento del mercado"""
        try:
            # Obtener datos de múltiples fuentes
            cryptopanic_news = self.get_cryptopanic_news(5)
            reddit_sentiment = self.get_reddit_sentiment()
            rss_news = self.get_crypto_feeds()
            
            summary = []
            summary.append("🌐 ANÁLISIS DE FUENTES EXTERNAS")
            summary.append("=" * 45)
            
            # Análisis de noticias
            if cryptopanic_news:
                positive_news = sum(1 for n in cryptopanic_news if n['sentiment'] == 'positive')
                negative_news = sum(1 for n in cryptopanic_news if n['sentiment'] == 'negative')
                
                summary.append(f"\n📰 NOTICIAS CRYPTOPANIC ({len(cryptopanic_news)} artículos):")
                summary.append(f"   Positivas: {positive_news} | Negativas: {negative_news}")
                
                # Mostrar noticia más relevante
                if cryptopanic_news:
                    top_news = max(cryptopanic_news, key=lambda x: x['votes'])
                    summary.append(f"   🔥 Trending: {top_news['title'][:60]}...")
            
            # Sentimiento de Reddit
            summary.append(f"\n🔴 REDDIT SENTIMENT:")
            summary.append(f"   {reddit_sentiment['summary']}")
            
            # Análisis de feeds RSS
            if rss_news:
                recent_positive = sum(1 for n in rss_news if n['sentiment'] == 'positive')
                recent_negative = sum(1 for n in rss_news if n['sentiment'] == 'negative')
                
                summary.append(f"\n📡 MEDIOS ESPECIALIZADOS ({len(rss_news)} artículos 24h):")
                summary.append(f"   Tono positivo: {recent_positive} | Tono negativo: {recent_negative}")
                
                if rss_news:
                    latest = rss_news[0]
                    summary.append(f"   📌 Último: {latest['title'][:50]}...")
            
            # Resumen general
            summary.append(f"\n💡 CONCLUSIÓN:")
            
            total_positive = sum([
                len([n for n in cryptopanic_news if n['sentiment'] == 'positive']),
                reddit_sentiment['positive'],
                len([n for n in rss_news if n['sentiment'] == 'positive'])
            ])
            
            total_negative = sum([
                len([n for n in cryptopanic_news if n['sentiment'] == 'negative']),
                reddit_sentiment['negative'],
                len([n for n in rss_news if n['sentiment'] == 'negative'])
            ])
            
            if total_positive > total_negative * 1.5:
                mood = "OPTIMISTA - Sentimiento mayoritariamente positivo"
            elif total_negative > total_positive * 1.5:
                mood = "PESIMISTA - Sentimiento mayoritariamente negativo"
            else:
                mood = "NEUTRAL - Sentimiento mixto en el mercado"
            
            summary.append(f"   {mood}")
            summary.append(f"\n🔄 Actualizado: {datetime.now().strftime('%H:%M:%S')}")
            
            return "\n".join(summary)
            
        except Exception as e:
            logging.error(f"Error generating market sentiment: {str(e)}")
            return f"❌ Error obteniendo datos de fuentes externas: {str(e)}"