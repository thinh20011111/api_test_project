# tests/utils/report_generator.py
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.io as pio
import os
import json

class ReportGenerator:
    def __init__(self, report_dir="reports"):
        self.report_dir = report_dir
        self.results = []

    def add_result(self, test_name, status, response_code, request_info, response_body):
        # Giới hạn kích thước response_body nếu quá dài
        response_body_str = json.dumps(response_body, indent=2)[:1000] + "..." if len(json.dumps(response_body, indent=2)) > 1000 else json.dumps(response_body, indent=2)
        self.results.append({
            "test_name": test_name,
            "status": status,
            "response_code": response_code,
            "url": request_info["url"],
            "method": request_info["method"],
            "headers": json.dumps(request_info["headers"], indent=2),
            "response_body": response_body_str,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def generate_xlsx(self, env, timestamp):
        os.makedirs(f"{self.report_dir}/xlsx", exist_ok=True)
        filename = f"test_report_{env}_{timestamp}.xlsx"
        result = pd.DataFrame(self.results)
        if result.empty:
            result = pd.DataFrame(columns=["test_name", "status", "response_code", "url", "method", "headers", "response_body", "timestamp"])
        result.to_excel(f"{self.report_dir}/xlsx/{filename}", index=False)

    def generate_html(self, env, timestamp):
        os.makedirs(f"{self.report_dir}/html", exist_ok=True)
        filename = f"test_report_{env}_{timestamp}.html"
        result = pd.DataFrame(self.results)
        if result.empty:
            result = pd.DataFrame(columns=["test_name", "status", "response_code", "url", "method", "headers", "response_body", "timestamp"])
        
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
            <title>Test Report ({env})</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                pre {{ white-space: pre-wrap; max-height: 300px; overflow-y: auto; }}
            </style>
        </head>
        <body>
            <h1>Test Report ({env})</h1>
            {pio.to_html(fig, full_html=False)}
            <h2>Test Details</h2>
            {result.to_html(index=False, escape=False, formatters={
                "headers": lambda x: f"<pre>{x}</pre>",
                "response_body": lambda x: f"<pre>{x}</pre>"
            })}
        </body>
        </html>
        """
        
        with open(f"{self.report_dir}/html/{filename}", "w", encoding="utf-8") as f:
            f.write(html_content)