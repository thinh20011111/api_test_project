import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.io as pio
import os
import json
import logging

# Thiết lập logging để ghi vào file
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/api_test.log',
    filemode='w'
)

class ReportGenerator:
    def __init__(self, report_dir="reports"):
        self.report_dir = report_dir
        self.results = []
        self.json_file = f"{self.report_dir}/json/test_results.json"
        os.makedirs(f"{self.report_dir}/json", exist_ok=True)

    def add_result(self, test_name, status, response_code, request_info, response_body):
        try:
            # Định dạng response_body và headers với xuống dòng và thụt lề
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
                "time_duration": request_info.get("time_duration", 0),  # Lưu bằng giây
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
            filepath = f"{self.report_dir}/xlsx/{filename}"
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
            # Đổi tên cột time_duration thành Time Duration (s)
            result = result.rename(columns={"time_duration": "Time Duration (s)"})
            logging.debug(f"XLSX table content: {result.to_dict()}")
            # Ghi vào file Excel
            writer = pd.ExcelWriter(filepath, engine="openpyxl")
            result.to_excel(writer, index=False, sheet_name="Test Results")
            # Điều chỉnh chiều rộng cột và bật wrap text
            worksheet = writer.sheets["Test Results"]
            for idx, col in enumerate(result.columns):
                max_length = max(
                    result[col].astype(str).map(len).max() if not result[col].empty else 10,
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 5, 50)
                for cell in worksheet[chr(65 + idx)]:  # Sử dụng chỉ số cột
                    cell.alignment = cell.alignment.copy(wrap_text=True)
            writer.close()
            logging.debug(f"Successfully generated XLSX report: {filepath}")
            return filepath
        except PermissionError as pe:
            logging.error(f"Permission denied when creating XLSX file {filepath}: {pe}")
            return None
        except Exception as e:
            logging.error(f"Error generating XLSX file {filepath}: {e}")
            return None

    def generate_html(self, env, timestamp):
        try:
            os.makedirs(f"{self.report_dir}/html", exist_ok=True)
            filename = f"test_report_{env}_{timestamp}.html"
            filepath = f"{self.report_dir}/html/{filename}"
            # Đọc dữ liệu từ file JSON
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    results = json.load(f)
            except FileNotFoundError:
                results = []
                logging.warning(f"JSON file {self.json_file} not found, using empty results")
            result = pd.DataFrame(results)
            if result.empty:
                result = pd.DataFrame(columns=["test_name", "status", "response_code", "url", "method", "headers", "response_body", "time_duration", "timestamp"])
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
            fig.update_traces(
                hoverinfo="label+percent",
                textinfo="value+percent",
                textfont_size=14,
                marker=dict(line=dict(color='#000000', width=2))
            )
            
            # Convert DataFrame to HTML with collapsible content and color-coded time_duration
            table_rows = ""
            for idx, row in result.iterrows():
                time_duration = float(row['time_duration'])
                time_class = "text-success" if time_duration < 0.2 else "text-warning" if time_duration < 0.5 else "text-danger"
                table_rows += f"""
                <tr>
                    <td class="text-truncate">{row['test_name']}</td>
                    <td><span class='status-{row['status']}'>{row['status']}</span></td>
                    <td>{row['response_code']}</td>
                    <td><a href='{row['url']}' target='_blank' class='text-truncate' style='display: inline-block;'>{row['url']}</a></td>
                    <td>{row['method']}</td>
                    <td>
                        <button class='btn btn-sm btn-outline-primary' type='button' data-bs-toggle='collapse' data-bs-target='#headers{idx}' aria-expanded='false' aria-controls='headers{idx}'>
                            Toggle Headers
                        </button>
                        <div class='collapse' id='headers{idx}'>
                            <pre class='mt-2 mb-0 text-wrap json-pretty'>{row['headers'].replace('\n', '<br>')}</pre>
                        </div>
                    </td>
                    <td>
                        <button class='btn btn-sm btn-outline-primary' type='button' data-bs-toggle='collapse' data-bs-target='#response{idx}' aria-expanded='false' aria-controls='response{idx}'>
                            Toggle Response
                        </button>
                        <div class='collapse' id='response{idx}'>
                            <pre class='mt-2 mb-0 text-wrap json-pretty'>{row['response_body'].replace('\n', '<br>')}</pre>
                        </div>
                    </td>
                    <td><span class='{time_class}'>{time_duration:.3f} s</span></td>
                    <td class="text-truncate">{row['timestamp']}</td>
                </tr>
                """
            
            # JavaScript code for Plotly and colResizable
            js_code = """
                /* Lấy biểu đồ Plotly */
                document.addEventListener('DOMContentLoaded', function() {
                    const chart = document.querySelector('.plotly-graph-div');
                    chart.on('plotly_click', function(data) {
                        const status = data.points[0].label;
                        if (status === 'No Results') return;
                        const rows = document.querySelectorAll('#testTableBody tr');
                        rows.forEach(row => {
                            const statusCell = row.querySelector('td:nth-child(2) span').textContent;
                            row.style.display = (status === statusCell) ? '' : 'none';
                        });
                    });
                    /* Reset filter khi click ngoài biểu đồ */
                    document.querySelector('.container-fluid').addEventListener('click', function(e) {
                        if (!e.target.closest('.plotly-graph-div')) {
                            const rows = document.querySelectorAll('#testTableBody tr');
                            rows.forEach(row => { row.style.display = ''; });
                        }
                    });
                    /* Kích hoạt colResizable cho bảng */
                    $(document).ready(function() {
                        $("#testTable").colResizable({
                            liveDrag: true,
                            gripInnerHtml: "<div class='grip'></div>",
                            draggingClass: "dragging"
                        });
                    });
                });
            """
            
            # Generate HTML với Bootstrap và colResizable, thêm CSS cho JSON
            html_content = f"""
<html>
<head>
    <title>Test Report ({env})</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jeresig-jquery.hotkeys/0.2.0/jquery.hotkeys.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/colresizable/1.6.0/colResizable.min.js"></script>
    <style>
        body {{ padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .table-container {{ max-height: 600px; overflow-y: auto; }}
        .table {{ font-size: 0.85em; width: 100%; border-collapse: collapse; }}
        th, td {{ vertical-align: middle; padding: 8px !important; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        th {{ background-color: #f1f3f5; position: sticky; top: 0; z-index: 10; }}
        .status-PASS {{ color: #28a745; font-weight: 600; }}
        .status-FAIL {{ color: #dc3545; font-weight: 600; }}
        .status-SKIPPED {{ color: #ffc107; font-weight: 600; }}
        pre.text-wrap {{ white-space: pre-wrap; max-height: 200px; overflow-y: auto; background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 0.8em; max-width: 100%; word-wrap: break-word; }}
        .json-pretty {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 0.8em; white-space: pre-wrap; overflow-x: auto; line-height: 1.4; }}
        .text-truncate {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100%; }}
        .chart-container {{ max-width: 400px; margin-bottom: 20px; }}
        .text-success {{ color: #28a745; font-weight: 600; }} /* Xanh cho nhanh (< 0.2 s) */
        .text-warning {{ color: #ffc107; font-weight: 600; }} /* Vàng cho trung bình (0.2-0.5 s) */
        .text-danger {{ color: #dc3545; font-weight: 600; }} /* Đỏ cho chậm (>= 0.5 s) */
        .grip {{ width: 5px; height: 20px; background: #ccc; margin: 0 auto; }}
        .dragging {{ cursor: col-resize; }}
        @media (max-width: 768px) {{ .table {{ font-size: 0.75em; }} }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <h1 class="my-4">Test Report ({env})</h1>
        <div class="row">
            <div class="col-lg-3 col-md-4 chart-container">
                {pio.to_html(fig, full_html=False, include_plotlyjs='cdn')}
            </div>
            <div class="col-lg-9 col-md-8">
                <div class="card mb-4">
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
        <div class="table-container">
            <table id="testTable" class="table table-striped table-bordered table-sm">
                <thead>
                    <tr>
                        <th style="width: 15%;">Test Name</th>
                        <th style="width: 10%;">Status</th>
                        <th style="width: 10%;">Response Code</th>
                        <th style="width: 15%;">URL</th>
                        <th style="width: 10%;">Method</th>
                        <th style="width: 20%;">Headers</th>
                        <th style="width: 20%;">Response Body</th>
                        <th style="width: 10%;">Time Duration (s)</th>
                        <th style="width: 10%;">Timestamp</th>
                    </tr>
                </thead>
                <tbody id="testTableBody">
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        {js_code}
    </script>
</body>
</html>
"""
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.debug(f"Successfully generated HTML report: {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Error generating HTML file {filepath}: {e}")
            return None