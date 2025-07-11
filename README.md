Cấu trúc thư mục
api_test_project/
├── src/
│   └── api_tester.py      # Hàm kiểm thử API chính
├── tests/
│   └── test_api.py        # Các test case cụ thể
├── templates/
│   └── report_template.html  # Mẫu báo cáo HTML
├── static/
│   └── styles.css         # CSS cho báo cáo HTML
├── config/
│   ├── config.py         # Tiện ích cấu hình
│   └── environments.yaml  # Cấu hình các môi trường
├── reports/               # Thư mục chứa báo cáo (tạo tự động)
├── main.py               # Script chính để chạy kiểm thử và tạo báo cáo
└── README.md             # Hướng dẫn sử dụng


Tính năng

- Kiểm thử API linh hoạt: Hỗ trợ các phương thức HTTP như GET, POST, với payload và header tùy chỉnh.
- Hỗ trợ nhiều môi trường: Chuyển đổi giữa các môi trường (dev, staging, production) thông qua file cấu hình YAML.
- Báo cáo HTML tương tác: Báo cáo HTML có bảng tương tác với khả năng lọc và sắp xếp sử dụng DataTables.
- Báo cáo XLSX: Kết quả kiểm thử chi tiết được xuất ra file Excel để phân tích offline.
- Dễ mở rộng: Dễ dàng thêm test case hoặc môi trường mới.

===============================================================

HDCĐ

Các gói Python cần thiết:
pip install requests pytest pandas openpyxl jinja2 pyyaml

Cấu hình môi trường:
Chỉnh sửa file config/environments.yaml để thêm URL API và thời gian timeout cho từng môi trường. Ví dụ:

environments:
  dev:
    api_base_url: "https://api.dev.example.com"
    timeout: 10
  staging:
    api_base_url: "https://api.staging.example.com"
    timeout: 15
  production:
    api_base_url: "https://api.example.com"
    timeout: 20

Cài đặt thư viện:
pip install -r requirements.txt

===============================================================
Cách sử dụng:
1, Chạy kiểm thử:
python main.py

2, Chạy kiểm thử với môi trường khác (ví dụ: staging hoặc production):
python main.py --env staging

python main.py --env production

3, Xem báo cáo:
Báo cáo HTML và XLSX được tạo trong thư mục reports/.

Báo cáo HTML (ví dụ: api_test_report_dev_20250711_0913.html) có bảng tương tác với chức năng lọc và sắp xếp.

Báo cáo XLSX (ví dụ: api_test_report_dev_20250711_0913.xlsx) chứa kết quả kiểm thử chi tiết.

4, Thêm test case mới
- Mở file tests/test_api.py.
- Thêm các hàm kiểm thử mới theo mẫu hiện có. Ví 
- Tham số env_config được cung cấp tự động bởi pytest, chứa thông tin cấu hình môi trường.

def test_new_endpoint(env_config):
    result = perform_api_test(env_config, "/new-endpoint", expected_status=200)
    assert result["success"], f"Kiểm thử thất bại: {result['error_message']}"

5, Tùy chỉnh môi trường
Thêm môi trường mới vào config/environments.yaml với api_base_url và timeout tương ứng. Ví dụ:

environments:
  custom:
    api_base_url: "https://api.custom.example.com"
    timeout: 12

6, Chạy test case cụ thể:
Để chỉ chạy test case test_get_users:
python main.py --env dev --tests test_get_users

Để chạy nhiều test case (ví dụ: test_get_users và test_create_user):
python main.py --env dev --tests "test_get_users or test_create_user"

Sử dụng biểu thức logic:
and: Chạy các test case thỏa mãn cả hai điều kiện.
or: Chạy các test case thỏa mãn một trong hai điều kiện.
not: Loại trừ test case khớp với biểu thức.

