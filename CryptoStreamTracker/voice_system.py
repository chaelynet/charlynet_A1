import pyttsx3
import logging
from gtts import gTTS
import os
import tempfile
import threading
from typing import Optional
import time

class VoiceSystem:
    """Sistema de respuestas habladas para el asistente cripto"""
    
    def __init__(self):
        self.tts_engine = None
        self.voice_enabled = True
        self.language = 'es'
        self.initialize_engine()
    
    def initialize_engine(self):
        """Inicializa el motor de síntesis de voz"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configurar propiedades de voz
            voices = self.tts_engine.getProperty('voices')
            
            # Buscar voz en español si está disponible
            spanish_voice = None
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    spanish_voice = voice.id
                    break
            
            if spanish_voice:
                self.tts_engine.setProperty('voice', spanish_voice)
            
            # Configurar velocidad y volumen
            self.tts_engine.setProperty('rate', 180)  # Palabras por minuto
            self.tts_engine.setProperty('volume', 0.8)  # Volumen (0.0 a 1.0)
            
            logging.info("Voice engine initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing voice engine: {str(e)}")
            self.tts_engine = None
    
    def speak_text(self, text: str, async_mode: bool = True) -> bool:
        """Convierte texto a voz usando pyttsx3 (offline)"""
        if not self.voice_enabled or not text:
            return False
        
        try:
            # Limpiar texto para TTS
            clean_text = self.clean_text_for_speech(text)
            
            if async_mode:
                # Ejecutar en hilo separado para no bloquear
                thread = threading.Thread(target=self._speak_sync, args=(clean_text,))
                thread.daemon = True
                thread.start()
                return True
            else:
                return self._speak_sync(clean_text)
                
        except Exception as e:
            logging.error(f"Error in speak_text: {str(e)}")
            return False
    
    def _speak_sync(self, text: str) -> bool:
        """Ejecuta síntesis de voz sincronizada"""
        try:
            if self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                return True
            return False
        except Exception as e:
            logging.error(f"Error in speech synthesis: {str(e)}")
            return False
    
    def speak_with_gtts(self, text: str, save_file: bool = False) -> Optional[str]:
        """Genera audio usando Google TTS (requiere internet)"""
        if not self.voice_enabled or not text:
            return None
        
        try:
            # Limpiar texto
            clean_text = self.clean_text_for_speech(text)
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                temp_filename = tmp_file.name
            
            # Generar audio con gTTS
            tts = gTTS(text=clean_text, lang=self.language, slow=False)
            tts.save(temp_filename)
            
            if save_file:
                # Guardar con nombre descriptivo
                timestamp = int(time.time())
                audio_filename = f"crypto_voice_{timestamp}.mp3"
                os.rename(temp_filename, audio_filename)
                return audio_filename
            else:
                # Reproducir y eliminar
                self._play_audio_file(temp_filename)
                os.unlink(temp_filename)
                return temp_filename
                
        except Exception as e:
            logging.error(f"Error with gTTS: {str(e)}")
            return None
    
    def _play_audio_file(self, filename: str):
        """Reproduce archivo de audio (placeholder - requiere reproductor)"""
        try:
            # En un entorno real, usarías pygame, playsound, o similar
            # Por ahora solo loggeamos
            logging.info(f"Audio file generated: {filename}")
        except Exception as e:
            logging.error(f"Error playing audio: {str(e)}")
    
    def clean_text_for_speech(self, text: str) -> str:
        """Limpia texto para síntesis de voz"""
        # Remover emojis y caracteres especiales
        import re
        
        # Reemplazar emojis con descripciones
        emoji_replacements = {
            '🚨': 'alerta',
            '📈': 'subida',
            '📉': 'bajada',
            '💰': 'dinero',
            '🔴': 'rojo',
            '🟢': 'verde',
            '⚠️': 'advertencia',
            '🔥': 'fuego',
            '🌙': 'luna',
            '🚀': 'cohete',
            '💎': 'diamante',
            '📊': 'gráfico',
            '🔍': 'análisis',
            '✅': 'correcto',
            '❌': 'error',
            '📰': 'noticias',
            '🌐': 'internet',
            '💡': 'idea'
        }
        
        clean_text = text
        for emoji, replacement in emoji_replacements.items():
            clean_text = clean_text.replace(emoji, f' {replacement} ')
        
        # Remover caracteres especiales excepto puntuación básica
        clean_text = re.sub(r'[^\w\s.,;:!?¿¡\-()]', ' ', clean_text)
        
        # Limpiar espacios múltiples
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Reemplazar abreviaciones comunes
        replacements = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'ADA': 'Cardano',
            'SOL': 'Solana',
            'XRP': 'Ripple',
            'DOT': 'Polkadot',
            'DOGE': 'Dogecoin',
            'AVAX': 'Avalanche',
            'LINK': 'Chainlink',
            'BNB': 'Binance Coin',
            'USD': 'dólares',
            '24h': 'veinticuatro horas',
            '%': 'por ciento',
            'API': 'A P I',
            'vs': 'versus'
        }
        
        for abbr, full in replacements.items():
            clean_text = clean_text.replace(abbr, full)
        
        return clean_text
    
    def speak_alert(self, alert_message: str) -> bool:
        """Reproduce alerta de voz específica"""
        try:
            # Prefijo para alertas
            alert_prefix = "Alerta de criptomonedas. "
            full_message = alert_prefix + alert_message
            
            return self.speak_text(full_message, async_mode=True)
            
        except Exception as e:
            logging.error(f"Error speaking alert: {str(e)}")
            return False
    
    def speak_price_update(self, crypto_name: str, price: float, change: float) -> bool:
        """Anuncia actualización de precio"""
        try:
            if change >= 0:
                message = f"{crypto_name} está en {price:.2f} dólares, con una subida del {change:.2f} por ciento"
            else:
                message = f"{crypto_name} está en {price:.2f} dólares, con una bajada del {abs(change):.2f} por ciento"
            
            return self.speak_text(message, async_mode=True)
            
        except Exception as e:
            logging.error(f"Error speaking price update: {str(e)}")
            return False
    
    def speak_analysis_summary(self, summary_text: str) -> bool:
        """Reproduce resumen de análisis"""
        try:
            # Tomar solo las partes más importantes para voz
            lines = summary_text.split('\n')
            important_lines = []
            
            for line in lines:
                # Filtrar líneas importantes
                if any(keyword in line.lower() for keyword in ['alerta', 'crítico', 'extremo', 'recomendación', 'movimiento']):
                    # Limpiar formato
                    clean_line = line.strip('- •=')
                    if clean_line and len(clean_line) > 10:
                        important_lines.append(clean_line)
            
            if important_lines:
                speech_text = ". ".join(important_lines[:3])  # Solo las 3 primeras
                return self.speak_text(speech_text, async_mode=True)
            
            return False
            
        except Exception as e:
            logging.error(f"Error speaking analysis: {str(e)}")
            return False
    
    def toggle_voice(self) -> bool:
        """Activa/desactiva el sistema de voz"""
        self.voice_enabled = not self.voice_enabled
        return self.voice_enabled
    
    def set_language(self, language: str) -> bool:
        """Cambia el idioma del sistema de voz"""
        try:
            self.language = language
            logging.info(f"Voice language set to: {language}")
            return True
        except Exception as e:
            logging.error(f"Error setting language: {str(e)}")
            return False
    
    def get_voice_status(self) -> dict:
        """Obtiene estado del sistema de voz"""
        return {
            'enabled': self.voice_enabled,
            'engine_available': self.tts_engine is not None,
            'language': self.language,
            'engine_type': 'pyttsx3' if self.tts_engine else 'none'
        }