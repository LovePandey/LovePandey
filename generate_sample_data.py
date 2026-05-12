"""Generate sample FP&A Excel data for the analytics dashboard."""

import random
from datetime import datetime

import openpyxl


def generate_fpa_data(filepath="sample_data/fpa_data.xlsx"):
    """Create a realistic FP&A dataset with P&L, Budget vs Actuals, and Balance Sheet."""
    wb = openpyxl.Workbook()
    random.seed(42)

    months = [datetime(2025, m, 1) for m in range(1, 13)]
    month_labels = [d.strftime("%b-%Y") for d in months]

    # --- Sheet 1: P&L (Income Statement) ---
    ws = wb.active
    ws.title = "PnL"
    ws.append(["Account", "Category", "Type"] + month_labels)

    pnl_lines = [
        ("Product Revenue", "Revenue", "Revenue", 500000, 0.08),
        ("Service Revenue", "Revenue", "Revenue", 180000, 0.05),
        ("Licensing Revenue", "Revenue", "Revenue", 90000, 0.03),
        ("COGS - Materials", "COGS", "Expense", 150000, 0.06),
        ("COGS - Labor", "COGS", "Expense", 100000, 0.04),
        ("COGS - Overhead", "COGS", "Expense", 40000, 0.02),
        ("Salaries & Wages", "OpEx", "Expense", 180000, 0.03),
        ("Marketing & Advertising", "OpEx", "Expense", 45000, 0.10),
        ("Rent & Facilities", "OpEx", "Expense", 30000, 0.01),
        ("Software & IT", "OpEx", "Expense", 25000, 0.05),
        ("Travel & Entertainment", "OpEx", "Expense", 12000, 0.15),
        ("Professional Services", "OpEx", "Expense", 18000, 0.08),
        ("Depreciation", "OpEx", "Expense", 15000, 0.01),
        ("Interest Income", "Other Income", "Revenue", 5000, 0.02),
        ("Interest Expense", "Other Expense", "Expense", 8000, 0.01),
        ("Tax Provision", "Tax", "Expense", 40000, 0.05),
    ]

    for account, category, acct_type, base, volatility in pnl_lines:
        row = [account, category, acct_type]
        for i in range(12):
            seasonal = 1.0 + 0.1 * (i / 11)
            amount = round(base * seasonal * random.uniform(1 - volatility, 1 + volatility), 2)
            row.append(amount)
        ws.append(row)

    # --- Sheet 2: Budget vs Actuals ---
    ws2 = wb.create_sheet("Budget_vs_Actual")
    ws2.append(["Department", "Month", "Budget", "Actual", "Forecast"])

    departments = ["Sales", "Marketing", "Engineering", "Operations", "HR", "Finance"]
    for dept in departments:
        base_budget = random.randint(80000, 250000)
        for i, month in enumerate(month_labels):
            budget = round(base_budget * random.uniform(0.95, 1.05), 2)
            variance_pct = random.uniform(-0.15, 0.12)
            actual = round(budget * (1 + variance_pct), 2)
            forecast = round(budget * random.uniform(0.97, 1.08), 2)
            ws2.append([dept, month, budget, actual, forecast])

    # --- Sheet 3: Cash Flow ---
    ws3 = wb.create_sheet("CashFlow")
    ws3.append(["Month", "Operating_Inflows", "Operating_Outflows",
                "Investing_Outflows", "Financing_Inflows", "Financing_Outflows",
                "Opening_Balance"])

    opening = 2500000
    for i, month in enumerate(month_labels):
        op_in = round(random.uniform(700000, 950000), 2)
        op_out = round(random.uniform(500000, 700000), 2)
        inv_out = round(random.uniform(20000, 80000), 2)
        fin_in = round(random.uniform(0, 50000), 2)
        fin_out = round(random.uniform(10000, 40000), 2)
        ws3.append([month, op_in, op_out, inv_out, fin_in, fin_out, round(opening, 2)])
        opening += op_in - op_out - inv_out + fin_in - fin_out

    # --- Sheet 4: Headcount & Workforce ---
    ws4 = wb.create_sheet("Headcount")
    ws4.append(["Department", "Month", "Headcount", "Avg_Salary", "Total_Comp", "Open_Positions"])

    for dept in departments:
        base_hc = random.randint(15, 80)
        base_salary = random.randint(60000, 140000)
        for i, month in enumerate(month_labels):
            hc = base_hc + random.randint(-2, 3)
            salary = round(base_salary * random.uniform(0.98, 1.02), 2)
            total = round(hc * salary / 12, 2)
            openings = random.randint(0, 5)
            ws4.append([dept, month, hc, salary, total, openings])

    # --- Sheet 5: KPI Scorecard ---
    ws5 = wb.create_sheet("KPIs")
    ws5.append(["KPI", "Month", "Target", "Actual", "Unit"])

    kpi_defs = [
        ("Revenue Growth %", 15, 3, "%"),
        ("Gross Margin %", 65, 4, "%"),
        ("Operating Margin %", 20, 3, "%"),
        ("Customer Acquisition Cost", 250, 40, "$"),
        ("Customer Lifetime Value", 2800, 200, "$"),
        ("Employee Turnover %", 8, 2, "%"),
        ("Days Sales Outstanding", 35, 5, "days"),
        ("Current Ratio", 2.0, 0.3, "ratio"),
    ]

    for kpi_name, target, noise, unit in kpi_defs:
        for month in month_labels:
            actual_val = round(target + random.uniform(-noise, noise), 2)
            ws5.append([kpi_name, month, target, actual_val, unit])

    wb.save(filepath)
    print(f"FP&A sample data generated: {filepath}")
    return filepath


def generate_sales_data(filepath="sample_data/sales_data.xlsx"):
    """Create a realistic sales dataset in Excel format (legacy)."""
    wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = "Sales"
    headers = ["Date", "Region", "Product", "Category", "Units", "Unit_Price", "Revenue", "Cost"]
    ws.append(headers)

    regions = ["North", "South", "East", "West"]
    products = {
        "Laptop": ("Electronics", 800, 600),
        "Phone": ("Electronics", 500, 350),
        "Tablet": ("Electronics", 400, 280),
        "Desk": ("Furniture", 300, 180),
        "Chair": ("Furniture", 200, 120),
        "Monitor": ("Electronics", 350, 220),
        "Keyboard": ("Accessories", 80, 40),
        "Mouse": ("Accessories", 40, 20),
    }

    from datetime import timedelta
    start_date = datetime(2025, 1, 1)
    random.seed(42)

    for _ in range(500):
        date = start_date + timedelta(days=random.randint(0, 364))
        region = random.choice(regions)
        product = random.choice(list(products.keys()))
        category, base_price, base_cost = products[product]
        units = random.randint(1, 30)
        price = round(base_price * random.uniform(0.9, 1.1), 2)
        revenue = round(units * price, 2)
        cost = round(units * base_cost * random.uniform(0.9, 1.05), 2)
        ws.append([date, region, product, category, units, price, revenue, cost])

    ws2 = wb.create_sheet("Targets")
    ws2.append(["Month", "Region", "Target_Revenue"])
    for month in range(1, 13):
        for region in regions:
            target = random.randint(20000, 50000)
            ws2.append([datetime(2025, month, 1), region, target])

    ws3 = wb.create_sheet("Employees")
    ws3.append(["Employee", "Region", "Department", "Deals_Closed", "Revenue_Generated"])
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank",
             "Ivy", "Jack", "Karen", "Leo", "Mia", "Nick", "Olivia", "Pete"]
    departments_list = ["Sales", "Marketing", "Support"]
    for name in names:
        region = random.choice(regions)
        dept = random.choice(departments_list)
        deals = random.randint(5, 80)
        rev = round(deals * random.uniform(500, 3000), 2)
        ws3.append([name, region, dept, deals, rev])

    wb.save(filepath)
    print(f"Sample data generated: {filepath}")
    return filepath


if __name__ == "__main__":
    generate_fpa_data()
