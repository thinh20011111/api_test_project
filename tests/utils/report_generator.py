# tests/utils/report_generator.py
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.io as pio
import os
import json
import logging

# Thiết lập logging để debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportGenerator:
    def __init__(self, report_dir="reports"):
        self.report_dir = report_dir
        self.results = []
        self.json_file = f"{self.report_dir}/json/test_results.json"
        os.makedirs(f"{self.report_dir}/json", exist_ok=True)

    def add_result(self, test_name, status, response_code, request_info, response_body):
        try:
            # Định dạng response_body và headers
            response_body_str = json.dumps(response_body, indent=2, ensure_ascii=False)[:1000] + "..." if len(json.dumps(response_body, indent=2)) > 1000 else json.dumps(response_body, indent=2, ensure_ascii=False)
            headers_str = json.dumps(request_info["headers"], indent=2, ensure_ascii=False)
            result = {
                "test_name": test_name,
                "status": status,
                "response_code": response_code,
                "url": request_info["url"],
                "method": request_info["method"],
                "headers": headers_str,
                "response_body": response_body_str,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.results.append(result)
            # Lưu vào file JSON
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            logging.debug(f"Added result and saved to JSON: {result}")
        except Exception as e:
            logging.error(f"Error adding result: {e}")

    def generate_xlsx(self, env, timestamp):
        try:
            os.makedirs(f"{self.report_dir}/xlsx", exist_ok=True)
            filename = f"test_report_{env}_{timestamp}.xlsx"
            # Đọc dữ liệu từ file JSON
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    results = json.load(f)
            except FileNotFoundError:
                results = []
                logging.warning(f"JSON file {self.json_file} not found, using empty results")
            result = pd.DataFrame(results)
            if result.empty:
                logging.warning("No test results to generate XLSX report, skipping generation")
                return None
            logging.debug(f"XLSX table content: {result.to_dict()}")
            writer = pd.ExcelWriter(f"{self.report_dir}/xlsx/{filename}", engine="openpyxl")
            result.to_excel(writer, index=False, sheet_name="Test Results")
            # Điều chỉnh chiều rộng cột và bật wrap text
            worksheet = writer.sheets["Test Results"]
            for idx, col in enumerate(result.columns):
                max_length = max(
                    result[col].astype(str).map(len).max() if not result[col].empty else 10,
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 5, 50)
                for cell in worksheet[col]:
                    cell.alignment = cell.alignment.copy(wrap_text=True)
            writer.close()
            logging.debug(f"Generated XLSX report: {filename}")
            return f"{self.report_dir}/xlsx/{filename}"
        except Exception as e:
            logging.error(f"Error generating XLSX: {e}")
            return None

    def generate_html(self, env, timestamp):
        try:
            os.makedirs(f"{self.report_dir}/html", exist_ok=True)
            filename = f"test_report_{env}_{timestamp}.html"
            # Đọc dữ liệu từ file JSON
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    results = json.load(f)
            except FileNotFoundError:
                results = []
                logging.warning(f"JSON file {self.json_file} not found, using empty results")
            result = pd.DataFrame(results)
            if result.empty:
                result = pd.DataFrame(columns=["test_name", "status", "response_code", "url", "method", "headers", "response_body", "timestamp"])
                logging.warning("No test results to generate HTML report")
            logging.debug(f"HTML table content: {result.to_dict()}")
            
            # Create donut chart
            status_counts = result["status"].value_counts() if not result.empty else pd.Series({"No Results": 1})
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Test Results by Status",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            # Generate HTML với Bootstrap
            html_content = f"""
            <html>
            <head>
                <title>Test Report ({env})</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ padding: 20px; font-family: Arial, sans-serif; }}
                    pre {{ white-space: pre-wrap; max-height: 300px; overflow-y: auto; background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 0.9em; }}
                    table {{ margin-top: 20px; width: 100%; }}
                    th, td {{ vertical-align: top; word-wrap: break-word; padding: 10px !important; }}
                    .table {{ table-layout: auto; }}
                    .status-PASS {{ color: #28a745; font-weight: bold; }}
                    .status-FAIL {{ color: #dc3545; font-weight: bold; }}
                    .status-SKIPPED {{ color: #ffc107; font-weight: bold; }}
                    th {{ min-width: 100px; }}
                    td {{ max-width: 400px; }}
                </style>
            </head>
            <body>
                <div class="container-fluid">
                    <h1 class="my-4">Test Report ({env})</h1>
                    <div class="row">
                        <div class="col-md-4">
                            {pio.to_html(fig, full_html=False)}
                        </div>
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Summary</h5>
                                    <p>Total Tests: {len(result)}</p>
                                    <p>Passed: {len(result[result['status'] == 'PASS']) if not result.empty else 0} ({(len(result[result['status'] == 'PASS']) / len(result) * 100 if len(result) > 0 else 0):.1f}%)</p>
                                    <p>Failed: {len(result[result['status'] == 'FAIL']) if not result.empty else 0} ({(len(result[result['status'] == 'FAIL']) / len(result) * 100 if len(result) > 0 else 0):.1f}%)</p>
                                    <p>Skipped: {len(result[result['status'] == 'SKIPPED']) if not result.empty else 0} ({(len(result[result['status'] == 'SKIPPED']) / len(result) * 100 if len(result) > 0 else 0):.1f}%)</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <h2 class="my-4">Test Details</h2>
                    {result.to_html(index=False, escape=False, classes="table table-striped table-bordered table-sm", formatters={
                        "headers": lambda x: f"<pre>{x}</pre>",
                        "response_body": lambda x: f"<pre>{x}</pre>",
                        "url": lambda x: f"<a href='{x}' target='_blank'>{x}</a>",
                        "status": lambda x: f"<span class='status-{x}'>{x}</span>"
                    })}
                </div>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
            </body>
            </html>
            """
            
            with open(f"{self.report_dir}/html/{filename}", "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.debug(f"Generated HTML report: {filename}")
            return f"{self.report_dir}/html/{filename}"
        except Exception as e:
            logging.error(f"Error generating HTML: {e}")
            return None