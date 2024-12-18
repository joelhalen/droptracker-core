from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from hypercorn.config import Config
import os
from cache.metrics import MetricsTracker

# Initialize metrics tracker
metrics = MetricsTracker()

# Initialize FastAPI app
app = FastAPI(title="DropTracker Metrics")
config = Config()
config.bind = [f"0.0.0.0:{os.getenv('METRICS_PORT', '8000')}"]

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
    """Simple metrics dashboard"""
    metrics_data = await metrics.get_all_metrics()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DropTracker Metrics</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .metric-card {
                border: 1px solid #ddd;
                padding: 15px;
                margin: 10px;
                border-radius: 5px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
        </style>
    </head>
    <body>
        <h1>DropTracker Metrics Dashboard</h1>
        <div class="grid">
    """
    
    for metric_type, data in metrics_data.items():
        html_content += f"""
            <div class="metric-card">
                <h2>{metric_type.title()}</h2>
                <p>Total Count: {data['total']['count']}</p>
                <p>Average per Hour: {data['total']['avg_per_hour']:.2f}</p>
                <h3>Last Hour</h3>
                <p>Count: {data['rolling']['last_hour']['count']}</p>
                <p>Avg per Minute: {data['rolling']['last_hour']['avg_per_minute']:.2f}</p>
                <h3>Last Day</h3>
                <p>Count: {data['rolling']['last_day']['count']}</p>
                <p>Avg per Hour: {data['rolling']['last_day']['avg_per_hour']:.2f}</p>
            </div>
        """
    
    html_content += """
        </div>
        <script>
            // Auto-refresh every .5 seconds
            setTimeout(() => location.reload(), 500);
        </script>
    </body>
    </html>
    """
    
    return html_content
