"""FP&A Analytics Dashboard - Streamlit App

Run with: streamlit run app.py
"""

import hmac
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from excel_analytics.analyzer import load_excel, summarize_dataframe, compute_fpa_analytics
from generate_sample_data import generate_fpa_data


st.set_page_config(
    page_title="FP&A Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = (".xlsx", ".xls")


# ── Authentication ────────────────────────────────────────────────────────────

def check_password():
    """Gate the app behind a password. Configure in .streamlit/secrets.toml."""
    if "password" not in st.secrets:
        return True

    if st.session_state.get("authenticated"):
        return True

    st.title("FP&A Analytics Dashboard")
    st.markdown("---")

    with st.form("login_form"):
        password = st.text_input("Password", type="password", placeholder="Enter access password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        if hmac.compare_digest(password, st.secrets["password"]):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    st.caption("Contact your admin for access credentials.")
    return False


if not check_password():
    st.stop()


# ── File Validation ───────────────────────────────────────────────────────────

def validate_and_load(uploaded_file):
    """Validate uploaded file and return sheets dict, or None on error."""
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.sidebar.error(f"File too large. Maximum size is {MAX_FILE_SIZE_MB} MB.")
        return None

    name = uploaded_file.name.lower()
    if not name.endswith(ALLOWED_EXTENSIONS):
        st.sidebar.error("Invalid file type. Please upload .xlsx or .xls files only.")
        return None

    try:
        sheets = load_excel(uploaded_file)
    except Exception as e:
        st.sidebar.error(f"Failed to read Excel file: {e}")
        return None

    if not sheets:
        st.sidebar.error("The uploaded file contains no sheets.")
        return None

    total_rows = sum(len(df) for df in sheets.values())
    if total_rows == 0:
        st.sidebar.warning("All sheets are empty.")
        return None

    return sheets


# ── Sidebar: Data Source ──────────────────────────────────────────────────────

st.sidebar.title("Data Source")
data_source = st.sidebar.radio("Choose data source:", ["Upload Excel File", "Use Sample Data"])

sheets = None

if data_source == "Upload Excel File":
    uploaded = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
    if uploaded:
        sheets = validate_and_load(uploaded)
        if sheets:
            st.sidebar.success(f"Loaded {len(sheets)} sheet(s)")
            for name, df in sheets.items():
                st.sidebar.caption(f"  {name}: {len(df)} rows x {len(df.columns)} cols")
else:
    if st.sidebar.button("Generate Sample FP&A Data"):
        st.session_state["sample_generated"] = True

    if st.session_state.get("sample_generated"):
        filepath = generate_fpa_data()
        sheets = load_excel(filepath)
        st.sidebar.success(f"Loaded sample data ({len(sheets)} sheets)")

if sheets is None:
    st.title("FP&A Analytics Dashboard")
    st.info("Upload an Excel file or generate sample data from the sidebar to get started.")
    st.markdown("""
### Expected Excel Sheets

| Sheet Name | Description |
|---|---|
| **PnL** | Income statement with Account, Category, Type, and monthly columns |
| **Budget_vs_Actual** | Department, Month, Budget, Actual, Forecast |
| **CashFlow** | Monthly cash flow with Operating, Investing, Financing |
| **Headcount** | Department, Month, Headcount, Avg_Salary, Total_Comp, Open_Positions |
| **KPIs** | KPI, Month, Target, Actual, Unit |

You don't need all sheets - the dashboard adapts to whatever is available.
""")
    st.stop()

# ── Compute Analytics ─────────────────────────────────────────────────────────

try:
    analytics = compute_fpa_analytics(sheets)
except Exception as e:
    st.error(f"Analytics computation failed: {e}")
    st.info("Check that your Excel sheets match the expected column format above.")
    st.stop()

if not analytics:
    st.warning("No recognized FP&A sheets found. The dashboard expects sheets named: PnL, Budget_vs_Actual, CashFlow, Headcount, KPIs.")
    st.stop()

# ── Sidebar: Navigation ──────────────────────────────────────────────────────

available_pages = []
if "pnl" in analytics:
    available_pages.append("P&L / Income Statement")
if "budget" in analytics:
    available_pages.append("Budget vs Actuals")
if "cashflow" in analytics:
    available_pages.append("Cash Flow")
if "headcount" in analytics:
    available_pages.append("Headcount & Workforce")
if "kpis" in analytics:
    available_pages.append("KPI Scorecard")
available_pages.append("Raw Data Explorer")

st.sidebar.markdown("---")
page = st.sidebar.radio("Dashboard View", available_pages)

# ── Color Palette ─────────────────────────────────────────────────────────────

COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"]


# ══════════════════════════════════════════════════════════════════════════════
# P&L / Income Statement
# ══════════════════════════════════════════════════════════════════════════════

if page == "P&L / Income Statement":
    pnl = analytics["pnl"]

    st.title("P&L / Income Statement")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${pnl['total_revenue']:,.0f}")
    c2.metric("Total Expenses", f"${pnl['total_expenses']:,.0f}")
    c3.metric("Net Income", f"${pnl['total_net_income']:,.0f}")
    avg_net_margin = round(sum(pnl["net_margin"]) / len(pnl["net_margin"]), 1)
    c4.metric("Avg Net Margin", f"{avg_net_margin}%")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pnl["months"], y=pnl["revenue"],
            name="Revenue", line=dict(color="#10b981", width=3),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.1)",
        ))
        fig.add_trace(go.Scatter(
            x=pnl["months"], y=pnl["expenses"],
            name="Expenses", line=dict(color="#ef4444", width=3),
            fill="tozeroy", fillcolor="rgba(239,68,68,0.1)",
        ))
        fig.add_trace(go.Scatter(
            x=pnl["months"], y=pnl["net_income"],
            name="Net Income", line=dict(color="#3b82f6", width=2, dash="dash"),
        ))
        fig.update_layout(title="Revenue vs Expenses vs Net Income", height=400, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pnl["months"], y=pnl["gross_margin"],
            name="Gross Margin %", line=dict(color="#10b981", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=pnl["months"], y=pnl["operating_margin"],
            name="Operating Margin %", line=dict(color="#f59e0b", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=pnl["months"], y=pnl["net_margin"],
            name="Net Margin %", line=dict(color="#3b82f6", width=2),
        ))
        fig.update_layout(title="Margin Trends (%)", height=400, template="plotly_dark",
                          yaxis=dict(title="Margin %"))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Expense Breakdown by Category")
    cat_totals = pnl["category_totals"]
    fig = px.pie(
        names=list(cat_totals.keys()),
        values=list(cat_totals.values()),
        color_discrete_sequence=COLORS,
        hole=0.4,
    )
    fig.update_layout(height=400, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Detailed P&L Line Items"):
        pnl_df = pd.DataFrame(pnl["line_items"])
        st.dataframe(pnl_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# Budget vs Actuals
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Budget vs Actuals":
    budget = analytics["budget"]

    st.title("Budget vs Actuals")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Budget", f"${budget['total_budget']:,.0f}")
    c2.metric("Total Actual", f"${budget['total_actual']:,.0f}")
    variance = budget["total_variance"]
    c3.metric("Total Variance", f"${variance:,.0f}",
              delta=f"{'Over' if variance > 0 else 'Under'} budget")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        bm = budget["by_month"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=bm["Month"], y=bm["Budget"], name="Budget",
                             marker_color="#64748b"))
        fig.add_trace(go.Bar(x=bm["Month"], y=bm["Actual"], name="Actual",
                             marker_color="#3b82f6"))
        fig.add_trace(go.Scatter(x=bm["Month"], y=bm["Forecast"], name="Forecast",
                                 line=dict(color="#f59e0b", width=2, dash="dot")))
        fig.update_layout(title="Monthly: Budget vs Actual vs Forecast",
                          barmode="group", height=400, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        colors = ["#10b981" if v < 0 else "#ef4444" for v in bm["Variance"]]
        fig.add_trace(go.Bar(x=bm["Month"], y=bm["Variance"],
                             marker_color=colors, name="Variance"))
        fig.update_layout(title="Monthly Variance (Actual - Budget)",
                          height=400, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Department Budget Performance")
    bd = budget["by_department"]
    dept_df = pd.DataFrame(bd)

    fig = go.Figure()
    fig.add_trace(go.Bar(y=dept_df["Department"], x=dept_df["Total_Budget"],
                         name="Budget", orientation="h", marker_color="#64748b"))
    fig.add_trace(go.Bar(y=dept_df["Department"], x=dept_df["Total_Actual"],
                         name="Actual", orientation="h", marker_color="#3b82f6"))
    fig.update_layout(title="Budget vs Actual by Department", barmode="group",
                      height=400, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Variance Details")
    dept_df["Variance_Display"] = dept_df["Variance"].apply(lambda x: f"${x:,.0f}")
    dept_df["Variance_%_Display"] = dept_df["Variance_%"].apply(lambda x: f"{x:+.1f}%")
    st.dataframe(dept_df[["Department", "Total_Budget", "Total_Actual",
                          "Variance_Display", "Variance_%_Display", "Total_Forecast"]],
                 use_container_width=True, hide_index=True)

    st.subheader("Department Drill-Down")
    selected_dept = st.selectbox("Select Department", bd["Department"])
    detail_df = pd.DataFrame(budget["detail"])
    dept_detail = detail_df[detail_df["Department"] == selected_dept]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dept_detail["Month"], y=dept_detail["Budget"],
                             name="Budget", line=dict(color="#64748b", width=2)))
    fig.add_trace(go.Scatter(x=dept_detail["Month"], y=dept_detail["Actual"],
                             name="Actual", line=dict(color="#3b82f6", width=2)))
    fig.add_trace(go.Scatter(x=dept_detail["Month"], y=dept_detail["Forecast"],
                             name="Forecast", line=dict(color="#f59e0b", width=2, dash="dot")))
    fig.update_layout(title=f"{selected_dept} - Monthly Trend",
                      height=350, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Cash Flow
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Cash Flow":
    cf = analytics["cashflow"]

    st.title("Cash Flow Analysis")

    c1, c2, c3 = st.columns(3)
    c1.metric("Opening Balance", f"${cf['opening_balance'][0]:,.0f}")
    c2.metric("Closing Balance", f"${cf['closing_balance'][-1]:,.0f}")
    total_net = sum(cf["net_cashflow"])
    c3.metric("Net Cash Flow (YTD)", f"${total_net:,.0f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cf["months"], y=cf["operating_inflows"],
                             name="Operating Inflows", marker_color="#10b981"))
        fig.add_trace(go.Bar(x=cf["months"], y=[-v for v in cf["operating_outflows"]],
                             name="Operating Outflows", marker_color="#ef4444"))
        fig.add_trace(go.Bar(x=cf["months"], y=[-v for v in cf["investing_outflows"]],
                             name="Investing Outflows", marker_color="#f59e0b"))
        fig.update_layout(title="Cash Flow Components", barmode="relative",
                          height=400, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cf["months"], y=cf["closing_balance"],
            name="Cash Balance", line=dict(color="#3b82f6", width=3),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.1)",
        ))
        fig.update_layout(title="Cash Balance Trend", height=400, template="plotly_dark",
                          yaxis=dict(title="Balance ($)"))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Net Cash Flow")
    colors = ["#10b981" if v >= 0 else "#ef4444" for v in cf["net_cashflow"]]
    fig = go.Figure(go.Bar(x=cf["months"], y=cf["net_cashflow"],
                           marker_color=colors))
    fig.update_layout(height=350, template="plotly_dark",
                      yaxis=dict(title="Net Cash Flow ($)"))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Headcount & Workforce
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Headcount & Workforce":
    hc = analytics["headcount"]

    st.title("Headcount & Workforce Analytics")

    c1, c2, c3 = st.columns(3)
    c1.metric("Current Headcount", f"{hc['current_headcount']:,}")
    c2.metric("Open Positions", f"{hc['current_openings']}")
    c3.metric("Annual Compensation", f"${hc['total_annual_comp']:,.0f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        monthly = hc["monthly"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Total_Headcount"],
            name="Headcount", line=dict(color="#3b82f6", width=3),
        ))
        fig.add_trace(go.Bar(
            x=monthly["Month"], y=monthly["Open_Positions"],
            name="Open Positions", marker_color="rgba(245,158,11,0.6)",
            yaxis="y2",
        ))
        fig.update_layout(
            title="Headcount Trend & Open Positions",
            height=400, template="plotly_dark",
            yaxis2=dict(overlaying="y", side="right", title="Open Positions"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        dept = hc["by_department"]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=dept["Department"], x=dept["Total_Comp"],
            orientation="h", name="Total Comp",
            marker_color="#3b82f6",
        ))
        fig.update_layout(title="Total Compensation by Department",
                          height=400, template="plotly_dark",
                          xaxis=dict(title="Total Compensation ($)"))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Compensation Trend")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Total_Comp"],
        line=dict(color="#10b981", width=2), fill="tozeroy",
        fillcolor="rgba(16,185,129,0.1)",
    ))
    fig.update_layout(height=350, template="plotly_dark",
                      yaxis=dict(title="Monthly Comp ($)"))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPI Scorecard
# ══════════════════════════════════════════════════════════════════════════════

elif page == "KPI Scorecard":
    kpis = analytics["kpis"]

    st.title("KPI Scorecard")

    cols = st.columns(4)
    for i, name in enumerate(kpis["kpi_names"][:8]):
        detail = kpis["details"][name]
        with cols[i % 4]:
            delta = detail["latest_actual"] - detail["latest_target"]
            st.metric(
                name,
                f"{detail['latest_actual']}{detail['unit']}",
                delta=f"{delta:+.1f} vs target",
            )

    st.markdown("---")

    selected_kpi = st.selectbox("Select KPI for detailed view", kpis["kpi_names"])
    detail = kpis["details"][selected_kpi]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=detail["months"], y=detail["target"],
        name="Target", line=dict(color="#64748b", width=2, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=detail["months"], y=detail["actual"],
        name="Actual", line=dict(color="#3b82f6", width=3),
        fill="tonexty", fillcolor="rgba(59,130,246,0.1)",
    ))
    fig.update_layout(
        title=f"{selected_kpi} - Target vs Actual ({detail['unit']})",
        height=400, template="plotly_dark",
        yaxis=dict(title=detail["unit"]),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("KPI Summary Table")
    rows = []
    for name in kpis["kpi_names"]:
        d = kpis["details"][name]
        rows.append({
            "KPI": name,
            "Latest Actual": d["latest_actual"],
            "Target": d["latest_target"],
            "Avg Actual": d["avg_actual"],
            "Unit": d["unit"],
            "Status": "On Track" if d["on_track"] else "Off Track",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# Raw Data Explorer
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Raw Data Explorer":
    st.title("Raw Data Explorer")

    sheet_name = st.selectbox("Select Sheet", list(sheets.keys()))
    df = sheets[sheet_name]

    summary = summarize_dataframe(df, sheet_name)

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{summary['rows']:,}")
    c2.metric("Columns", f"{len(summary['columns'])}")
    c3.metric("Missing Values", f"{sum(summary['missing'].values()):,}")

    st.markdown("---")

    selected_cols = st.multiselect("Select columns to display", df.columns.tolist(),
                                   default=df.columns.tolist())
    st.dataframe(df[selected_cols], use_container_width=True, hide_index=True)

    if summary["numeric_columns"]:
        with st.expander("Descriptive Statistics"):
            st.dataframe(df[summary["numeric_columns"]].describe(),
                         use_container_width=True)

    st.download_button(
        "Download as CSV",
        df.to_csv(index=False),
        file_name=f"{sheet_name}.csv",
        mime="text/csv",
    )
