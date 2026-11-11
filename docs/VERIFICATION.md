# Biên bản kiểm tra

Ngày thực hiện: 11/11/2026 (Asia/Saigon). Môi trường Windows, Python 3.11.0.

## Kết quả

- Tạo venv hoàn toàn mới và cài `requirements.txt`: thành công. Dùng `python -X utf8 -m pip install -r requirements.txt` để pip cũ hiển thị đúng đường dẫn có dấu.
- Chạy đúng entrypoint `python run.py` từ venv mới: thành công, Waitress nghe localhost:5000.
- Gọi HTTP thực `/`, `/apidocs/`, `/apispec_1.json`, `/api/products`: đều 200.
- `python -X utf8 -m unittest discover -v`: **11/11 test methods đạt**, thời gian lần cuối 5,783 giây; mỗi method có nhiều assertion/tình huống biên.
- Smoke: đăng ký, đăng nhập, thêm giỏ, đặt đơn chưa trừ kho, admin xác nhận trừ đúng kho, admin hủy hoàn đúng kho; hủy lặp trả 409 và không hoàn lần hai.
- Validation: các biên tên/email/mật khẩu/điện thoại/địa chỉ/giá/kho/số lượng/đánh giá/giá nhập; body sai kiểu; trường lạ; query lặp.
- Phân quyền/session: chưa login 401, role sai 403, không thấy đơn/dòng giỏ người khác, khóa sau 5 lần sai, mở khóa, đổi mật khẩu và logout.
- Xác nhận đơn nhiều dòng bị thiếu một dòng: 409, không trừ một phần, trạng thái không thay đổi.
- Chuyển trạng thái không đúng luồng bị từ chối; soft delete giữ snapshot đơn cũ.
- Báo cáo seed: 2 đơn hoàn thành, tổng 22.800.000 VND; nhóm ngày/tháng đúng.
- Reset: **0,015 giây** trong lần kiểm tra cuối, dữ liệu công khai khôi phục giống trước; APP_ENV=prod trả 404 cho cả hai API test.
- Swagger có đủ **36 operations** khớp route map API; tài nguyên UI được đóng gói cục bộ bằng flask-swagger-ui.
- Waitress, ThreadPoolExecutor với 100 workers gửi 100 request danh sách sản phẩm: **100/100 HTTP 200**, tổng khoảng **0,570 giây**.
- 20 request HTTP đồng thời xác nhận hai đơn tranh một sản phẩm cuối: **1 thành công, 19 trả 409**, tồn kho cuối 0; không bán quá kho hoặc trừ trùng.
- Không theo dõi `.db`, `.env`, venv trong Git; commit trên repo mới, nhánh main.

## Phạm vi chưa kiểm tra hoặc chưa hoàn tất

- Chưa chạy Selenium/JMeter; các bài này theo đề dành cho sinh viên. Bài HTTP đồng thời trên máy này không thay thế đo tải kéo dài hoặc cam kết 100 user cho mọi workload.
- Đã chạy thực tế trên Python 3.11 Windows; chưa chạy ma trận các phiên bản Python/OS khác.
- Frontend đã hoàn tất; kết quả kiểm tra bổ sung ghi ở phần dưới.
- Chưa tạo remote/push GitHub vì máy không có `gh`. Lệnh đầy đủ sau khi tạo repo public trống có trong README; không tự đoán username.
- `APP_ENV=test` mặc định có API reset công khai và tài khoản mẫu công khai. Ứng dụng phục vụ bài kiểm thử cục bộ; `APP_ENV=prod` chỉ tắt API test.

## Quyết định triển khai

- Chuyển Flasgger sang thư viện tương đương flask-swagger-ui vì Flasgger dùng cài đặt legacy gây lỗi encoding đường dẫn tiếng Việt với pip có sẵn.
- SQLite WAL + busy_timeout 30 giây + BEGIN IMMEDIATE cho request ghi. Cơ sở: [SQLite isolation](https://www.sqlite.org/isolation.html), [Waitress API](https://docs.pylonsproject.org/projects/waitress/en/stable/api.html), [flask-swagger-ui](https://github.com/sveint/flask-swagger-ui).
- Các giả định nghiệp vụ được ghi cuối README và đánh số trong BUSINESS_RULES.md.

## Bổ sung kiểm tra frontend — 11/11/2026

- 14 trang HTML riêng, JavaScript ES modules thuần, CSS chung; không framework/build step/CDN.
- Đã thao tác trên trình duyệt thật: đăng ký sai mật khẩu hiển thị lỗi server theo trường; đăng ký thành công; login customer/admin và chuyển trang đúng vai trò.
- Tìm tên, lọc CPU, sắp xếp giá, phân trang và lỗi search dài hơn 100 ký tự; nút xóa bộ lọc làm sạch cả thông báo lỗi.
- Giỏ: thêm sản phẩm, đổi số lượng 1 → 2, tổng tiền đúng 7.360.000 ₫; checkout COD chuyển đến đơn #11; hủy bằng dialog HTML làm trạng thái đổi sang Đã hủy.
- Đánh giá: tạo, sửa điểm 5 → 4, xóa; điểm trung bình cập nhật ngay về 0 sau khi xóa đánh giá cuối.
- Customer truy cập admin/index hiển thị Bạn không có quyền truy cập.
- Admin: thêm sản phẩm #101, sửa giá, nhập kho 3 sản phẩm, khóa/mở khóa tài khoản QA; tạo đơn #12, chủ động đưa tồn kho về 0 để kiểm tra toast 409 đúng nguyên văn, khôi phục tồn rồi xác nhận → giao hàng → hoàn thành; xóa mềm sản phẩm QA.
- Báo cáo: dữ liệu seed ban đầu hiển thị 22.800.000 ₫, đổi nhóm ngày/tháng hoạt động; dữ liệu QA hoàn thành sau đó cộng thêm doanh thu tương ứng.
- Desktop và màn hình 390px: đã xem screenshot; không tràn ngang toàn trang. Tài nguyên minh họa là SVG theo danh mục.
- Kiểm tra cú pháp tất cả JS bằng node --check. Các kiểm tra DOM dùng trực tiếp trong phiên kiểm tra, không tạo bộ test Selenium.
- Chi tiết locator trong UI_LOCATORS.md, thiết kế trong FRONTEND_DESIGN.md, đường dẫn sử dụng trong README.
- Đổi mật khẩu đã có kiểm tra backend tự động; frontend đã rà hợp đồng API và so khớp hai trường mật khẩu mới, chưa thực hiện đổi mật khẩu qua trình duyệt.

- Rà DOM 14 trang: 0 phần tử tương tác thiếu data-testid, 0 ID trùng, 0 data-testid trùng trong các trạng thái đã mở; mọi locator thu được đều có trong UI_LOCATORS.md. Dữ liệu kiểm tra: ui-audit.json.
- Kiểm tra HTTP: 22 tệp frontend (14 HTML, 7 JS, 1 CSS) đều được Flask phục vụ với HTTP 200.
- Chạy lại smoke test backend sau bàn giao frontend: đạt (0,731 giây). Ảnh trang chủ lưu tại frontend-preview.jpg.
