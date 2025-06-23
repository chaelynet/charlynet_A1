# Guía de Exportación del Proyecto

## 📦 CÓMO EXPORTAR TU PROYECTO DE REPLIT

### Método 1: Descarga Directa (Más Fácil)
1. En Replit, ve al panel de archivos (izquierda)
2. Haz clic en los 3 puntos (...) junto a "Files"
3. Selecciona "Download as zip"
4. Descomprime el archivo en tu computadora

### Método 2: Git Clone (Recomendado para GitHub)
```bash
# En tu terminal local:
git clone https://github.com/tu-usuario/tu-repo.git
```

### Método 3: Sincronización con GitHub
1. En Replit: Tools → Git → "Connect to GitHub"
2. Crea nuevo repositorio o conecta existente
3. Todos los cambios se sincronizan automáticamente
4. Úsalo desde GitHub para deploys

## 📋 ARCHIVOS ESENCIALES PARA EL DESPLIEGUE

### Archivos Principales ✅
```
main.py              # Punto de entrada
app.py              # Aplicación Flask principal
crypto_service.py   # Servicio de criptomonedas
ai_network.py       # Red colaborativa de IAs (9 IAs)
alert_system.py     # Sistema de alertas
voice_system.py     # Sistema de voz
external_sources.py # Fuentes externas
auto_scheduler.py   # Programador automático
crypto_assistant.py # Asistente crypto
```

### Archivos de Configuración ✅
```
pyproject.toml      # Dependencias Python
uv.lock            # Lock file de dependencias
.replit            # Configuración Replit (opcional para otros)
replit.md          # Documentación del proyecto
```

### Carpetas Estáticas ✅
```
templates/         # Plantillas HTML
├── index.html    # Dashboard principal
└── api_docs.html # Documentación API

static/           # Archivos estáticos
├── css/
│   └── custom.css
└── js/
    └── app.js    # JavaScript del frontend
```

### Archivos de Datos ✅
```
alert_history.json  # Historial de alertas (opcional)
```

## 🔧 PREPARACIÓN PARA DIFERENTES PLATAFORMAS

### Para Railway/Render/Fly.io:
- ✅ main.py (ya existe)
- ✅ pyproject.toml (ya configurado)
- ✅ Código optimizado para producción

### Para Heroku (requiere Procfile):
```bash
# Crear Procfile en la raíz:
echo "web: gunicorn --bind 0.0.0.0:\$PORT --workers 1 main:app" > Procfile
```

### Para PythonAnywhere:
- ✅ Todo listo, solo subir archivos
- Configurar WSGI apuntando a main.py

## 📤 PASOS PARA EXPORTAR Y DESPLEGAR

### 1. Exportar de Replit
```bash
# Opción A: Descarga directa (zip)
Replit → Files → ... → Download as zip

# Opción B: Git (si tienes repositorio conectado)
git pull origin main
```

### 2. Subir a GitHub (Recomendado)
```bash
# En tu computadora local:
git init
git add .
git commit -m "CharlyNet Crypto API - Red colaborativa 9 IAs"
git branch -M main
git remote add origin https://github.com/tu-usuario/charlynet-crypto.git
git push -u origin main
```

### 3. Desplegar en Railway
1. railway.app → Login with GitHub
2. "New Project" → "Deploy from GitHub repo"
3. Seleccionar repositorio
4. ✅ Railway detecta automáticamente Python/Flask
5. Agregar variables de entorno (mínimas):
   ```env
   FLASK_ENV=production
   SECRET_KEY=tu_clave_secreta_aqui
   ```
6. ✅ Deploy automático completo

## 🔐 VARIABLES DE ENTORNO NECESARIAS

### Mínimas (Para funcionamiento básico):
```env
FLASK_ENV=production
SECRET_KEY=genera_una_clave_secreta_fuerte_aqui
PORT=5000
```

### Opcionales (Para funcionalidades completas):
```env
# Reddit API (para análisis de sentimiento)
REDDIT_CLIENT_ID=tu_reddit_client_id
REDDIT_CLIENT_SECRET=tu_reddit_client_secret
REDDIT_USER_AGENT=CharlyNetCrypto/1.0

# Base de datos (se configura automáticamente en Railway)
DATABASE_URL=postgresql://usuario:password@host:port/database
```

## ⚠️ NOTAS IMPORTANTES

### 1. **APIs Externas**
- ✅ CoinGecko API: Funciona sin API key (tier gratuito)
- ✅ RSS Feeds: Funcionan sin configuración
- ⚠️ Reddit API: Requiere registro gratuito para funcionalidad completa
- ⚠️ CryptoPanic: Usando tier gratuito (limitado)

### 2. **Optimizaciones Ya Implementadas**
- ✅ Rate limiting en APIs
- ✅ Cache de datos para reducir llamadas
- ✅ Scheduler optimizado (60 min ciclos)
- ✅ Manejo eficiente de errores
- ✅ Sistema robusto de 9 IAs colaborativas

### 3. **Funcionalidades que Funcionan Sin Configuración**
- ✅ Precios en tiempo real (10 cryptos principales)
- ✅ Red colaborativa de 9 IAs especializadas
- ✅ Dashboard interactivo completo
- ✅ Sistema de alertas automáticas
- ✅ Análisis técnico, fundamental y on-chain
- ✅ Auto-scheduler con 6 trabajos programados
- ✅ API REST completa con documentación

### 4. **Tamaño del Proyecto**
- Código: ~50-60 archivos
- Tamaño total: ~15-20 MB
- ✅ Perfecto para servicios gratuitos

## 🎯 CHECKLIST DE DESPLIEGUE

### Antes de Exportar:
- [x] Código funcionando en Replit
- [x] Todas las dependencias en pyproject.toml
- [x] main.py como punto de entrada
- [x] Variables sensibles como variables de entorno

### Después de Exportar:
- [ ] Subir a GitHub
- [ ] Crear cuenta en Railway/Render
- [ ] Conectar repositorio
- [ ] Configurar variables de entorno
- [ ] Verificar despliegue exitoso
- [ ] Probar todas las funcionalidades

Tu proyecto está completamente listo para despliegue gratuito. La red colaborativa de 9 IAs y todas las funcionalidades avanzadas funcionarán perfectamente en cualquiera de estas plataformas.