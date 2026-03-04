"""Generate sample Excel data for testing the analytics tool."""

import random
from datetime import datetime, timedelta

import openpyxl


def generate_sales_data(filepath="sample_data/sales_data.xlsx"):
    """Create a realistic sales dataset in Excel format."""
    wb = openpyxl.Workbook()

    # --- Sheet 1: Sales Transactions ---
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

    start_date = datetime(2025, 1, 1)
    random.seed(42)

    for i in range(500):
        date = start_date + timedelta(days=random.randint(0, 364))
        region = random.choice(regions)
        product = random.choice(list(products.keys()))
        category, base_price, base_cost = products[product]
        units = random.randint(1, 30)
        price = round(base_price * random.uniform(0.9, 1.1), 2)
        revenue = round(units * price, 2)
        cost = round(units * base_cost * random.uniform(0.9, 1.05), 2)
        ws.append([date, region, product, category, units, price, revenue, cost])

    # --- Sheet 2: Monthly Targets ---
    ws2 = wb.create_sheet("Targets")
    ws2.append(["Month", "Region", "Target_Revenue"])
    for month in range(1, 13):
        for region in regions:
            target = random.randint(20000, 50000)
            ws2.append([datetime(2025, month, 1), region, target])

    # --- Sheet 3: Employee Performance ---
    ws3 = wb.create_sheet("Employees")
    ws3.append(["Employee", "Region", "Department", "Deals_Closed", "Revenue_Generated"])
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank",
             "Ivy", "Jack", "Karen", "Leo", "Mia", "Nick", "Olivia", "Pete"]
    departments = ["Sales", "Marketing", "Support"]
    for name in names:
        region = random.choice(regions)
        dept = random.choice(departments)
        deals = random.randint(5, 80)
        rev = round(deals * random.uniform(500, 3000), 2)
        ws3.append([name, region, dept, deals, rev])

    wb.save(filepath)
    print(f"Sample data generated: {filepath}")
    return filepath


if __name__ == "__main__":
    generate_sales_data()
