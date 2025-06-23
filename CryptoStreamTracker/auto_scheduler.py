import logging
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Dict, Any
import threading

class AutoScheduler:
    """Programador automático para el asistente cripto con loop cada 60 min"""
    
    def __init__(self, crypto_service, alert_system, voice_system, external_sources):
        self.crypto_service = crypto_service
        self.alert_system = alert_system
        self.voice_system = voice_system
        self.external_sources = external_sources
        
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.last_analysis = None
        self.analysis_history = []
        
        # Configurar trabajos programados
        self.setup_scheduled_jobs()
    
    def setup_scheduled_jobs(self):
        """Configura todos los trabajos programados"""
        
        # 1. Análisis completo cada 60 minutos
        self.scheduler.add_job(
            func=self.comprehensive_analysis,
            trigger=IntervalTrigger(minutes=60),
            id='comprehensive_analysis_60min',
            name='Análisis Completo cada 60 minutos',
            max_instances=1,
            coalesce=True
        )
        
        # 2. Verificación de alertas cada 5 minutos
        self.scheduler.add_job(
            func=self.check_alerts,
            trigger=IntervalTrigger(minutes=5),
            id='alert_check_5min',
            name='Verificación de Alertas cada 5 minutos',
            max_instances=1,
            coalesce=True
        )
        
        # 3. Actualización de precios cada 2 minutos (ya existe en app.py pero lo reforzamos)
        self.scheduler.add_job(
            func=self.update_prices,
            trigger=IntervalTrigger(minutes=2),
            id='price_update_2min',
            name='Actualización de Precios cada 2 minutos',
            max_instances=1,
            coalesce=True
        )
        
        # 4. Análisis de fuentes externas cada 30 minutos
        self.scheduler.add_job(
            func=self.analyze_external_sources,
            trigger=IntervalTrigger(minutes=30),
            id='external_sources_30min',
            name='Análisis de Fuentes Externas cada 30 minutos',
            max_instances=1,
            coalesce=True
        )
        
        # 5. Limpieza de datos cada 6 horas
        self.scheduler.add_job(
            func=self.cleanup_data,
            trigger=IntervalTrigger(hours=6),
            id='cleanup_6h',
            name='Limpieza de Datos cada 6 horas',
            max_instances=1,
            coalesce=True
        )
        
        # 6. Resumen diario a las 9:00 AM
        self.scheduler.add_job(
            func=self.daily_summary,
            trigger=CronTrigger(hour=9, minute=0),
            id='daily_summary_9am',
            name='Resumen Diario a las 9:00 AM',
            max_instances=1,
            coalesce=True
        )
        
        logging.info("Scheduled jobs configured successfully")
    
    def start(self):
        """Inicia el programador automático"""
        try:
            if not self.is_running:
                self.scheduler.start()
                self.is_running = True
                
                # Ejecutar análisis inicial
                threading.Timer(5.0, self.initial_analysis).start()
                
                logging.info("🔄 Auto-scheduler started - Loop automático cada 60 min activado")
                return True
        except Exception as e:
            logging.error(f"Error starting scheduler: {str(e)}")
            return False
    
    def stop(self):
        """Detiene el programador automático"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logging.info("Auto-scheduler stopped")
                return True
        except Exception as e:
            logging.error(f"Error stopping scheduler: {str(e)}")
            return False
    
    def initial_analysis(self):
        """Análisis inicial al arrancar el sistema"""
        try:
            logging.info("🚀 Ejecutando análisis inicial del sistema...")
            
            # Actualizar precios primero
            self.update_prices()
            time.sleep(2)
            
            # Ejecutar análisis completo
            result = self.comprehensive_analysis()
            
            if result:
                # Anuncio por voz de inicio
                if self.voice_system and self.voice_system.voice_enabled:
                    self.voice_system.speak_text(
                        "Sistema de análisis cripto iniciado. Monitoreo automático activado.",
                        async_mode=True
                    )
                
                logging.info("✅ Análisis inicial completado exitosamente")
            
        except Exception as e:
            logging.error(f"Error in initial analysis: {str(e)}")
    
    def comprehensive_analysis(self):
        """Análisis completo del mercado cada 60 minutos"""
        try:
            timestamp = datetime.now()
            logging.info(f"🔍 Ejecutando análisis completo - {timestamp.strftime('%H:%M:%S')}")
            
            # 1. Actualizar datos de precios
            price_update = self.crypto_service.update_prices()
            
            # 2. Procesar alertas
            new_alerts = self.alert_system.process_alerts()
            
            # 3. Obtener análisis de movimientos
            from crypto_assistant import CryptoAssistant
            assistant = CryptoAssistant(self.crypto_service)
            movement_analysis = assistant.analizar_movimientos_extraños()
            
            # 4. Analizar fuentes externas (cada 2 ciclos = cada 2 horas)
            external_analysis = ""
            if len(self.analysis_history) % 2 == 0:
                external_analysis = self.external_sources.get_market_sentiment_summary()
            
            # 5. Compilar resultado
            analysis_result = {
                'timestamp': timestamp.isoformat(),
                'price_update_success': price_update,
                'new_alerts_count': len(new_alerts),
                'movement_analysis': movement_analysis,
                'external_analysis': external_analysis,
                'critical_alerts': len(self.alert_system.get_critical_alerts()),
                'market_status': self.determine_market_status(new_alerts)
            }
            
            # 6. Guardar en historial
            self.analysis_history.append(analysis_result)
            self.last_analysis = analysis_result
            
            # 7. Procesar alertas críticas con voz
            if new_alerts:
                critical_alerts = [a for a in new_alerts if a.severity == "critical"]
                if critical_alerts and self.voice_system:
                    alert_summary = f"Se detectaron {len(critical_alerts)} alertas críticas en el mercado cripto"
                    self.voice_system.speak_alert(alert_summary)
            
            # 8. Log de resumen
            logging.info(f"📊 Análisis completado: {len(new_alerts)} alertas, Status: {analysis_result['market_status']}")
            
            return analysis_result
            
        except Exception as e:
            logging.error(f"Error in comprehensive analysis: {str(e)}")
            return None
    
    def check_alerts(self):
        """Verificación rápida de alertas cada 5 minutos"""
        try:
            new_alerts = self.alert_system.process_alerts()
            
            if new_alerts:
                high_priority = [a for a in new_alerts if a.severity in ["critical", "high"]]
                
                if high_priority:
                    logging.info(f"⚠️ {len(high_priority)} alertas de alta prioridad detectadas")
                    
                    # Anuncio por voz para alertas críticas
                    critical = [a for a in high_priority if a.severity == "critical"]
                    if critical and self.voice_system:
                        for alert in critical[:2]:  # Solo las 2 primeras
                            self.voice_system.speak_alert(alert.message)
            
            return len(new_alerts)
            
        except Exception as e:
            logging.error(f"Error checking alerts: {str(e)}")
            return 0
    
    def update_prices(self):
        """Actualiza precios de criptomonedas"""
        try:
            result = self.crypto_service.update_prices()
            if result:
                logging.debug("💰 Precios actualizados correctamente")
            return result
        except Exception as e:
            logging.error(f"Error updating prices: {str(e)}")
            return False
    
    def analyze_external_sources(self):
        """Analiza fuentes externas cada 30 minutos"""
        try:
            logging.info("🌐 Analizando fuentes externas...")
            sentiment_summary = self.external_sources.get_market_sentiment_summary()
            
            # Guardar resultado para uso posterior
            self.last_external_analysis = {
                'timestamp': datetime.now().isoformat(),
                'summary': sentiment_summary
            }
            
            logging.info("📰 Análisis de fuentes externas completado")
            return sentiment_summary
            
        except Exception as e:
            logging.error(f"Error analyzing external sources: {str(e)}")
            return None
    
    def cleanup_data(self):
        """Limpia datos antiguos cada 6 horas"""
        try:
            # Limpiar historial de análisis (mantener últimos 24)
            if len(self.analysis_history) > 24:
                self.analysis_history = self.analysis_history[-24:]
            
            # Limpiar alertas antiguas
            cutoff_time = datetime.now() - timedelta(hours=48)
            original_count = len(self.alert_system.alert_history)
            
            self.alert_system.alert_history = [
                alert for alert in self.alert_system.alert_history 
                if alert.timestamp > cutoff_time
            ]
            
            cleaned_count = original_count - len(self.alert_system.alert_history)
            
            logging.info(f"🧹 Limpieza completada: {cleaned_count} alertas antiguas eliminadas")
            return cleaned_count
            
        except Exception as e:
            logging.error(f"Error in cleanup: {str(e)}")
            return 0
    
    def daily_summary(self):
        """Genera resumen diario a las 9:00 AM"""
        try:
            logging.info("📊 Generando resumen diario...")
            
            # Contar alertas de las últimas 24 horas
            yesterday = datetime.now() - timedelta(hours=24)
            recent_alerts = [
                alert for alert in self.alert_system.alert_history 
                if alert.timestamp > yesterday
            ]
            
            critical_count = len([a for a in recent_alerts if a.severity == "critical"])
            high_count = len([a for a in recent_alerts if a.severity == "high"])
            
            # Crear resumen
            summary = f"""Resumen diario de criptomonedas. 
            En las últimas 24 horas se detectaron {len(recent_alerts)} alertas,
            incluyendo {critical_count} críticas y {high_count} de alta prioridad."""
            
            # Anunciar por voz
            if self.voice_system:
                self.voice_system.speak_text(summary, async_mode=True)
            
            logging.info(f"📈 Resumen diario: {len(recent_alerts)} alertas totales")
            return summary
            
        except Exception as e:
            logging.error(f"Error generating daily summary: {str(e)}")
            return None
    
    def determine_market_status(self, alerts):
        """Determina el estado general del mercado"""
        if not alerts:
            return "STABLE"
        
        critical_count = len([a for a in alerts if a.severity == "critical"])
        high_count = len([a for a in alerts if a.severity == "high"])
        
        if critical_count >= 3:
            return "CRITICAL"
        elif critical_count >= 1 or high_count >= 5:
            return "HIGH_VOLATILITY"
        elif high_count >= 2:
            return "MODERATE_VOLATILITY"
        else:
            return "STABLE"
    
    def get_scheduler_status(self):
        """Obtiene estado del programador"""
        return {
            'running': self.is_running,
            'jobs_count': len(self.scheduler.get_jobs()) if self.is_running else 0,
            'last_analysis_time': self.last_analysis['timestamp'] if self.last_analysis else None,
            'analysis_count_24h': len(self.analysis_history),
            'next_analysis': self.get_next_analysis_time()
        }
    
    def get_next_analysis_time(self):
        """Obtiene la hora del próximo análisis"""
        try:
            if self.is_running:
                job = self.scheduler.get_job('comprehensive_analysis_60min')
                if job:
                    return job.next_run_time.isoformat() if job.next_run_time else None
        except:
            pass
        return None
    
    def force_analysis(self):
        """Fuerza un análisis inmediato"""
        try:
            logging.info("🔄 Forzando análisis inmediato...")
            result = self.comprehensive_analysis()
            return result is not None
        except Exception as e:
            logging.error(f"Error forcing analysis: {str(e)}")
            return False