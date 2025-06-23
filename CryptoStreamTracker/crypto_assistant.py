import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from crypto_service import CryptoService

class CryptoAssistant:
    """Asistente para análisis de movimientos de criptomonedas"""
    
    def __init__(self, crypto_service: CryptoService):
        self.crypto_service = crypto_service
        
    def analizar_movimientos_extraños(self) -> str:
        """Analiza las criptomonedas y detecta movimientos extraños"""
        try:
            # Asegurar que tenemos datos actualizados
            self.crypto_service.update_prices()
            
            # Obtener datos actuales de precios
            precios = self.crypto_service.get_all_prices()
            
            if not precios:
                return "No se pudieron obtener los datos de precios actuales."
            
            movimientos_extraños = []
            movimientos_normales = []
            
            # Analizar cada criptomoneda
            for simbolo, datos in precios.items():
                cambio_24h = datos.get('price_change_24h', 0)
                precio_actual = datos.get('current_price', 0)
                nombre = datos.get('name', simbolo.upper())
                
                # Detectar movimientos extraños (más de ±10%)
                if abs(cambio_24h) > 10:
                    tipo_movimiento = "📈 ALZA EXTREMA" if cambio_24h > 0 else "📉 CAÍDA EXTREMA"
                    movimientos_extraños.append({
                        'nombre': nombre,
                        'simbolo': simbolo.upper(),
                        'precio': precio_actual,
                        'cambio': cambio_24h,
                        'tipo': tipo_movimiento
                    })
                elif abs(cambio_24h) > 5:
                    tipo_movimiento = "📊 MOVIMIENTO NOTABLE" if cambio_24h > 0 else "📊 CAÍDA NOTABLE"
                    movimientos_extraños.append({
                        'nombre': nombre,
                        'simbolo': simbolo.upper(),
                        'precio': precio_actual,
                        'cambio': cambio_24h,
                        'tipo': tipo_movimiento
                    })
                else:
                    movimientos_normales.append({
                        'nombre': nombre,
                        'simbolo': simbolo.upper(),
                        'cambio': cambio_24h
                    })
            
            # Generar respuesta
            respuesta = self._generar_reporte_movimientos(movimientos_extraños, movimientos_normales)
            return respuesta
            
        except Exception as e:
            logging.error(f"Error analizando movimientos: {str(e)}")
            return f"Error al analizar movimientos de criptomonedas: {str(e)}"
    
    def _generar_reporte_movimientos(self, extraños: List[Dict], normales: List[Dict]) -> str:
        """Genera un reporte legible de los movimientos"""
        
        # Ordenar movimientos extraños por magnitud del cambio
        extraños_ordenados = sorted(extraños, key=lambda x: abs(x['cambio']), reverse=True)
        
        reporte = []
        
        # Título del reporte
        fecha_actual = datetime.now().strftime("%d de %B, %Y a las %H:%M")
        reporte.append(f"🔍 ANÁLISIS DE MOVIMIENTOS CRIPTO - {fecha_actual}")
        reporte.append("=" * 60)
        
        if extraños_ordenados:
            reporte.append("\n🚨 MOVIMIENTOS EXTRAÑOS DETECTADOS:")
            reporte.append("-" * 40)
            
            for crypto in extraños_ordenados:
                signo = "+" if crypto['cambio'] > 0 else ""
                precio_formateado = f"${crypto['precio']:,.2f}" if crypto['precio'] >= 1 else f"${crypto['precio']:.8f}"
                
                reporte.append(f"\n{crypto['tipo']}")
                reporte.append(f"💰 {crypto['nombre']} ({crypto['simbolo']})")
                reporte.append(f"   Precio actual: {precio_formateado}")
                reporte.append(f"   Cambio 24h: {signo}{crypto['cambio']:.2f}%")
                
                # Análisis del movimiento
                if abs(crypto['cambio']) > 15:
                    reporte.append("   ⚠️  MOVIMIENTO MUY VOLÁTIL - Revisar noticias")
                elif abs(crypto['cambio']) > 10:
                    reporte.append("   ⚡ Movimiento significativo - Monitorear de cerca")
                else:
                    reporte.append("   📋 Movimiento notable - Observar tendencia")
        else:
            reporte.append("\n✅ NO SE DETECTARON MOVIMIENTOS EXTRAÑOS")
            reporte.append("Todas las criptomonedas muestran variaciones normales (< 5%)")
        
        # Resumen de movimientos normales
        if normales:
            reporte.append(f"\n📊 CRIPTOMONEDAS CON MOVIMIENTOS NORMALES ({len(normales)}):")
            reporte.append("-" * 50)
            
            for crypto in normales[:5]:  # Mostrar solo las primeras 5
                signo = "+" if crypto['cambio'] > 0 else ""
                reporte.append(f"• {crypto['nombre']} ({crypto['simbolo']}): {signo}{crypto['cambio']:.2f}%")
            
            if len(normales) > 5:
                reporte.append(f"... y {len(normales) - 5} más con movimientos normales")
        
        # Recomendaciones
        reporte.append("\n💡 RECOMENDACIONES:")
        reporte.append("-" * 20)
        
        if extraños_ordenados:
            alta_volatilidad = len([c for c in extraños_ordenados if abs(c['cambio']) > 15])
            if alta_volatilidad > 0:
                reporte.append("🔥 Alta volatilidad detectada - Considerar estrategias de gestión de riesgo")
            
            subidas_extremas = len([c for c in extraños_ordenados if c['cambio'] > 10])
            caidas_extremas = len([c for c in extraños_ordenados if c['cambio'] < -10])
            
            if subidas_extremas > caidas_extremas:
                reporte.append("📈 Tendencia alcista dominante en el mercado")
            elif caidas_extremas > subidas_extremas:
                reporte.append("📉 Tendencia bajista dominante - Precaución recomendada")
            else:
                reporte.append("⚖️  Mercado mixto - Evaluar cada posición individualmente")
        else:
            reporte.append("🌊 Mercado estable - Buen momento para estrategias a largo plazo")
        
        reporte.append("\n🔄 Datos actualizados automáticamente cada minuto")
        reporte.append("📡 Fuente: CoinGecko API a través de CharlyNet Crypto API")
        
        return "\n".join(reporte)

def llamar_asistente(consulta: str) -> str:
    """Función principal para llamar al asistente cripto"""
    
    # Inicializar servicios
    crypto_service = CryptoService()
    asistente = CryptoAssistant(crypto_service)
    
    # Actualizar precios antes del análisis
    crypto_service.update_prices()
    
    # Procesar la consulta
    consulta_lower = consulta.lower()
    
    if any(palabra in consulta_lower for palabra in ['movimientos extraños', 'movimientos extraños', 'volatilidad', 'cambios raros']):
        return asistente.analizar_movimientos_extraños()
    elif any(palabra in consulta_lower for palabra in ['precios', 'cotizaciones', 'valores']):
        precios = crypto_service.get_all_prices()
        if precios:
            respuesta = "💰 PRECIOS ACTUALES DE CRIPTOMONEDAS:\n"
            respuesta += "=" * 40 + "\n"
            for simbolo, datos in precios.items():
                precio = f"${datos['current_price']:,.2f}" if datos['current_price'] >= 1 else f"${datos['current_price']:.8f}"
                cambio = datos['price_change_24h']
                signo = "+" if cambio > 0 else ""
                respuesta += f"• {datos['name']} ({simbolo.upper()}): {precio} ({signo}{cambio:.2f}%)\n"
            return respuesta
        else:
            return "No se pudieron obtener los precios actuales."
    else:
        return asistente.analizar_movimientos_extraños()

if __name__ == "__main__":
    respuesta = llamar_asistente("¿Cuáles son las criptomonedas con movimientos extraños hoy?")
    print("Respuesta del asistente:")
    print(respuesta)