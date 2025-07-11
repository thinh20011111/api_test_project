# tests/utils/report_generator.py
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.io as pio
import os

class ReportGenerator:
    def __init__(self, report_dir="reports"):
        self.report_dir = report_dir
        self.results = []

    def add_result(self, test_name, status, response_code):
        self.results.append({
            "test_name": test_name,
            "status": status,
            "response_code": response_code,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def generate_xlsx(self, filename="test_report.xlsx"):
        os.makedirs(f"{self.report_dir}/xlsx", exist_ok=True)
        result = pd.DataFrame(self.results)
        if result.empty:
            result = pd.DataFrame(columns=["test_name", "status", "response_code", "timestamp"])
        result.to_excel(f"{self.report_dir}/xlsx/{filename}", index=False)

    def generate_html(self, filename="test_report.html"):
        os.makedirs(f"{self.report_dir}/html", exist_ok=True)
        result = pd.DataFrame(self.results)
        if result.empty:
            result = pd.DataFrame(columns=["test_name", "status", "response_code", "timestamp"])
        
        # Create donut chart
        status_counts = result["status"].value_counts() if not result.empty else pd.Series({"No Results": 1})
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Test Results by Status",
            hole=0.4
        )
        
        # Generate HTML
        html_content = f"""
        <html>
        <head>
            <title>Test Report</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Test Report</h1>
            {pio.to_html(fig, full_html=False)}
            <h2>Test Details</h2>
            {result.to_html(index=False)}
        </body>
        </html>
        """
        
        # Ghi file với mã hóa utf-8
        with open(f"{self.report_dir}/html/{filename}", "w", encoding="utf-8") as f:
            f.write(html_content)