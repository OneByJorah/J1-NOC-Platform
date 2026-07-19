#!/usr/bin/env python3
"""Capture NexusCore NOC dashboard screenshots using Playwright HTML mockups.

Usage:
    python scripts/capture-screenshots.py

Prerequisites:
    pip install playwright
    python -m playwright install chromium

Screenshots are saved to docs/screenshots/ for use in the README.
"""
from playwright.sync_api import sync_playwright
import time
import os

SCREENSHOT_DIR = os.environ.get("SCREENSHOT_DIR", "docs/screenshots")

NOC_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexusCore - NOC Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: #e2e8f0; height: 100vh; display: flex; }
        .sidebar { width: 260px; background: #1e293b; padding: 20px; border-right: 1px solid #334155; }
        .logo { font-size: 20px; font-weight: 700; color: #10b981; margin-bottom: 32px; }
        .logo span { color: #8b5cf6; }
        .nav-item { padding: 12px 16px; border-radius: 8px; margin-bottom: 4px; font-size: 14px; color: #94a3b8; }
        .nav-item.active { background: #10b981; color: white; }
        .main { flex: 1; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .header h1 { font-size: 24px; }
        .status-badge { background: #065f46; color: #10b981; padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
        .stat-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; }
        .stat-value { font-size: 28px; font-weight: 700; }
        .stat-value.green { color: #10b981; }
        .stat-value.yellow { color: #f59e0b; }
        .stat-value.red { color: #ef4444; }
        .stat-value.blue { color: #3b82f6; }
        .services-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
        .service-card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
        .service-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .service-name { font-weight: 600; }
        .service-status { width: 10px; height: 10px; border-radius: 50%; }
        .service-status.healthy { background: #10b981; }
        .service-status.warning { background: #f59e0b; }
        .service-metrics { font-size: 12px; color: #94a3b8; }
        .bar { height: 4px; background: #334155; border-radius: 2px; margin-top: 8px; }
        .bar-fill { height: 100%; border-radius: 2px; }
        .bar-fill.green { background: #10b981; }
        .bar-fill.yellow { background: #f59e0b; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">Nexus<span>Core</span></div>
        <div class="nav-item active">📊 Dashboard</div>
        <div class="nav-item">🖥️ Servers</div>
        <div class="nav-item">🌐 Network</div>
        <div class="nav-item">🤖 AI Insights</div>
        <div class="nav-item">📋 Logs</div>
    </div>
    <div class="main">
        <div class="header"><h1>NOC Dashboard</h1><span class="status-badge">✓ All Systems Operational</span></div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">Total Servers</div><div class="stat-value blue">24</div></div>
            <div class="stat-card"><div class="stat-label">Healthy</div><div class="stat-value green">22</div></div>
            <div class="stat-card"><div class="stat-label">Warnings</div><div class="stat-value yellow">2</div></div>
            <div class="stat-card"><div class="stat-label">Critical</div><div class="stat-value red">0</div></div>
        </div>
        <div class="services-grid">
            <div class="service-card"><div class="service-header"><span class="service-name">web-prod-01</span><div class="service-status healthy"></div></div><div class="service-metrics">CPU: 45% | RAM: 68%</div><div class="bar"><div class="bar-fill green" style="width: 45%"></div></div></div>
            <div class="service-card"><div class="service-header"><span class="service-name">db-primary</span><div class="service-status healthy"></div></div><div class="service-metrics">CPU: 32% | RAM: 78%</div><div class="bar"><div class="bar-fill green" style="width: 32%"></div></div></div>
            <div class="service-card"><div class="service-header"><span class="service-name">cache-redis</span><div class="service-status warning"></div></div><div class="service-metrics">CPU: 72% | RAM: 85%</div><div class="bar"><div class="bar-fill yellow" style="width: 72%"></div></div></div>
        </div>
    </div>
</body></html>
"""

SERVICE_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NexusCore - Service Monitor</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px; }
        h1 { font-size: 24px; margin-bottom: 24px; }
        .service-list { display: flex; flex-direction: column; gap: 12px; }
        .service-row { background: #1e293b; border-radius: 12px; padding: 16px 20px; display: flex; align-items: center; gap: 16px; border: 1px solid #334155; }
        .status-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
        .status-dot.green { background: #10b981; box-shadow: 0 0 8px #10b981; }
        .status-dot.yellow { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
        .service-info { flex: 1; }
        .service-name { font-weight: 600; margin-bottom: 4px; }
        .service-details { font-size: 12px; color: #94a3b8; }
        .service-metrics { display: flex; gap: 24px; font-size: 13px; }
        .metric { text-align: center; }
        .metric-value { font-weight: 600; }
        .metric-label { font-size: 11px; color: #64748b; }
        .uptime { color: #10b981; font-weight: 600; }
    </style>
</head>
<body>
    <h1>🖥️ Service Monitor</h1>
    <div class="service-list">
        <div class="service-row"><div class="status-dot green"></div><div class="service-info"><div class="service-name">Web Production Cluster</div><div class="service-details">3 instances • 10.0.1.10-12</div></div><div class="service-metrics"><div class="metric"><div class="metric-value">45%</div><div class="metric-label">CPU</div></div><div class="metric"><div class="metric-value">68%</div><div class="metric-label">RAM</div></div><div class="metric"><div class="uptime">99.98%</div><div class="metric-label">Uptime</div></div></div></div>
        <div class="service-row"><div class="status-dot green"></div><div class="service-info"><div class="service-name">PostgreSQL Primary</div><div class="service-details">db-prod-01 • 10.0.2.20</div></div><div class="service-metrics"><div class="metric"><div class="metric-value">32%</div><div class="metric-label">CPU</div></div><div class="metric"><div class="metric-value">78%</div><div class="metric-label">RAM</div></div><div class="metric"><div class="uptime">99.99%</div><div class="metric-label">Uptime</div></div></div></div>
        <div class="service-row"><div class="status-dot yellow"></div><div class="service-info"><div class="service-name">Redis Cache</div><div class="service-details">cache-prod-01 • 10.0.3.30</div></div><div class="service-metrics"><div class="metric"><div class="metric-value">72%</div><div class="metric-label">CPU</div></div><div class="metric"><div class="metric-value">85%</div><div class="metric-label">RAM</div></div><div class="metric"><div class="uptime" style="color: #f59e0b;">99.85%</div><div class="metric-label">Uptime</div></div></div></div>
    </div>
</body></html>
"""

AI_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NexusCore - AI Insights</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px; }
        h1 { font-size: 24px; margin-bottom: 8px; }
        .subtitle { color: #94a3b8; margin-bottom: 32px; }
        .insights-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .insight-card { background: #1e293b; border-radius: 12px; padding: 24px; border: 1px solid #334155; }
        .insight-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
        .insight-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .insight-icon.purple { background: #8b5cf620; }
        .insight-icon.green { background: #10b98120; }
        .insight-icon.yellow { background: #f59e0b20; }
        .insight-icon.blue { background: #3b82f620; }
        .insight-title { font-weight: 600; font-size: 16px; }
        .insight-desc { font-size: 13px; color: #94a3b8; line-height: 1.6; }
        .insight-action { margin-top: 16px; padding: 8px 16px; background: #8b5cf6; color: white; border: none; border-radius: 6px; font-size: 13px; }
    </style>
</head>
<body>
    <h1>🤖 AI Insights</h1>
    <p class="subtitle">Intelligent analysis and recommendations</p>
    <div class="insights-grid">
        <div class="insight-card"><div class="insight-header"><div class="insight-icon purple">🧠</div><div class="insight-title">Predictive Scaling</div></div><div class="insight-desc">Web-prod-01 will reach 85% CPU in 4 hours. Consider scaling up.</div><button class="insight-action">View Recommendations</button></div>
        <div class="insight-card"><div class="insight-header"><div class="insight-icon green">🔒</div><div class="insight-title">Security Anomaly</div></div><div class="insight-desc">Unusual SSH login attempts detected from 192.168.1.100.</div><button class="insight-action">Investigate</button></div>
        <div class="insight-card"><div class="insight-header"><div class="insight-icon yellow">📊</div><div class="insight-title">Cost Optimization</div></div><div class="insight-desc">Redis cache hit rate dropped. Increasing memory could save $127/mo.</div><button class="insight-action">Optimize</button></div>
        <div class="insight-card"><div class="insight-header"><div class="insight-icon blue">⚡</div><div class="insight-title">Performance Bottleneck</div></div><div class="insight-desc">Database connection pool exhaustion detected during peak hours.</div><button class="insight-action">Configure</button></div>
    </div>
</body></html>
"""

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for name, html in [("noc-dashboard.png", NOC_HTML), ("service-monitor.png", SERVICE_HTML), ("ai-insights.png", AI_HTML)]:
            print(f"Capturing {name}...")
            page.set_content(html)
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            path = os.path.join(SCREENSHOT_DIR, name)
            page.screenshot(path=path, full_page=False)
            print(f"Saved: {path} ({os.path.getsize(path):,} bytes)")
        
        browser.close()
    print("\nAll screenshots captured successfully!")

if __name__ == "__main__":
    capture_screenshots()
