## No longer using this for the time being

# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse
# from hypercorn.config import Config
# import os
# from cache.metrics import MetricsTracker
# import json

# # Initialize metrics tracker
# metrics = MetricsTracker()

# # Initialize FastAPI app
# app = FastAPI(title="DropTracker Metrics")
# config = Config()
# config.bind = [f"0.0.0.0:{os.getenv('METRICS_PORT', '8000')}"]

# @app.on_event("startup")
# async def startup_event():
#     """Initialize async components on FastAPI startup"""
#     await metrics.initialize()

# @app.get("/metrics")
# async def get_metrics():
#     """Get all system metrics"""
#     return await metrics.get_all_metrics()

# @app.get("/metrics/{metric_type}")
# async def get_metric_type(metric_type: str):
#     """Get metrics for a specific type"""
#     return await metrics.get_metrics(metric_type)

# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard():
#     """Enhanced metrics dashboard with real-time updates and styling"""
#     html_content = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>DropTracker Metrics</title>
#         <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
#         <style>
#             :root {
#                 --primary-color: #00ff00;
#                 --bg-color: #1a1a1a;
#                 --card-bg: #2d2d2d;
#                 --text-color: #ffffff;
#                 --chart-grid: #3d3d3d;
#                 --hover-color: #3a3a3a;
#             }
            
#             body { 
#                 font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#                 margin: 0;
#                 padding: 20px;
#                 background-color: var(--bg-color);
#                 color: var(--text-color);
#                 line-height: 1.6;
#             }
            
#             .header {
#                 text-align: center;
#                 margin-bottom: 30px;
#                 padding: 20px;
#                 background-color: var(--card-bg);
#                 border-radius: 10px;
#                 box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
#             }
            
#             .header h1 {
#                 color: var(--primary-color);
#                 font-size: 2.5em;
#                 margin-bottom: 10px;
#                 text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
#             }
            
#             .header p {
#                 color: #888;
#                 font-size: 1.1em;
#             }
            
#             .metric-card {
#                 background-color: var(--card-bg);
#                 border-radius: 10px;
#                 padding: 20px;
#                 box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#                 transition: all 0.3s ease;
#                 margin-bottom: 20px;
#             }
            
#             .metric-card:hover {
#                 transform: translateY(-5px);
#                 box-shadow: 0 6px 12px rgba(0, 255, 0, 0.1);
#                 background-color: var(--hover-color);
#             }
            
#             .metric-card h2 {
#                 color: var(--primary-color);
#                 margin-top: 0;
#                 border-bottom: 2px solid var(--primary-color);
#                 padding-bottom: 10px;
#                 font-size: 1.8em;
#             }
            
#             .metric-card h3 {
#                 color: #888;
#                 margin: 15px 0 5px 0;
#                 font-size: 1.2em;
#             }
            
#             .grid {
#                 display: grid;
#                 grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
#                 gap: 20px;
#                 margin-bottom: 30px;
#             }
            
#             .chart-container {
#                 background-color: var(--card-bg);
#                 border-radius: 10px;
#                 padding: 20px;
#                 margin-bottom: 20px;
#                 height: 300px;
#                 box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#             }
            
#             .stat-value {
#                 font-size: 1.8em;
#                 font-weight: bold;
#                 color: var(--primary-color);
#                 margin: 5px 0;
#                 text-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
#             }
            
#             .stat-label {
#                 font-size: 0.9em;
#                 color: #888;
#             }
            
#             .system-stats {
#                 display: grid;
#                 grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
#                 gap: 15px;
#             }
            
#             .charts-grid {
#                 display: grid;
#                 grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
#                 gap: 20px;
#                 margin: 20px 0;
#             }
            
#             .loading {
#                 position: fixed;
#                 top: 10px;
#                 right: 10px;
#                 background-color: var(--primary-color);
#                 color: var(--bg-color);
#                 padding: 5px 10px;
#                 border-radius: 5px;
#                 opacity: 0;
#                 transition: opacity 0.3s ease;
#             }
            
#             .loading.active {
#                 opacity: 1;
#             }

#             @media (max-width: 768px) {
#                 .charts-grid {
#                     grid-template-columns: 1fr;
#                 }
                
#                 .system-stats {
#                     grid-template-columns: repeat(2, 1fr);
#                 }
#             }
#         </style>
#     </head>
#     <body>
#         <div class="loading" id="loading-indicator">Updating...</div>
        
#         <div class="header">
#             <h1>DropTracker Metrics Dashboard</h1>
#             <p>Real-time bot/app status and monitoring</p>
#         </div>
        
#         <div id="metrics-container" class="grid">
#             <!-- Metrics cards will be inserted here -->
#         </div>
        
#         <div class="charts-grid">
#             <div class="chart-container">
#                 <canvas id="hourlyChart"></canvas>
#             </div>
#             <div class="chart-container">
#                 <canvas id="dailyChart"></canvas>
#             </div>
#         </div>

#         <script>
#             let charts = {};
#             const chartColors = {
#                 drops: '#00ff00',
#                 logs: '#00ffff',
#                 achievements: '#ff00ff',
#                 pbs: '#ffff00'
#             };
            
#             // Initialize charts with styling
#             function initCharts() {
#                 Chart.defaults.color = '#888';
#                 Chart.defaults.borderColor = 'rgba(61, 61, 61, 0.5)';
                
#                 const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
#                 charts.hourly = new Chart(hourlyCtx, {
#                     type: 'line',
#                     data: {
#                         labels: Array.from({length: 24}, (_, i) => `${23-i}h ago`),
#                         datasets: ['drops', 'logs', 'achievements', 'pbs'].map(metric => ({
#                             label: metric.charAt(0).toUpperCase() + metric.slice(1),
#                             data: Array(24).fill(0),  // Initialize with zeros
#                             borderColor: chartColors[metric],
#                             backgroundColor: `${chartColors[metric]}33`,
#                             fill: true,
#                             tension: 0.4,
#                             borderWidth: 2
#                         }))
#                     },
#                     options: {
#                         responsive: true,
#                         maintainAspectRatio: false,
#                         animation: {
#                             duration: 750,
#                             easing: 'easeInOutQuart'
#                         },
#                         scales: {
#                             y: {
#                                 beginAtZero: true,
#                                 grid: {
#                                     color: 'rgba(61, 61, 61, 0.5)'
#                                 }
#                             },
#                             x: {
#                                 grid: {
#                                     color: 'rgba(61, 61, 61, 0.5)'
#                                 }
#                             }
#                         },
#                         plugins: {
#                             legend: {
#                                 position: 'top',
#                                 labels: {
#                                     color: '#888',
#                                     font: {
#                                         family: "'Segoe UI', sans-serif"
#                                     }
#                                 }
#                             },
#                             title: {
#                                 display: true,
#                                 text: 'Hourly Activity',
#                                 color: '#00ff00',
#                                 font: {
#                                     size: 16,
#                                     family: "'Segoe UI', sans-serif"
#                                 }
#                             }
#                         }
#                     }
#                 });
#             }

#             // Update metrics display with animations
#             function updateMetrics(data) {
#                 const container = document.getElementById('metrics-container');
#                 let html = '';
                
#                 // System metrics card
#                 html += `
#                     <div class="metric-card">
#                         <h2>System Resources</h2>
#                         <div class="system-stats">
#                             <div>
#                                 <div class="stat-label">Memory Usage</div>
#                                 <div class="stat-value">${data.system.memory.rss.toFixed(1)}MB</div>
#                             </div>
#                             <div>
#                                 <div class="stat-label">CPU Usage</div>
#                                 <div class="stat-value">${data.system.memory.cpu_percent.toFixed(1)}%</div>
#                             </div>
#                             <div>
#                                 <div class="stat-label">System Memory</div>
#                                 <div class="stat-value">${data.system.system.memory_percent.toFixed(1)}%</div>
#                             </div>
#                             <div>
#                                 <div class="stat-label">Uptime</div>
#                                 <div class="stat-value">${data.system.uptime.formatted}</div>
#                             </div>
#                         </div>
#                     </div>
#                 `;
                
#                 // Metrics cards
#                 ['drops', 'logs', 'achievements', 'pbs'].forEach(metric => {
#                     const metricData = data[metric];
#                     html += `
#                         <div class="metric-card">
#                             <h2>${metric.charAt(0).toUpperCase() + metric.slice(1)}</h2>
#                             <div class="stat-value">${metricData.total.count}</div>
#                             <div class="stat-label">Total Count</div>
                            
#                             <h3>Last Hour</h3>
#                             <div class="stat-value">${metricData.rolling.last_hour.count}</div>
#                             <div class="stat-label">${metricData.rolling.last_hour.avg_per_minute.toFixed(2)}/min</div>
                            
#                             <h3>Last Day</h3>
#                             <div class="stat-value">${metricData.rolling.last_day.count}</div>
#                             <div class="stat-label">${metricData.rolling.last_day.avg_per_hour.toFixed(2)}/hr</div>
#                         </div>
#                     `;
#                 });
                
#                 container.innerHTML = html;
#             }

#             // Update charts with smooth transitions
#             function updateCharts(data) {
#                 const metrics = ['drops', 'logs', 'achievements', 'pbs'];
#                 metrics.forEach((metric, index) => {
#                     const newData = data[metric].historical.hourly;
#                     charts.hourly.data.datasets[index].data = newData;
#                 });
                
#                 charts.hourly.update('none');  // Update without animation for smoother transitions
#             }

#             // Fetch new data with loading indicator
#             async function fetchMetrics() {
#                 const loadingIndicator = document.getElementById('loading-indicator');
#                 loadingIndicator.classList.add('active');
                
#                 try {
#                     const response = await fetch('/api/metrics');
#                     const data = await response.json();
#                     updateMetrics(data);
#                     updateCharts(data);
#                 } catch (error) {
#                     console.error('Error fetching metrics:', error);
#                 } finally {
#                     loadingIndicator.classList.remove('active');
#                 }
#             }

#             // Initialize and start updates
#             document.addEventListener('DOMContentLoaded', () => {
#                 initCharts();
#                 fetchMetrics(); // Initial fetch
#                 setInterval(fetchMetrics, 1000); // Update every 1 second
#             });
#         </script>
#     </body>
#     </html>
#     """
    
#     return html_content

# @app.get("/api/metrics")
# async def get_metrics():
#     """API endpoint for fetching metrics data"""
#     return await metrics.get_all_metrics()
