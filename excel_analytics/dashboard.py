"""Generate an interactive HTML dashboard from analytics results."""

import json
import os


def generate_dashboard(analytics, output_path="output/dashboard.html"):
    """Build a self-contained HTML dashboard with Plotly charts."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    kpis = analytics.get("kpis", {})
    monthly = analytics.get("monthly_trend", {})
    by_region = analytics.get("by_region", {})
    by_category = analytics.get("by_category", {})
    by_product = analytics.get("by_product", {})
    heatmap = analytics.get("region_category_heatmap", {})
    tva = analytics.get("target_vs_actual", {})
    top_emp = analytics.get("top_employees", {})
    by_dept = analytics.get("by_department", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Excel Analytics Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; }}
  .header {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
             padding: 24px 32px; border-bottom: 2px solid #3b82f6; }}
  .header h1 {{ font-size: 1.6rem; font-weight: 600; }}
  .header p {{ color: #94a3b8; font-size: 0.9rem; margin-top: 4px; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .kpi-card {{ background: #1e293b; border-radius: 12px; padding: 20px;
               border: 1px solid #334155; text-align: center; }}
  .kpi-card .value {{ font-size: 1.8rem; font-weight: 700; color: #3b82f6; }}
  .kpi-card .label {{ font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }}
  .chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(580px, 1fr)); gap: 20px; }}
  .chart-card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .chart-card h3 {{ margin-bottom: 12px; font-size: 1rem; color: #cbd5e1; }}
  .chart {{ width: 100%; height: 350px; }}
  .table-wrap {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #334155; }}
  th {{ background: #334155; color: #94a3b8; font-weight: 600; }}
  tr:hover {{ background: #263045; }}
</style>
</head>
<body>
<div class="header">
  <h1>Excel Analytics Dashboard</h1>
  <p>Auto-generated from Excel data source</p>
</div>
<div class="container">

<!-- KPIs -->
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="value">${kpis.get('total_revenue', 0):,.0f}</div>
    <div class="label">Total Revenue</div>
  </div>
  <div class="kpi-card">
    <div class="value">${kpis.get('total_profit', 0):,.0f}</div>
    <div class="label">Total Profit</div>
  </div>
  <div class="kpi-card">
    <div class="value">{kpis.get('profit_margin', 0)}%</div>
    <div class="label">Profit Margin</div>
  </div>
  <div class="kpi-card">
    <div class="value">{kpis.get('total_units', 0):,}</div>
    <div class="label">Units Sold</div>
  </div>
  <div class="kpi-card">
    <div class="value">${kpis.get('avg_order_value', 0):,.0f}</div>
    <div class="label">Avg Order Value</div>
  </div>
  <div class="kpi-card">
    <div class="value">{kpis.get('total_transactions', 0):,}</div>
    <div class="label">Transactions</div>
  </div>
</div>

<div class="chart-grid">
  <!-- Monthly Revenue Trend -->
  <div class="chart-card">
    <h3>Monthly Revenue &amp; Profit Trend</h3>
    <div id="monthlyTrend" class="chart"></div>
  </div>

  <!-- Target vs Actual -->
  <div class="chart-card">
    <h3>Target vs Actual Revenue</h3>
    <div id="targetVsActual" class="chart"></div>
  </div>

  <!-- Revenue by Region -->
  <div class="chart-card">
    <h3>Revenue by Region</h3>
    <div id="byRegion" class="chart"></div>
  </div>

  <!-- Revenue by Category -->
  <div class="chart-card">
    <h3>Revenue by Category</h3>
    <div id="byCategory" class="chart"></div>
  </div>

  <!-- Top Products -->
  <div class="chart-card">
    <h3>Top Products by Revenue</h3>
    <div id="byProduct" class="chart"></div>
  </div>

  <!-- Region x Category Heatmap -->
  <div class="chart-card">
    <h3>Revenue Heatmap: Region x Category</h3>
    <div id="heatmap" class="chart"></div>
  </div>

  <!-- Department Performance -->
  <div class="chart-card">
    <h3>Department Performance</h3>
    <div id="byDept" class="chart"></div>
  </div>

  <!-- Top Employees Table -->
  <div class="chart-card">
    <h3>Top 10 Employees by Revenue</h3>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Employee</th><th>Region</th><th>Department</th><th>Deals</th><th>Revenue</th></tr></thead>
        <tbody id="empTable"></tbody>
      </table>
    </div>
  </div>
</div>
</div>

<script>
const layout = {{
  paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  font: {{ color: '#94a3b8' }}, margin: {{ l: 50, r: 20, t: 30, b: 50 }},
  xaxis: {{ gridcolor: '#334155' }}, yaxis: {{ gridcolor: '#334155' }},
}};

// Monthly Trend
Plotly.newPlot('monthlyTrend', [
  {{ x: {json.dumps(monthly.get('Month', []))}, y: {json.dumps(monthly.get('Revenue', []))},
     type: 'scatter', mode: 'lines+markers', name: 'Revenue',
     line: {{ color: '#3b82f6', width: 2 }} }},
  {{ x: {json.dumps(monthly.get('Month', []))}, y: {json.dumps(monthly.get('Profit', []))},
     type: 'scatter', mode: 'lines+markers', name: 'Profit',
     line: {{ color: '#10b981', width: 2 }} }},
], {{...layout}}, {{responsive: true}});

// Target vs Actual
Plotly.newPlot('targetVsActual', [
  {{ x: {json.dumps(tva.get('Month', []))}, y: {json.dumps(tva.get('Target_Revenue', []))},
     type: 'bar', name: 'Target', marker: {{ color: '#64748b' }} }},
  {{ x: {json.dumps(tva.get('Month', []))}, y: {json.dumps(tva.get('Revenue', []))},
     type: 'bar', name: 'Actual', marker: {{ color: '#3b82f6' }} }},
], {{...layout, barmode: 'group'}}, {{responsive: true}});

// By Region (pie)
Plotly.newPlot('byRegion', [{{
  labels: {json.dumps(by_region.get('Region', []))},
  values: {json.dumps(by_region.get('Revenue', []))},
  type: 'pie', hole: 0.4,
  marker: {{ colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'] }},
  textfont: {{ color: '#fff' }},
}}], {{...layout}}, {{responsive: true}});

// By Category
Plotly.newPlot('byCategory', [{{
  x: {json.dumps(by_category.get('Category', []))},
  y: {json.dumps(by_category.get('Revenue', []))},
  type: 'bar', marker: {{ color: ['#3b82f6', '#10b981', '#f59e0b'] }},
}}], {{...layout}}, {{responsive: true}});

// By Product
Plotly.newPlot('byProduct', [{{
  y: {json.dumps(by_product.get('Product', []))},
  x: {json.dumps(by_product.get('Revenue', []))},
  type: 'bar', orientation: 'h',
  marker: {{ color: '#3b82f6' }},
}}], {{...layout, yaxis: {{...layout.yaxis, autorange: 'reversed'}}}}, {{responsive: true}});

// Heatmap
Plotly.newPlot('heatmap', [{{
  z: {json.dumps(heatmap.get('values', []))},
  x: {json.dumps(heatmap.get('categories', []))},
  y: {json.dumps(heatmap.get('regions', []))},
  type: 'heatmap', colorscale: 'Blues',
}}], {{...layout}}, {{responsive: true}});

// By Department
Plotly.newPlot('byDept', [{{
  x: {json.dumps(by_dept.get('Department', []))},
  y: {json.dumps(by_dept.get('Total_Revenue', []))},
  type: 'bar', name: 'Revenue',
  marker: {{ color: '#3b82f6' }},
}}, {{
  x: {json.dumps(by_dept.get('Department', []))},
  y: {json.dumps(by_dept.get('Headcount', []))},
  type: 'scatter', mode: 'lines+markers', name: 'Headcount', yaxis: 'y2',
  line: {{ color: '#f59e0b', width: 2 }},
}}], {{...layout, yaxis2: {{ overlaying: 'y', side: 'right', gridcolor: '#334155', font: {{ color: '#94a3b8' }} }} }}, {{responsive: true}});

// Employee Table
const empData = {{
  Employee: {json.dumps(top_emp.get('Employee', []))},
  Region: {json.dumps(top_emp.get('Region', []))},
  Department: {json.dumps(top_emp.get('Department', []))},
  Deals_Closed: {json.dumps(top_emp.get('Deals_Closed', []))},
  Revenue_Generated: {json.dumps(top_emp.get('Revenue_Generated', []))},
}};
const tbody = document.getElementById('empTable');
for (let i = 0; i < empData.Employee.length; i++) {{
  const row = `<tr><td>${{empData.Employee[i]}}</td><td>${{empData.Region[i]}}</td>` +
    `<td>${{empData.Department[i]}}</td><td>${{empData.Deals_Closed[i]}}</td>` +
    `<td>${{empData.Revenue_Generated[i]?.toLocaleString('en-US', {{style:'currency',currency:'USD'}})}}</td></tr>`;
  tbody.innerHTML += row;
}}
</script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)

    print(f"Dashboard saved: {output_path}")
    return output_path
