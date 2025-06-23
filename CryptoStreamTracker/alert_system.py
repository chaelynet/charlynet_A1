import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json
import os

class AlertType(Enum):
    PRICE_SPIKE = "price_spike"
    PRICE_DROP = "price_drop"
    VOLUME_SURGE = "volume_surge"
    MARKET_CRASH = "market_crash"
    SENTIMENT_CHANGE = "sentiment_change"

@dataclass
class Alert:
    id: str
    timestamp: datetime
    crypto_symbol: str
    alert_type: AlertType
    message: str
    severity: str  # "low", "medium", "high", "critical"
    value: float
    threshold: float
    is_active: bool = True

class AlertSystem:
    """Sistema de alertas automáticas para criptomonedas"""
    
    def __init__(self, crypto_service):
        self.crypto_service = crypto_service
        self.alerts = []
        self.alert_history = []
        self.thresholds = {
            'price_change_24h': {'high': 15, 'medium': 10, 'low': 5},
            'volume_change': {'high': 100, 'medium': 50, 'low': 25},
            'market_cap_change': {'high': 20, 'medium': 15, 'low': 10}
        }
        self.load_alert_history()
    
    def check_price_alerts(self, current_data: Dict) -> List[Alert]:
        """Verifica alertas de precio"""
        new_alerts = []
        
        for symbol, data in current_data.items():
            price_change = data.get('price_change_24h', 0)
            current_price = data.get('current_price', 0)
            crypto_name = data.get('name', symbol.upper())
            
            # Alertas de cambios extremos
            if abs(price_change) >= self.thresholds['price_change_24h']['high']:
                severity = "critical" if abs(price_change) >= 20 else "high"
                alert_type = AlertType.PRICE_SPIKE if price_change > 0 else AlertType.PRICE_DROP
                
                direction = "subido" if price_change > 0 else "bajado"
                alert = Alert(
                    id=f"{symbol}_{alert_type.value}_{datetime.now().isoformat()}",
                    timestamp=datetime.now(),
                    crypto_symbol=symbol,
                    alert_type=alert_type,
                    message=f"🚨 {crypto_name} ({symbol.upper()}) ha {direction} {abs(price_change):.2f}% en 24h. Precio actual: ${current_price:,.2f}",
                    severity=severity,
                    value=price_change,
                    threshold=self.thresholds['price_change_24h']['high']
                )
                new_alerts.append(alert)
        
        return new_alerts
    
    def check_volume_alerts(self, current_data: Dict) -> List[Alert]:
        """Verifica alertas de volumen"""
        new_alerts = []
        
        for symbol, data in current_data.items():
            volume_24h = data.get('volume_24h', 0)
            market_cap = data.get('market_cap', 0)
            crypto_name = data.get('name', symbol.upper())
            
            # Calcular ratio volumen/market cap
            if market_cap > 0:
                volume_ratio = (volume_24h / market_cap) * 100
                
                if volume_ratio >= self.thresholds['volume_change']['medium']:
                    severity = "high" if volume_ratio >= self.thresholds['volume_change']['high'] else "medium"
                    
                    alert = Alert(
                        id=f"{symbol}_volume_surge_{datetime.now().isoformat()}",
                        timestamp=datetime.now(),
                        crypto_symbol=symbol,
                        alert_type=AlertType.VOLUME_SURGE,
                        message=f"📊 {crypto_name} ({symbol.upper()}) muestra volumen anómalo: {volume_ratio:.2f}% del market cap en 24h",
                        severity=severity,
                        value=volume_ratio,
                        threshold=self.thresholds['volume_change']['medium']
                    )
                    new_alerts.append(alert)
        
        return new_alerts
    
    def check_market_alerts(self, current_data: Dict) -> List[Alert]:
        """Verifica alertas del mercado general"""
        new_alerts = []
        
        # Contar cuántas cryptos están cayendo significativamente
        major_drops = 0
        total_cryptos = len(current_data)
        
        for symbol, data in current_data.items():
            price_change = data.get('price_change_24h', 0)
            if price_change <= -10:
                major_drops += 1
        
        # Si más del 70% del mercado está cayendo fuertemente
        crash_percentage = (major_drops / total_cryptos) * 100
        if crash_percentage >= 70:
            alert = Alert(
                id=f"market_crash_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                crypto_symbol="MARKET",
                alert_type=AlertType.MARKET_CRASH,
                message=f"🔴 ALERTA DE MERCADO: {crash_percentage:.0f}% de las criptomonedas están cayendo más del 10%. Posible crash del mercado detectado.",
                severity="critical",
                value=crash_percentage,
                threshold=70
            )
            new_alerts.append(alert)
        
        return new_alerts
    
    def process_alerts(self) -> List[Alert]:
        """Procesa todas las alertas automáticamente"""
        try:
            # Obtener datos actuales
            current_data = self.crypto_service.get_all_prices()
            if not current_data:
                return []
            
            all_new_alerts = []
            
            # Verificar diferentes tipos de alertas
            all_new_alerts.extend(self.check_price_alerts(current_data))
            all_new_alerts.extend(self.check_volume_alerts(current_data))
            all_new_alerts.extend(self.check_market_alerts(current_data))
            
            # Filtrar alertas duplicadas recientes (últimas 4 horas)
            filtered_alerts = self.filter_duplicate_alerts(all_new_alerts)
            
            # Agregar a la lista de alertas activas
            self.alerts.extend(filtered_alerts)
            self.alert_history.extend(filtered_alerts)
            
            # Guardar historial
            self.save_alert_history()
            
            return filtered_alerts
            
        except Exception as e:
            logging.error(f"Error procesando alertas: {str(e)}")
            return []
    
    def filter_duplicate_alerts(self, new_alerts: List[Alert]) -> List[Alert]:
        """Filtra alertas duplicadas de las últimas 4 horas"""
        cutoff_time = datetime.now() - timedelta(hours=4)
        
        filtered = []
        for alert in new_alerts:
            # Buscar alertas similares recientes
            is_duplicate = False
            for existing in self.alert_history:
                if (existing.timestamp > cutoff_time and 
                    existing.crypto_symbol == alert.crypto_symbol and
                    existing.alert_type == alert.alert_type):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(alert)
        
        return filtered
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtiene alertas activas de las últimas 24 horas"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        return [alert for alert in self.alerts if alert.timestamp > cutoff_time and alert.is_active]
    
    def get_critical_alerts(self) -> List[Alert]:
        """Obtiene solo alertas críticas activas"""
        active_alerts = self.get_active_alerts()
        return [alert for alert in active_alerts if alert.severity == "critical"]
    
    def generate_alert_summary(self) -> str:
        """Genera un resumen de alertas activas"""
        active_alerts = self.get_active_alerts()
        
        if not active_alerts:
            return "✅ No hay alertas activas en este momento."
        
        summary = []
        summary.append(f"🚨 ALERTAS ACTIVAS ({len(active_alerts)}):")
        summary.append("=" * 50)
        
        # Agrupar por severidad
        critical = [a for a in active_alerts if a.severity == "critical"]
        high = [a for a in active_alerts if a.severity == "high"]
        medium = [a for a in active_alerts if a.severity == "medium"]
        
        for severity, alerts in [("CRÍTICAS", critical), ("ALTAS", high), ("MEDIAS", medium)]:
            if alerts:
                summary.append(f"\n🔴 {severity} ({len(alerts)}):")
                for alert in alerts[-3:]:  # Mostrar solo las 3 más recientes
                    time_str = alert.timestamp.strftime("%H:%M")
                    summary.append(f"• [{time_str}] {alert.message}")
        
        summary.append(f"\n📊 Total de alertas en 24h: {len(active_alerts)}")
        return "\n".join(summary)
    
    def save_alert_history(self):
        """Guarda el historial de alertas"""
        try:
            # Mantener solo las últimas 1000 alertas
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
            
            # Convertir alertas a diccionarios para JSON
            alert_data = []
            for alert in self.alert_history[-100:]:  # Guardar solo las últimas 100
                alert_data.append({
                    'id': alert.id,
                    'timestamp': alert.timestamp.isoformat(),
                    'crypto_symbol': alert.crypto_symbol,
                    'alert_type': alert.alert_type.value,
                    'message': alert.message,
                    'severity': alert.severity,
                    'value': alert.value,
                    'threshold': alert.threshold,
                    'is_active': alert.is_active
                })
            
            with open('alert_history.json', 'w') as f:
                json.dump(alert_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error guardando historial de alertas: {str(e)}")
    
    def load_alert_history(self):
        """Carga el historial de alertas"""
        try:
            if os.path.exists('alert_history.json'):
                with open('alert_history.json', 'r') as f:
                    alert_data = json.load(f)
                
                for data in alert_data:
                    alert = Alert(
                        id=data['id'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        crypto_symbol=data['crypto_symbol'],
                        alert_type=AlertType(data['alert_type']),
                        message=data['message'],
                        severity=data['severity'],
                        value=data['value'],
                        threshold=data['threshold'],
                        is_active=data['is_active']
                    )
                    self.alert_history.append(alert)
                    
        except Exception as e:
            logging.error(f"Error cargando historial de alertas: {str(e)}")