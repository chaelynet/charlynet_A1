# Guía de Despliegue Gratuito - CharlyNet Crypto API

## 🆓 OPCIONES GRATUITAS PARA EXTENDER EL SERVICIO

### 1. **Railway** (Recomendado - Más Fácil)
- **Costo**: $0/mes con límites generosos
- **Límites**: 500 horas/mes, 1GB RAM, 1GB almacenamiento
- **Ventajas**: Despliegue automático desde GitHub, base de datos PostgreSQL incluida
- **Pasos**:
  1. Crea cuenta en railway.app
  2. Conecta tu repositorio GitHub
  3. Railway detecta automáticamente Python/Flask
  4. Agrega variables de entorno necesarias
  5. Despliega automáticamente

### 2. **Render**
- **Costo**: $0/mes para servicios web
- **Límites**: Se duerme después de 15 min inactividad, 512MB RAM
- **Ventajas**: SSL automático, fácil configuración
- **Pasos**:
  1. Crea cuenta en render.com
  2. Conecta repositorio GitHub
  3. Configura como "Web Service"
  4. Agrega comando de inicio: `gunicorn --bind 0.0.0.0:$PORT main:app`

### 3. **Heroku** (Con Limitaciones)
- **Costo**: $0/mes hasta 550 horas
- **Límites**: Se duerme después de 30 min, no base de datos persistente gratis
- **Requiere**: Tarjeta de crédito para verificación

### 4. **Fly.io**
- **Costo**: $0/mes con créditos iniciales
- **Límites**: 3 micro VMs, 160GB transferencia
- **Ventajas**: Mejor rendimiento, múltiples regiones

### 5. **PythonAnywhere** (Especializado en Python)
- **Costo**: $0/mes para plan básico
- **Límites**: 1 aplicación web, 512MB almacenamiento
- **Ventajas**: Consola Python incluida, fácil manejo de dependencias

## 📋 PREPARACIÓN PARA EL DESPLIEGUE

### Archivos Necesarios (Ya incluidos en tu proyecto):
```
✅ requirements.txt (via pyproject.toml)
✅ main.py (punto de entrada)
✅ Procfile (para Heroku)
✅ .replit (configuración actual)
```

### Variables de Entorno a Configurar:
```env
# Obligatorias
FLASK_ENV=production
SECRET_KEY=tu_clave_secreta_aqui

# Opcionales (para funcionalidades completas)
REDDIT_CLIENT_ID=tu_reddit_client_id
REDDIT_CLIENT_SECRET=tu_reddit_client_secret
REDDIT_USER_AGENT=tu_user_agent

# Base de datos (se configura automáticamente en Railway/Render)
DATABASE_URL=postgresql://...
```

## 🚀 GUÍA PASO A PASO - RAILWAY (RECOMENDADO)

### Paso 1: Preparar el Código
```bash
# Ya está listo, pero asegúrate de tener estos archivos:
# main.py, requirements.txt, todos los .py del proyecto
```

### Paso 2: Subir a GitHub
1. Crea repositorio en GitHub
2. Sube todo el código del proyecto
3. Asegúrate que main.py esté en la raíz

### Paso 3: Desplegar en Railway
1. Ve a railway.app
2. "Login with GitHub"
3. "New Project" → "Deploy from GitHub repo"
4. Selecciona tu repositorio
5. Railway detecta automáticamente Python
6. Agrega variables de entorno en "Variables"
7. El servicio se despliega automáticamente

### Paso 4: Configurar Base de Datos (Opcional)
1. En Railway: "Add Service" → "Database" → "PostgreSQL"
2. Railway conecta automáticamente la DATABASE_URL
3. Tu aplicación ya está configurada para usarla

## 💡 CONSEJOS PARA OPTIMIZAR COSTOS

### 1. **Uso Eficiente de APIs**
```python
# Ya implementado en tu código:
# - Rate limiting en CoinGecko API
# - Caché de datos para reducir llamadas
# - Intervalos optimizados en el scheduler
```

### 2. **Optimizar Recursos**
- El auto-scheduler ya está optimizado (60 min ciclos principales)
- Sistema de cache implementado
- Manejo eficiente de memoria

### 3. **Monitoreo de Uso**
- Railway/Render muestran uso de recursos en tiempo real
- Configura alertas cuando te acerques a límites
- El sistema actual es muy eficiente en recursos

### 4. **Escalado Gratuito**
- Usa múltiples servicios gratuitos para diferentes regiones
- Implementa balanceador de carga simple
- Rota entre diferentes APIs gratuitas

## 🔧 CONFIGURACIÓN ESPECÍFICA POR PLATAFORMA

### Railway (requirements.txt automático desde pyproject.toml)
```toml
# pyproject.toml ya configurado correctamente
[project]
dependencies = [
    "flask",
    "flask-cors", 
    "apscheduler",
    # ... resto de dependencias
]
```

### Render (render.yaml - opcional)
```yaml
services:
- type: web
  name: charlynet-crypto
  env: python
  buildCommand: pip install -r requirements.txt
  startCommand: gunicorn --bind 0.0.0.0:$PORT main:app
```

### Variables de Entorno Mínimas
```env
PORT=5000
FLASK_ENV=production
SECRET_KEY=genera_una_clave_secreta_fuerte
```

## 📊 COMPARACIÓN DE OPCIONES

| Plataforma | Facilidad | Límites | Base de Datos | SSL | Recomendación |
|------------|-----------|---------|---------------|-----|---------------|
| Railway | ⭐⭐⭐⭐⭐ | Generosos | ✅ Gratis | ✅ | **MEJOR OPCIÓN** |
| Render | ⭐⭐⭐⭐ | Moderados | ⭐ Limitada | ✅ | Muy buena |
| Fly.io | ⭐⭐⭐ | Buenos | ✅ Gratis | ✅ | Técnicamente superior |
| PythonAnywhere | ⭐⭐⭐⭐ | Básicos | ❌ | ✅ | Simple pero limitada |
| Heroku | ⭐⭐ | Restrictivos | ❌ | ✅ | No recomendado |

## 🎯 RECOMENDACIÓN FINAL

**Para tu caso específico, te recomiendo Railway:**

1. **Más fácil**: Configuración automática
2. **Más generoso**: 500 horas/mes son suficientes
3. **Base de datos gratis**: PostgreSQL incluida
4. **Sin tarjeta**: No requiere tarjeta de crédito
5. **Escalable**: Fácil upgrade cuando tengas presupuesto

Tu aplicación actual está perfectamente optimizada para funcionar dentro de estos límites gratuitos.