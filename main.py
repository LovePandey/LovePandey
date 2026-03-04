#!/usr/bin/env python3
"""
Excel Analytics Tool - CLI Entry Point

Usage:
    python main.py                          # Use sample data
    python main.py path/to/your/file.xlsx   # Use your own Excel file
    python main.py data.xlsx -o report.html  # Custom output path
"""

import argparse
import sys

from excel_analytics.analyzer import load_excel, summarize_dataframe, compute_sales_analytics
from excel_analytics.dashboard import generate_dashboard
from generate_sample_data import generate_sales_data


def main():
    parser = argparse.ArgumentParser(description="Generate an interactive dashboard from Excel data")
    parser.add_argument("input", nargs="?", default=None, help="Path to Excel file (omit to generate sample data)")
    parser.add_argument("-o", "--output", default="output/dashboard.html", help="Output HTML path")
    args = parser.parse_args()

    # Generate sample data if no input provided
    if args.input is None:
        print("No input file specified. Generating sample data...")
        args.input = generate_sales_data()

    print(f"\nLoading: {args.input}")
    sheets = load_excel(args.input)

    # Print summary for each sheet
    print(f"Found {len(sheets)} sheet(s):\n")
    for name, df in sheets.items():
        summary = summarize_dataframe(df, name)
        print(f"  [{name}] {summary['rows']} rows x {len(summary['columns'])} cols")
        missing_total = sum(summary["missing"].values())
        if missing_total > 0:
            print(f"    Missing values: {missing_total}")

    # Run analytics
    print("\nComputing analytics...")
    analytics = compute_sales_analytics(sheets)

    kpis = analytics.get("kpis", {})
    if kpis:
        print(f"\n  Revenue:       ${kpis['total_revenue']:>12,.2f}")
        print(f"  Profit:        ${kpis['total_profit']:>12,.2f}")
        print(f"  Margin:         {kpis['profit_margin']:>11}%")
        print(f"  Units Sold:     {kpis['total_units']:>11,}")
        print(f"  Transactions:   {kpis['total_transactions']:>11,}")

    # Generate dashboard
    print(f"\nGenerating dashboard...")
    output_path = generate_dashboard(analytics, args.output)
    print(f"Done! Open {output_path} in a browser to view your dashboard.")


if __name__ == "__main__":
    main()
