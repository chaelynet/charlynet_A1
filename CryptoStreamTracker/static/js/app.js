class CryptoApp {
    constructor() {
        this.cryptoData = {};
        this.chart = null;
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadCryptoPrices();
        });

        // Dashboard control buttons
        document.getElementById('analysisBtn').addEventListener('click', () => {
            this.loadCryptoAnalysis();
        });

        document.getElementById('alertsBtn').addEventListener('click', () => {
            this.loadAlerts();
        });

        document.getElementById('voiceToggleBtn').addEventListener('click', () => {
            this.toggleVoice();
        });

        document.getElementById('externalBtn').addEventListener('click', () => {
            this.loadExternalSources();
        });

        document.getElementById('forceAnalysisBtn').addEventListener('click', () => {
            this.forceAnalysis();
        });

        document.getElementById('schedulerStatusBtn').addEventListener('click', () => {
            this.loadSchedulerStatus();
        });

        document.getElementById('aiNetworkBtn').addEventListener('click', () => {
            this.executeCollaborativeAnalysis();
        });

        document.getElementById('speakAnalysisBtn').addEventListener('click', () => {
            this.speakCurrentAnalysis();
        });

        document.getElementById('speakNetworkBtn').addEventListener('click', () => {
            this.speakNetworkAnalysis();
        });

        // Chart controls
        document.getElementById('chartCrypto').addEventListener('change', () => {
            this.updateChart();
        });

        document.getElementById('chartDays').addEventListener('change', () => {
            this.updateChart();
        });
    }

    async loadInitialData() {
        await this.loadSupportedCryptos();
        await this.loadCryptoPrices();
    }

    getApiUrl(endpoint) {
        // Use the current window location to build API URLs
        const baseUrl = window.location.origin;
        return `${baseUrl}${endpoint}`;
    }

    async loadSupportedCryptos() {
        try {
            const response = await fetch(this.getApiUrl('/api/crypto/supported'));
            const data = await response.json();
            
            if (data.success) {
                this.populateChartSelector(data.data);
            }
        } catch (error) {
            console.error('Error loading supported cryptos:', error);
        }
    }

    populateChartSelector(cryptos) {
        const selector = document.getElementById('chartCrypto');
        selector.innerHTML = '<option value="">Select Cryptocurrency</option>';
        
        cryptos.forEach(crypto => {
            const option = document.createElement('option');
            option.value = crypto.symbol;
            option.textContent = `${crypto.name} (${crypto.symbol.toUpperCase()})`;
            selector.appendChild(option);
        });
    }

    async loadCryptoPrices() {
        this.showLoading(true);
        this.hideError();

        try {
            const response = await fetch(this.getApiUrl('/api/crypto/prices'));
            const data = await response.json();

            if (data.success) {
                this.cryptoData = data.data;
                this.updateLastUpdateTime(data.timestamp);
                this.renderCryptoCards();
            } else {
                this.showError(data.message || 'Failed to load cryptocurrency data');
            }
        } catch (error) {
            console.error('Error loading crypto prices:', error);
            this.showError('Unable to connect to the API. Please check your connection and try again.');
        } finally {
            this.showLoading(false);
        }
    }

    renderCryptoCards() {
        const container = document.getElementById('cryptoCards');
        container.innerHTML = '';

        Object.values(this.cryptoData).forEach(crypto => {
            const card = this.createCryptoCard(crypto);
            container.appendChild(card);
        });
    }

    createCryptoCard(crypto) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 mb-4';

        const priceChange = crypto.price_change_24h || 0;
        const priceChangeClass = priceChange >= 0 ? 'text-success' : 'text-danger';
        const priceChangeIcon = priceChange >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';

        col.innerHTML = `
            <div class="card h-100 crypto-card" data-symbol="${crypto.symbol}">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-8">
                            <h6 class="card-title mb-1">${crypto.name}</h6>
                            <small class="text-muted">${crypto.symbol.toUpperCase()}</small>
                        </div>
                        <div class="col-4 text-end">
                            <div class="crypto-icon">
                                <i class="fas fa-coins"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <div class="h4 mb-1">$${this.formatPrice(crypto.current_price)}</div>
                        <div class="small ${priceChangeClass}">
                            <i class="fas ${priceChangeIcon} me-1"></i>
                            ${this.formatPercentage(priceChange)}%
                        </div>
                    </div>
                    
                    <div class="row mt-3 small text-muted">
                        <div class="col-6">
                            <div>Market Cap</div>
                            <div class="fw-bold">$${this.formatLargeNumber(crypto.market_cap)}</div>
                        </div>
                        <div class="col-6">
                            <div>Volume 24h</div>
                            <div class="fw-bold">$${this.formatLargeNumber(crypto.volume_24h)}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add click event for chart selection
        col.querySelector('.crypto-card').addEventListener('click', () => {
            document.getElementById('chartCrypto').value = crypto.symbol;
            this.updateChart();
        });

        return col;
    }

    async updateChart() {
        const symbol = document.getElementById('chartCrypto').value;
        const days = document.getElementById('chartDays').value;

        if (!symbol) {
            this.showChartMessage('Select a cryptocurrency to view price history');
            this.destroyChart();
            return;
        }

        this.hideChartMessage();

        try {
            const response = await fetch(this.getApiUrl(`/api/crypto/history/${symbol}?days=${days}`));
            const data = await response.json();

            if (data.success) {
                this.renderChart(data.data, data.symbol, days);
            } else {
                this.showChartMessage(data.message || 'Failed to load price history');
                this.destroyChart();
            }
        } catch (error) {
            console.error('Error loading price history:', error);
            this.showChartMessage('Failed to load price history');
            this.destroyChart();
        }
    }

    renderChart(historyData, symbol, days) {
        const ctx = document.getElementById('priceChart');
        
        this.destroyChart();

        const labels = historyData.map(point => {
            const date = new Date(point.timestamp);
            return days === '1' ? date.toLocaleTimeString() : date.toLocaleDateString();
        });

        const prices = historyData.map(point => point.price);

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `${symbol} Price (USD)`,
                    data: prices,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    },
                    x: {
                        ticks: {
                            maxTicksLimit: 8
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${symbol}: $${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                }
            }
        });
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    showChartMessage(message) {
        const messageDiv = document.getElementById('chartMessage');
        messageDiv.querySelector('p').textContent = message;
        messageDiv.classList.remove('d-none');
    }

    hideChartMessage() {
        document.getElementById('chartMessage').classList.add('d-none');
    }

    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        const cards = document.getElementById('cryptoCards');
        
        if (show) {
            spinner.classList.remove('d-none');
            cards.style.opacity = '0.5';
        } else {
            spinner.classList.add('d-none');
            cards.style.opacity = '1';
        }
    }

    showError(message) {
        const alert = document.getElementById('errorAlert');
        const messageElement = document.getElementById('errorMessage');
        
        messageElement.textContent = message;
        alert.classList.remove('d-none');
    }

    hideError() {
        document.getElementById('errorAlert').classList.add('d-none');
    }

    updateLastUpdateTime(timestamp) {
        if (timestamp) {
            const date = new Date(timestamp);
            const timeString = date.toLocaleString();
            document.getElementById('lastUpdate').textContent = timeString;
        }
    }

    formatPrice(price) {
        if (price >= 1) {
            return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        } else {
            return price.toFixed(8);
        }
    }

    formatPercentage(change) {
        return Math.abs(change).toFixed(2);
    }

    formatLargeNumber(num) {
        if (!num) return '0';
        
        if (num >= 1e12) {
            return (num / 1e12).toFixed(2) + 'T';
        } else if (num >= 1e9) {
            return (num / 1e9).toFixed(2) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(2) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(2) + 'K';
        }
        return num.toLocaleString();
    }

    startAutoRefresh() {
        // Refresh every 2 minutes
        this.refreshInterval = setInterval(() => {
            this.loadCryptoPrices();
        }, 120000);
    }

    async loadCryptoAnalysis() {
        this.showContent('analysis', 'Análisis IA', 'Generando análisis inteligente...');
        
        try {
            const response = await fetch(this.getApiUrl('/api/crypto/analysis'));
            const data = await response.json();

            if (data.success) {
                const content = document.getElementById('analysisContent');
                content.querySelector('pre').textContent = data.analysis;
                this.displayContent('analysisContent', 'Análisis Inteligente', 'Análisis generado con IA');
            } else {
                this.showError(data.message || 'Failed to generate analysis');
            }
        } catch (error) {
            console.error('Error loading crypto analysis:', error);
            this.showError('Unable to load crypto analysis');
        }
    }

    async loadAlerts() {
        this.showContent('alerts', 'Alertas Activas', 'Cargando alertas del sistema...');
        
        try {
            const response = await fetch(this.getApiUrl('/api/alerts'));
            const data = await response.json();

            if (data.success) {
                const content = document.getElementById('alertsContent');
                const display = content.querySelector('.alerts-display');
                
                display.innerHTML = `
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <div class="card border-warning">
                                <div class="card-body text-center">
                                    <h3 class="text-warning">${data.active_alerts}</h3>
                                    <small>Alertas Activas</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card border-danger">
                                <div class="card-body text-center">
                                    <h3 class="text-danger">${data.critical_alerts}</h3>
                                    <small>Alertas Críticas</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card border-info">
                                <div class="card-body text-center">
                                    <h3 class="text-info">${new Date().toLocaleTimeString()}</h3>
                                    <small>Última Actualización</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <pre class="bg-dark text-light p-3 rounded" style="white-space: pre-wrap;">${data.summary}</pre>
                `;
                
                this.displayContent('alertsContent', 'Sistema de Alertas', `${data.active_alerts} alertas activas`);
            } else {
                this.showError(data.message || 'Failed to load alerts');
            }
        } catch (error) {
            console.error('Error loading alerts:', error);
            this.showError('Unable to load alerts');
        }
    }

    async loadExternalSources() {
        this.showContent('external', 'Fuentes Externas', 'Analizando Reddit y CryptoPanic...');
        
        try {
            const response = await fetch(this.getApiUrl('/api/external-sources'));
            const data = await response.json();

            if (data.success) {
                const content = document.getElementById('externalContent');
                content.querySelector('pre').textContent = data.sentiment_analysis;
                this.displayContent('externalContent', 'Análisis de Fuentes Externas', 'Reddit + CryptoPanic + RSS');
            } else {
                this.showError(data.message || 'Failed to load external sources');
            }
        } catch (error) {
            console.error('Error loading external sources:', error);
            this.showError('Unable to load external sources');
        }
    }

    async toggleVoice() {
        try {
            const response = await fetch(this.getApiUrl('/api/voice/toggle'), { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                const statusElement = document.getElementById('voiceStatus');
                const btnElement = document.getElementById('voiceToggleBtn');
                
                if (data.voice_enabled) {
                    statusElement.textContent = 'Desactivar Voz';
                    btnElement.className = 'btn btn-success w-100 mb-2';
                } else {
                    statusElement.textContent = 'Activar Voz';
                    btnElement.className = 'btn btn-outline-success w-100 mb-2';
                }
                
                // Test voice if enabled
                if (data.voice_enabled) {
                    this.speakText('Sistema de voz activado correctamente');
                }
            }
        } catch (error) {
            console.error('Error toggling voice:', error);
            this.showError('Unable to toggle voice system');
        }
    }

    async forceAnalysis() {
        this.showContent('status', 'Análisis Forzado', 'Ejecutando análisis completo del sistema...');
        
        try {
            const response = await fetch(this.getApiUrl('/api/scheduler/force-analysis'), { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                // Reload analysis after forcing
                setTimeout(() => {
                    this.loadCryptoAnalysis();
                }, 2000);
                
                this.speakText('Análisis completo ejecutado correctamente');
            } else {
                this.showError(data.message || 'Failed to force analysis');
            }
        } catch (error) {
            console.error('Error forcing analysis:', error);
            this.showError('Unable to force analysis');
        }
    }

    async loadSchedulerStatus() {
        this.showContent('status', 'Estado del Sistema', 'Verificando estado del sistema...');
        
        try {
            const response = await fetch(this.getApiUrl('/api/scheduler/status'));
            const data = await response.json();

            if (data.success) {
                const content = document.getElementById('statusContent');
                const display = content.querySelector('.status-display');
                const status = data.scheduler_status;
                const voice = data.voice_status;
                
                display.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6><i class="fas fa-cogs me-2"></i>Auto-Scheduler</h6>
                            <ul class="list-unstyled">
                                <li><strong>Estado:</strong> <span class="badge ${status.running ? 'bg-success' : 'bg-danger'}">${status.running ? 'Activo' : 'Inactivo'}</span></li>
                                <li><strong>Trabajos:</strong> ${status.jobs_count}</li>
                                <li><strong>Análisis 24h:</strong> ${status.analysis_count_24h}</li>
                                <li><strong>Último análisis:</strong> ${status.last_analysis_time ? new Date(status.last_analysis_time).toLocaleString() : 'Nunca'}</li>
                                <li><strong>Próximo análisis:</strong> ${status.next_analysis ? new Date(status.next_analysis).toLocaleString() : 'N/A'}</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-volume-up me-2"></i>Sistema de Voz</h6>
                            <ul class="list-unstyled">
                                <li><strong>Estado:</strong> <span class="badge ${voice.enabled ? 'bg-success' : 'bg-secondary'}">${voice.enabled ? 'Habilitado' : 'Deshabilitado'}</span></li>
                                <li><strong>Motor:</strong> ${voice.engine_available ? voice.engine_type : 'No disponible'}</li>
                                <li><strong>Idioma:</strong> ${voice.language}</li>
                            </ul>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-12">
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                <strong>Loop Automático:</strong> El sistema ejecuta análisis completos cada 60 minutos y verifica alertas cada 5 minutos.
                            </div>
                        </div>
                    </div>
                `;
                
                this.displayContent('statusContent', 'Estado del Sistema', 'Sistema de monitoreo automático');
            } else {
                this.showError(data.message || 'Failed to get scheduler status');
            }
        } catch (error) {
            console.error('Error loading scheduler status:', error);
            this.showError('Unable to load scheduler status');
        }
    }

    async speakCurrentAnalysis() {
        const content = document.getElementById('analysisContent');
        const pre = content.querySelector('pre');
        
        if (pre && pre.textContent) {
            await this.speakText(pre.textContent);
        }
    }

    async speakText(text) {
        try {
            const response = await fetch(this.getApiUrl('/api/voice/speak'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            const data = await response.json();
            if (!data.success) {
                console.warn('Voice synthesis failed:', data.message);
            }
        } catch (error) {
            console.error('Error with voice synthesis:', error);
        }
    }

    async executeCollaborativeAnalysis() {
        this.showContent('ai-network', 'Red IA Expandida', 'Ejecutando análisis con 9 IAs especializadas...');
        
        try {
            const response = await fetch(this.getApiUrl('/api/ai-network/collaborative-analysis'), { 
                method: 'POST' 
            });
            const data = await response.json();

            if (data.success) {
                const content = document.getElementById('aiNetworkContent');
                content.querySelector('pre').textContent = data.collaborative_analysis;
                this.displayContent('aiNetworkContent', 'Red IA Expandida', '9 IAs especializadas consultadas');
                
                // Auto-reproducir resumen por voz si está habilitado
                setTimeout(() => {
                    this.speakText('Análisis colaborativo expandido completado. Nueve IAs especializadas han analizado el mercado.');
                }, 1000);
            } else {
                this.showError(data.message || 'Failed to execute collaborative analysis');
            }
        } catch (error) {
            console.error('Error executing collaborative analysis:', error);
            this.showError('Unable to execute collaborative analysis');
        }
    }

    async speakNetworkAnalysis() {
        const content = document.getElementById('aiNetworkContent');
        const pre = content.querySelector('pre');
        
        if (pre && pre.textContent) {
            // Extraer solo el resumen ejecutivo para voz
            const lines = pre.textContent.split('\n');
            const summaryStart = lines.findIndex(line => line.includes('RESUMEN EJECUTIVO'));
            const recommendationStart = lines.findIndex(line => line.includes('RECOMENDACIÓN FINAL'));
            
            if (summaryStart !== -1 && recommendationStart !== -1) {
                const summaryLines = lines.slice(summaryStart, recommendationStart + 3);
                const summary = summaryLines.join(' ').replace(/[=\-]/g, '');
                await this.speakText(summary);
            } else {
                await this.speakText('Análisis colaborativo completado con éxito por la red de IAs especializadas');
            }
        }
    }

    showContent(type, title, loadingMessage) {
        // Hide all content sections
        document.getElementById('defaultContent').classList.add('d-none');
        document.getElementById('analysisContent').classList.add('d-none');
        document.getElementById('alertsContent').classList.add('d-none');
        document.getElementById('externalContent').classList.add('d-none');
        document.getElementById('statusContent').classList.add('d-none');
        document.getElementById('aiNetworkContent').classList.add('d-none');
        
        // Show loading
        const loading = document.getElementById('contentLoading');
        const loadingMsg = document.getElementById('loadingMessage');
        loading.classList.remove('d-none');
        loadingMsg.textContent = loadingMessage;
        
        // Update title
        document.getElementById('contentTitle').innerHTML = `<i class="fas fa-sync-alt fa-spin me-2"></i>${title}`;
    }

    displayContent(contentId, title, subtitle) {
        // Hide loading
        document.getElementById('contentLoading').classList.add('d-none');
        
        // Show content
        document.getElementById(contentId).classList.remove('d-none');
        
        // Update title
        const iconMap = {
            'analysisContent': 'fa-robot',
            'alertsContent': 'fa-bell',
            'externalContent': 'fa-globe',
            'statusContent': 'fa-cogs',
            'aiNetworkContent': 'fa-network-wired'
        };
        
        const icon = iconMap[contentId] || 'fa-chart-line';
        document.getElementById('contentTitle').innerHTML = `<i class="fas ${icon} me-2"></i>${title}`;
        document.getElementById('contentSubtitle').textContent = subtitle;
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new CryptoApp();
});

// Clean up when page unloads
window.addEventListener('beforeunload', () => {
    if (window.cryptoApp) {
        window.cryptoApp.stopAutoRefresh();
    }
});
