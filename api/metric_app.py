from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from hypercorn.config import Config
import os
from cache.metrics import MetricsTracker
import json

# Initialize metrics tracker
metrics = MetricsTracker()

# Initialize FastAPI app
app = FastAPI(title="DropTracker Metrics")
config = Config()
config.bind = [f"0.0.0.0:{os.getenv('METRICS_PORT', '8000')}"]

@app.on_event("startup")
async def startup_event():
    """Initialize async components on FastAPI startup"""
    await metrics.initialize()

@app.get("/metrics")
async def get_metrics():
    """Get all system metrics"""
    return await metrics.get_all_metrics()

@app.get("/metrics/{metric_type}")
async def get_metric_type(metric_type: str):
    """Get metrics for a specific type"""
    return await metrics.get_metrics(metric_type)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Enhanced metrics dashboard with charts and better styling"""
    metrics_data = await metrics.get_all_metrics()
    
    # Format system metrics first
    sys_metrics = metrics_data['system']
    formatted_sys_metrics = {
        'memory_usage': f"{sys_metrics['memory']['rss']:.1f}",
        'cpu_usage': f"{sys_metrics['memory']['cpu_percent']:.1f}",
        'system_memory': f"{sys_metrics['system']['memory_percent']:.1f}",
        'uptime': sys_metrics['uptime']['formatted']
    }
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DropTracker Metrics</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {{
                --primary-color: #00ff00;
                --bg-color: #1a1a1a;
                --card-bg: #2d2d2d;
                --text-color: #ffffff;
            }}
            
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: var(--bg-color);
                color: var(--text-color);
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                color: var(--primary-color);
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .metric-card {{
                background-color: var(--card-bg);
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s;
                margin-bottom: 20px;
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px);
            }}
            
            .metric-card h2 {{
                color: var(--primary-color);
                margin-top: 0;
                border-bottom: 2px solid var(--primary-color);
                padding-bottom: 10px;
            }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .chart-container {{
                background-color: var(--card-bg);
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                height: 300px;
            }}
            
            .stat-value {{
                font-size: 1.8em;
                font-weight: bold;
                color: var(--primary-color);
                margin: 5px 0;
            }}
            
            .stat-label {{
                font-size: 0.9em;
                color: #888;
            }}
            
            .system-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }}
            
            .charts-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>DropTracker Metrics Dashboard</h1>
            <p>Real-time monitoring and statistics</p>
        </div>
        
        <!-- System Metrics Card -->
        <div class="metric-card">
            <h2>System Resources</h2>
            <div class="system-stats">
                <div>
                    <div class="stat-label">Memory Usage</div>
                    <div class="stat-value">{formatted_sys_metrics['memory_usage']}MB</div>
                </div>
                <div>
                    <div class="stat-label">CPU Usage</div>
                    <div class="stat-value">{formatted_sys_metrics['cpu_usage']}%</div>
                </div>
                <div>
                    <div class="stat-label">System Memory</div>
                    <div class="stat-value">{formatted_sys_metrics['system_memory']}%</div>
                </div>
                <div>
                    <div class="stat-label">Uptime</div>
                    <div class="stat-value" id="uptime">{formatted_sys_metrics['uptime']}</div>
                </div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid">
    """
    
    # Add chart containers for each metric type
    for metric_type in ['drops', 'logs', 'achievements', 'pbs']:
        html_content += f"""
            <div class="chart-container">
                <canvas id="{metric_type}Chart"></canvas>
            </div>
        """
    
    html_content += """
        </div>

        <!-- Metrics Cards Grid -->
        <div class="grid">
    """
    
    # Add metrics cards
    for metric_type in ['drops', 'logs', 'achievements', 'pbs']:
        data = metrics_data[metric_type]
        html_content += f"""
            <div class="metric-card">
                <h2>{metric_type.title()}</h2>
                <div class="stat-value">{data['total']['count']}</div>
                <div class="stat-label">Total Count</div>
                
                <h3>Last Hour</h3>
                <div class="stat-value">{data['rolling']['last_hour']['count']}</div>
                <div class="stat-label">{data['rolling']['last_hour']['avg_per_minute']:.2f}/min</div>
                
                <h3>Last Day</h3>
                <div class="stat-value">{data['rolling']['last_day']['count']}</div>
                <div class="stat-label">{data['rolling']['last_day']['avg_per_hour']:.2f}/hr</div>
            </div>
        """
    
    # Add JavaScript for charts and real-time updates
    html_content += """
        </div>
        <script>
            // Chart configuration factory
            function createChart(elementId, metricType, data) {
                const ctx = document.getElementById(elementId).getContext('2d');
                const now = new Date();
                const hourLabels = Array.from({length: 24}, (_, i) => {
                    const d = new Date(now - (23-i) * 3600000);
                    return `${d.getHours()}:00`;
                });
                
                return new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: hourLabels,
                        datasets: [{
                            label: metricType,
                            data: data,
                            borderColor: getColorForMetric(metricType),
                            backgroundColor: getColorForMetric(metricType) + '20',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: `24-Hour ${metricType} Activity`,
                                color: '#ffffff',
                                font: { size: 16 }
                            },
                            legend: {
                                labels: { color: '#ffffff' }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: '#333333' },
                                ticks: { 
                                    color: '#ffffff',
                                    precision: 0
                                }
                            },
                            x: {
                                grid: { color: '#333333' },
                                ticks: { color: '#ffffff' }
                            }
                        }
                    }
                });
            }

            function getColorForMetric(metricType) {
                const colors = {
                    'Drops': '#00ff00',
                    'Collection Logs': '#ff9900',
                    'Achievements': '#ff00ff',
                    'Personal Bests': '#00ffff'
                };
                return colors[metricType] || '#ffffff';
            }

            // Initialize charts with real data
            const metricsData = {
    """

    # Add real metrics data for each type
    for metric_type in ['drops', 'logs', 'achievements', 'pbs']:
        data = metrics_data[metric_type]['historical']['hourly']
        html_content += f"                '{metric_type.title()}': {json.dumps(data)},\n"

    html_content += """
            };

            // Create charts with real data
            Object.entries(metricsData).forEach(([metricType, data]) => {
                createChart(`${metricType.toLowerCase().replace(' ', '')}Chart`, metricType, data);
            });

            // Auto-refresh every 5 seconds
            setTimeout(() => location.reload(), 250);
        </script>
    </body>
    </html>
    """
    
    return html_content
