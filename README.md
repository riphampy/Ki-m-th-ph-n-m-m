# PC Parts Shop — backend phục vụ kiểm thử

Backend Flask + Flask-SQLAlchemy + SQLite, chạy bằng Waitress. Có 36 API nghiệp vụ, session/cookie, Swagger UI chạy từ tài nguyên cục bộ, seed cố định và trang frontend placeholder. Không dùng Docker, JWT hay CSRF token.

## Cài đặt và chạy trên Windows

Cần Python 3.10+ và Git. Mở PowerShell trong thư mục `pc-parts-shop`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Nếu PowerShell không cho kích hoạt venv, không cần thay đổi execution policy:

```powershell
.\.venv\Scripts\python -X utf8 -m pip install -r requirements.txt
.\.venv\Scripts\python run.py
```

`-X utf8` tránh lỗi hiển thị của pip cũ khi đường dẫn Windows có dấu. Server nghe `127.0.0.1:5000`, 16 worker threads. Lần chạy đầu tự tạo `shop.db` và seed; các lần sau giữ nguyên dữ liệu. Dừng bằng Ctrl+C.

- Trang placeholder: http://localhost:5000/
- Swagger UI: http://localhost:5000/apidocs
- Swagger JSON: http://localhost:5000/apispec_1.json
- [Hợp đồng API cho frontend](docs/API.md)
- [Quy tắc nghiệp vụ BR01…](docs/BUSINESS_RULES.md)
- [Kết quả kiểm tra và giới hạn](docs/VERIFICATION.md)

Trong Swagger, gọi `/api/auth/login` trước rồi gọi API cần đăng nhập. Cookie được trình duyệt gửi tự động trên cùng origin. Dùng nhất quán `localhost` hoặc `127.0.0.1`; cookie giữa hai host khác nhau.

## Tài khoản và seed

| Email | Mật khẩu mẫu | Vai trò |
|---|---|---|
| admin@test.com | Admin@123 | ADMIN |
| customer1@test.com | Customer@123 | CUSTOMER |
| customer2@test.com | Customer@123 | CUSTOMER |
| customer3@test.com | Customer@123 | CUSTOMER |

Các mật khẩu trên chỉ là fixture công khai của bài tập. Mật khẩu lưu trong DB dưới dạng hash Werkzeug.

Seed gồm 4 danh mục (ID 1 CPU, 2 RAM, 3 VGA, 4 PSU), mỗi danh mục 25 sản phẩm, 10 đơn ở 5 trạng thái, 3 đánh giá. Sản phẩm ID 1/26/51/76 tồn kho 0; ID 2/27/52/77 tồn kho 1; ID 3/28/53/78 tồn kho 5. Giá và biến thể cấu hình là dữ liệu mô phỏng, không phải báo giá/catalog thương mại chính xác. Đơn mẫu có thời gian cố định trong tháng 1–3/2026.

## Reset và tạo đơn mẫu

Mặc định `APP_ENV=test`. Hai API test không yêu cầu đăng nhập:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/test/reset
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/test/seed-orders -ContentType 'application/json' -Body '{"count":20}'
```

Reset xóa toàn bộ dữ liệu nghiệp vụ và seed lại, bao gồm ID cố định; cookie của client gọi reset được xóa. Các client khác nên đăng xuất/đăng nhập lại sau reset. Không gọi reset giữa một bài đo tải; thực hiện ở bước setup. Seed-orders tạo thêm đơn, không reset; thứ tự trạng thái lặp PENDING → CONFIRMED → SHIPPING → COMPLETED → CANCELLED, trừ kho với ba trạng thái giữa. Nếu thiếu kho, toàn bộ yêu cầu rollback.

Để tắt API test:

```powershell
$env:APP_ENV = 'prod'
$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
python run.py
```

Khi `APP_ENV=prod`, cả hai API trả 404. Không có `SECRET_KEY` thì ứng dụng sinh khóa mới mỗi lần khởi động, các session cũ hết hiệu lực. Không đọc `.env` tự động; đặt biến qua PowerShell. `prod` chỉ là cờ tắt API test, không tự thay đổi/xóa tài khoản mẫu.

## Tóm tắt validation

Chuỗi thông thường được trim hai đầu trước khi kiểm tra; mật khẩu giữ nguyên. Body phải là JSON object, không nhận trường ngoài hợp đồng. Trả lỗi tại trường đầu tiên vi phạm trong `errors`. Số nguyên JSON không chấp nhận chuỗi, bool hay số thực; tham số query số nguyên nhận chuỗi chữ số.

| Trường | Quy tắc |
|---|---|
| Họ tên/người nhận | 2–50 ký tự, không chỉ khoảng trắng |
| Email | Đúng dạng local@domain.tld, tối đa 100, không phân biệt hoa thường, duy nhất |
| Mật khẩu | 8–32; ít nhất một A–Z, a–z, 0–9, ký tự đặc biệt không phải khoảng trắng/chữ/số (underscore được chấp nhận) |
| Điện thoại | Đúng 10 chữ số ASCII, đầu 03/05/07/08/09 |
| Địa chỉ | 10–200 ký tự |
| Tên sản phẩm | 3–100; duy nhất trong cùng danh mục, không phân biệt hoa thường |
| Hãng/mô tả | Hãng bắt buộc 1–50; mô tả 0–1000 |
| Giá/giá nhập | Số nguyên 1.000–500.000.000 VND |
| Tồn kho | Số nguyên 0–9.999 |
| Số lượng giỏ | 1–10, cộng dồn vẫn ≤10 và ≤ tồn kho |
| Số lượng nhập | 1–1.000; tồn kho sau nhập ≤9.999 |
| Đánh giá | Điểm nguyên 1–5; bình luận 10–500 |
| Phân trang | page ≥1, page_size 1–50, mặc định 12 |
| Kho thấp | stock ≤ threshold, mặc định 5, threshold 0–9.999 |
| Ngày báo cáo | YYYY-MM-DD, ngày có thật, from ≤ to, tính cả hai đầu |

## Luồng nghiệp vụ

| Thao tác | Kết quả |
|---|---|
| Sai mật khẩu 5 lần liên tiếp | Khóa tài khoản, 403; đúng trước lần thứ 5 reset bộ đếm |
| Đặt đơn từ giỏ | Kiểm tra kho, snapshot giá/tên, xóa giỏ, chưa trừ kho |
| PENDING → CONFIRMED | Admin; kiểm tra toàn bộ dòng, trừ kho nguyên tử |
| CONFIRMED → SHIPPING → COMPLETED | Admin; không nhảy bước/đi ngược |
| Customer hủy | Chỉ đơn PENDING của chính mình |
| Admin hủy | PENDING hoặc CONFIRMED; CONFIRMED hoàn kho đúng một lần |
| Xóa sản phẩm | Xóa mềm; API công khai trả 404, đơn cũ giữ snapshot |
| Đánh giá | Một customer/sản phẩm; không yêu cầu đã mua hàng |
| Doanh thu/top sản phẩm | Chỉ đơn COMPLETED; doanh thu theo thời điểm hoàn thành UTC |

Mọi request ghi dữ liệu dùng `BEGIN IMMEDIATE`, giữ khóa ghi trước khi đọc kiểm tra nghiệp vụ. SQLite bật WAL, foreign keys, busy_timeout 30 giây. Khi xung đột nghiệp vụ trả 409, khi DB bận quá thời gian chờ trả 503. Cơ chế khóa dựa trên [giao dịch SQLite](https://www.sqlite.org/isolation.html); Waitress dùng [worker threads](https://docs.pylonsproject.org/projects/waitress/en/stable/api.html).

## Chạy kiểm thử tự động

```powershell
.\.venv\Scripts\python -X utf8 -m unittest discover -v
```

Hoặc chỉ chạy smoke test ngắn theo đề bài:

```powershell
.\.venv\Scripts\python -X utf8 -m unittest tests.test_backend.BackendTests.test_smoke_register_checkout_confirm_cancel -v
```

Test dùng DB tạm, không xóa `shop.db`. Bao phủ đăng ký → đăng nhập → giỏ → đặt đơn → xác nhận → trừ kho → hủy → hoàn kho, validation, phân quyền, báo cáo, reset, API prod, và 100 request HTTP qua Waitress. Test đồng thời xác nhận 2 đơn tranh 1 sản phẩm kiểm tra không bán quá kho.

Selenium sẽ dùng khi frontend thực tế được bổ sung. Với JMeter, thêm HTTP Cookie Manager để mỗi virtual user có session, HTTP Header Manager `Content-Type: application/json`, login trước các API bảo vệ. Request ghi SQLite được tuần tự hóa; kết quả thử 100 request không phải cam kết throughput cho mọi kịch bản.

## Cấu trúc

```text
app/                 Models, validators, auth, catalog, orders, inventory, reviews, reports
app/seed.py          Seed/reset cố định
app/api_docs.py      Hợp đồng Swagger và dữ liệu sinh tài liệu API
frontend/index.html  Placeholder
scripts/export_api.py Sinh lại docs/API.md và docs/openapi.json
tests/              Smoke, nghiệp vụ, concurrency (DB tạm)
docs/                API, BUSINESS_RULES, VERIFICATION
run.py               Waitress cổng 5000
```

## Đưa lên GitHub

Repo Git mới đã được khởi tạo trên nhánh `main` và commit theo từng bước. Máy hiện không có `gh`, nên chưa tạo repo remote hoặc push. Tạo một repository **public**, trống, tên `pc-parts-shop` trên GitHub (không thêm README/gitignore/license). Sau đó chạy trong thư mục này, thay `YOUR_GITHUB_USERNAME` bằng tài khoản thật:

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/pc-parts-shop.git
git push -u origin main
```

Không commit `.venv`, `shop.db`, `.env`, mật khẩu thật hoặc token.

## Giả định đã chốt

- Đăng ký yêu cầu đủ họ tên, email, mật khẩu, điện thoại, địa chỉ; cập nhật hồ sơ/sản phẩm cho phép cập nhật từng phần.
- Tên sản phẩm đã xóa mềm vẫn chiếm khóa duy nhất trong danh mục.
- Mọi timestamp và nhóm ngày/tháng báo cáo dùng UTC; kỳ không có doanh thu không xuất hiện trong response.
- Sản phẩm bị xóa sau khi đặt đơn: admin không thể xác nhận, nhưng có thể hủy PENDING; nếu đã xác nhận vẫn chuyển trạng thái/hoàn kho được.
- Nếu admin đã nhập/điều chỉnh kho sát 9.999 làm hoàn kho vượt trần, hủy trả 409 và giữ nguyên toàn bộ; cần điều chỉnh kho trước khi hủy.
- Giỏ chứa sản phẩm đã xóa vẫn hiển thị `is_active=false` để frontend cho phép xóa; không thể cập nhật số lượng hoặc đặt hàng dòng đó.
