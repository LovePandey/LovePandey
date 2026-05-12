"""Core analytics engine - reads Excel and computes FP&A metrics."""

import pandas as pd


def load_excel(filepath, sheet_name=None):
    """Load one or all sheets from an Excel file into DataFrames."""
    if sheet_name:
        return pd.read_excel(filepath, sheet_name=sheet_name)
    return pd.read_excel(filepath, sheet_name=None)


def summarize_dataframe(df, name="Sheet"):
    """Return a quick summary dict for a DataFrame."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    return {
        "name": name,
        "rows": len(df),
        "columns": list(df.columns),
        "numeric_columns": numeric_cols,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": df.isnull().sum().to_dict(),
        "stats": df[numeric_cols].describe().to_dict() if numeric_cols else {},
    }


def compute_pnl_analytics(pnl_df):
    """Compute P&L metrics from the income statement sheet."""
    months = [c for c in pnl_df.columns if c not in ("Account", "Category", "Type")]

    revenue_mask = pnl_df["Type"] == "Revenue"
    expense_mask = pnl_df["Type"] == "Expense"

    revenue_by_month = pnl_df.loc[revenue_mask, months].sum()
    expense_by_month = pnl_df.loc[expense_mask, months].sum()
    net_income_by_month = revenue_by_month - expense_by_month

    cogs_mask = pnl_df["Category"] == "COGS"
    opex_mask = pnl_df["Category"] == "OpEx"

    cogs_by_month = pnl_df.loc[cogs_mask, months].sum()
    opex_by_month = pnl_df.loc[opex_mask, months].sum()
    gross_profit_by_month = revenue_by_month - cogs_by_month

    gross_margin = (gross_profit_by_month / revenue_by_month * 100).round(1)
    operating_margin = ((gross_profit_by_month - opex_by_month) / revenue_by_month * 100).round(1)
    net_margin = (net_income_by_month / revenue_by_month * 100).round(1)

    by_category = pnl_df.groupby("Category")[months].sum()
    category_totals = by_category.sum(axis=1).to_dict()

    return {
        "months": list(months),
        "revenue": revenue_by_month.round(2).tolist(),
        "expenses": expense_by_month.round(2).tolist(),
        "cogs": cogs_by_month.round(2).tolist(),
        "opex": opex_by_month.round(2).tolist(),
        "gross_profit": gross_profit_by_month.round(2).tolist(),
        "net_income": net_income_by_month.round(2).tolist(),
        "gross_margin": gross_margin.tolist(),
        "operating_margin": operating_margin.tolist(),
        "net_margin": net_margin.tolist(),
        "total_revenue": round(float(revenue_by_month.sum()), 2),
        "total_expenses": round(float(expense_by_month.sum()), 2),
        "total_net_income": round(float(net_income_by_month.sum()), 2),
        "category_totals": category_totals,
        "line_items": pnl_df.to_dict(orient="records"),
    }


def compute_budget_analytics(budget_df):
    """Compute budget vs actual variance analysis."""
    budget_df = budget_df.copy()
    budget_df["Variance"] = budget_df["Actual"] - budget_df["Budget"]
    budget_df["Variance_%"] = ((budget_df["Variance"] / budget_df["Budget"]) * 100).round(1)

    by_dept = budget_df.groupby("Department").agg(
        Total_Budget=("Budget", "sum"),
        Total_Actual=("Actual", "sum"),
        Total_Forecast=("Forecast", "sum"),
    ).reset_index()
    by_dept["Variance"] = by_dept["Total_Actual"] - by_dept["Total_Budget"]
    by_dept["Variance_%"] = ((by_dept["Variance"] / by_dept["Total_Budget"]) * 100).round(1)

    by_month = budget_df.groupby("Month").agg(
        Budget=("Budget", "sum"),
        Actual=("Actual", "sum"),
        Forecast=("Forecast", "sum"),
    ).reset_index()
    by_month["Variance"] = by_month["Actual"] - by_month["Budget"]

    return {
        "by_department": by_dept.to_dict(orient="list"),
        "by_month": by_month.to_dict(orient="list"),
        "detail": budget_df.to_dict(orient="records"),
        "total_budget": round(float(budget_df["Budget"].sum()), 2),
        "total_actual": round(float(budget_df["Actual"].sum()), 2),
        "total_variance": round(float(budget_df["Variance"].sum()), 2),
    }


def compute_cashflow_analytics(cf_df):
    """Compute cash flow metrics."""
    cf_df = cf_df.copy()
    cf_df["Net_Operating"] = cf_df["Operating_Inflows"] - cf_df["Operating_Outflows"]
    cf_df["Net_Financing"] = cf_df["Financing_Inflows"] - cf_df["Financing_Outflows"]
    cf_df["Net_CashFlow"] = cf_df["Net_Operating"] - cf_df["Investing_Outflows"] + cf_df["Net_Financing"]
    cf_df["Closing_Balance"] = cf_df["Opening_Balance"] + cf_df["Net_CashFlow"]

    return {
        "months": cf_df["Month"].tolist(),
        "operating_inflows": cf_df["Operating_Inflows"].round(2).tolist(),
        "operating_outflows": cf_df["Operating_Outflows"].round(2).tolist(),
        "net_operating": cf_df["Net_Operating"].round(2).tolist(),
        "investing_outflows": cf_df["Investing_Outflows"].round(2).tolist(),
        "net_financing": cf_df["Net_Financing"].round(2).tolist(),
        "net_cashflow": cf_df["Net_CashFlow"].round(2).tolist(),
        "opening_balance": cf_df["Opening_Balance"].round(2).tolist(),
        "closing_balance": cf_df["Closing_Balance"].round(2).tolist(),
    }


def compute_headcount_analytics(hc_df):
    """Compute workforce/headcount metrics."""
    latest_month = hc_df["Month"].iloc[-1]
    latest = hc_df[hc_df["Month"] == latest_month]

    by_dept = hc_df.groupby("Department").agg(
        Avg_Headcount=("Headcount", "mean"),
        Total_Comp=("Total_Comp", "sum"),
        Total_Openings=("Open_Positions", "sum"),
    ).reset_index()

    monthly_totals = hc_df.groupby("Month").agg(
        Total_Headcount=("Headcount", "sum"),
        Total_Comp=("Total_Comp", "sum"),
        Open_Positions=("Open_Positions", "sum"),
    ).reset_index()

    return {
        "by_department": by_dept.to_dict(orient="list"),
        "monthly": monthly_totals.to_dict(orient="list"),
        "current_headcount": int(latest["Headcount"].sum()),
        "current_openings": int(latest["Open_Positions"].sum()),
        "total_annual_comp": round(float(hc_df["Total_Comp"].sum()), 2),
    }


def compute_kpi_analytics(kpi_df):
    """Compute KPI scorecard analysis."""
    kpi_df = kpi_df.copy()
    kpi_df["Variance"] = kpi_df["Actual"] - kpi_df["Target"]

    kpi_names = kpi_df["KPI"].unique().tolist()
    kpi_details = {}
    for name in kpi_names:
        subset = kpi_df[kpi_df["KPI"] == name]
        kpi_details[name] = {
            "months": subset["Month"].tolist(),
            "target": subset["Target"].tolist(),
            "actual": subset["Actual"].round(2).tolist(),
            "unit": subset["Unit"].iloc[0],
            "latest_actual": round(float(subset["Actual"].iloc[-1]), 2),
            "latest_target": round(float(subset["Target"].iloc[-1]), 2),
            "avg_actual": round(float(subset["Actual"].mean()), 2),
            "on_track": abs(float(subset["Actual"].iloc[-1]) - float(subset["Target"].iloc[-1])) < abs(float(subset["Target"].iloc[-1]) * 0.1),
        }

    return {
        "kpi_names": kpi_names,
        "details": kpi_details,
    }


def compute_fpa_analytics(sheets):
    """Compute all FP&A analytics from the workbook."""
    results = {}

    if "PnL" in sheets:
        results["pnl"] = compute_pnl_analytics(sheets["PnL"])

    if "Budget_vs_Actual" in sheets:
        results["budget"] = compute_budget_analytics(sheets["Budget_vs_Actual"])

    if "CashFlow" in sheets:
        results["cashflow"] = compute_cashflow_analytics(sheets["CashFlow"])

    if "Headcount" in sheets:
        results["headcount"] = compute_headcount_analytics(sheets["Headcount"])

    if "KPIs" in sheets:
        results["kpis"] = compute_kpi_analytics(sheets["KPIs"])

    return results


def compute_sales_analytics(sheets):
    """Compute dashboard-ready analytics from the sales workbook (legacy)."""
    sales = sheets.get("Sales")
    targets = sheets.get("Targets")
    employees = sheets.get("Employees")

    results = {}

    if sales is not None:
        sales["Date"] = pd.to_datetime(sales["Date"])
        sales["Month"] = sales["Date"].dt.to_period("M").astype(str)
        sales["Profit"] = sales["Revenue"] - sales["Cost"]

        results["kpis"] = {
            "total_revenue": round(float(sales["Revenue"].sum()), 2),
            "total_profit": round(float(sales["Profit"].sum()), 2),
            "total_units": int(sales["Units"].sum()),
            "avg_order_value": round(float(sales["Revenue"].mean()), 2),
            "profit_margin": round(float(sales["Profit"].sum() / sales["Revenue"].sum() * 100), 1),
            "total_transactions": len(sales),
        }

        monthly = sales.groupby("Month").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Units=("Units", "sum"),
        ).reset_index()
        results["monthly_trend"] = monthly.to_dict(orient="list")

        by_region = sales.groupby("Region").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
        ).reset_index()
        results["by_region"] = by_region.to_dict(orient="list")

        by_category = sales.groupby("Category").agg(
            Revenue=("Revenue", "sum"),
            Units=("Units", "sum"),
        ).reset_index()
        results["by_category"] = by_category.to_dict(orient="list")

        by_product = sales.groupby("Product").agg(
            Revenue=("Revenue", "sum"),
            Units=("Units", "sum"),
            Profit=("Profit", "sum"),
        ).sort_values("Revenue", ascending=False).reset_index()
        results["by_product"] = by_product.to_dict(orient="list")

        pivot = sales.pivot_table(values="Revenue", index="Region", columns="Category", aggfunc="sum", fill_value=0)
        results["region_category_heatmap"] = {
            "regions": pivot.index.tolist(),
            "categories": pivot.columns.tolist(),
            "values": pivot.values.tolist(),
        }

    if targets is not None and sales is not None:
        targets["Month"] = pd.to_datetime(targets["Month"]).dt.to_period("M").astype(str)
        target_monthly = targets.groupby("Month")["Target_Revenue"].sum().reset_index()
        actual_monthly = sales.groupby("Month")["Revenue"].sum().reset_index()
        comparison = pd.merge(target_monthly, actual_monthly, on="Month", how="outer").fillna(0)
        results["target_vs_actual"] = comparison.to_dict(orient="list")

    if employees is not None:
        top_emp = employees.sort_values("Revenue_Generated", ascending=False).head(10)
        results["top_employees"] = top_emp.to_dict(orient="list")

        by_dept = employees.groupby("Department").agg(
            Total_Revenue=("Revenue_Generated", "sum"),
            Avg_Deals=("Deals_Closed", "mean"),
            Headcount=("Employee", "count"),
        ).reset_index()
        results["by_department"] = by_dept.to_dict(orient="list")

    return results
