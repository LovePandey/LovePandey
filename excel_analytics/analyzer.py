"""Core analytics engine - reads Excel and computes metrics."""

import pandas as pd


def load_excel(filepath, sheet_name=None):
    """Load one or all sheets from an Excel file into DataFrames."""
    if sheet_name:
        return pd.read_excel(filepath, sheet_name=sheet_name)
    return pd.read_excel(filepath, sheet_name=None)  # dict of DataFrames


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


def compute_sales_analytics(sheets):
    """Compute dashboard-ready analytics from the sales workbook."""
    sales = sheets.get("Sales")
    targets = sheets.get("Targets")
    employees = sheets.get("Employees")

    results = {}

    if sales is not None:
        sales["Date"] = pd.to_datetime(sales["Date"])
        sales["Month"] = sales["Date"].dt.to_period("M").astype(str)
        sales["Profit"] = sales["Revenue"] - sales["Cost"]

        # KPIs
        results["kpis"] = {
            "total_revenue": round(float(sales["Revenue"].sum()), 2),
            "total_profit": round(float(sales["Profit"].sum()), 2),
            "total_units": int(sales["Units"].sum()),
            "avg_order_value": round(float(sales["Revenue"].mean()), 2),
            "profit_margin": round(float(sales["Profit"].sum() / sales["Revenue"].sum() * 100), 1),
            "total_transactions": len(sales),
        }

        # Monthly revenue trend
        monthly = sales.groupby("Month").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Units=("Units", "sum"),
        ).reset_index()
        results["monthly_trend"] = monthly.to_dict(orient="list")

        # Revenue by region
        by_region = sales.groupby("Region").agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
        ).reset_index()
        results["by_region"] = by_region.to_dict(orient="list")

        # Revenue by category
        by_category = sales.groupby("Category").agg(
            Revenue=("Revenue", "sum"),
            Units=("Units", "sum"),
        ).reset_index()
        results["by_category"] = by_category.to_dict(orient="list")

        # Top products by revenue
        by_product = sales.groupby("Product").agg(
            Revenue=("Revenue", "sum"),
            Units=("Units", "sum"),
            Profit=("Profit", "sum"),
        ).sort_values("Revenue", ascending=False).reset_index()
        results["by_product"] = by_product.to_dict(orient="list")

        # Region x Category heatmap data
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
