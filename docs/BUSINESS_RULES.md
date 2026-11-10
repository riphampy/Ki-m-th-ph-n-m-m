# Quy tắc nghiệp vụ — cơ sở kết quả mong đợi

| Mã | Quy tắc |
|---|---|
| BR01 | Response API thành công có success=true/data/message; lỗi có success=false/message/errors. Mọi lỗi bằng tiếng Việt. |
| BR02 | 400 sai dữ liệu; 401 chưa đăng nhập/sai thông tin login; 403 sai quyền/bị khóa; 404 không tồn tại/xóa mềm; 409 xung đột nghiệp vụ. |
| BR03 | Chỉ CUSTOMER tự đăng ký; ADMIN chỉ có từ seed. Body chứa role bị từ chối 400. |
| BR04 | Email trim, chuyển chữ thường/casefold; đúng định dạng local@domain.tld, ≤100 ký tự, duy nhất không phân biệt hoa thường; trùng trả 409. |
| BR05 | Họ tên và người nhận dài 2–50 sau trim, không chỉ khoảng trắng. |
| BR06 | Mật khẩu giữ nguyên 8–32 ký tự, có chữ hoa A–Z, chữ thường a–z, chữ số ASCII, ký tự đặc biệt không phải chữ/số/khoảng trắng (underscore được chấp nhận); lưu hash Werkzeug. |
| BR07 | Điện thoại là chuỗi 10 chữ số ASCII, đầu 03/05/07/08/09; địa chỉ trim dài 10–200. |
| BR08 | Login sai email hoặc mật khẩu đều trả “Email hoặc mật khẩu không đúng”. Tài khoản tồn tại sai 5 lần liên tiếp khóa và trả 403 ở lần 5; login đúng trước khóa reset bộ đếm. |
| BR09 | Tài khoản khóa không được dùng session cũ; admin mở khóa customer reset bộ đếm. Không khóa/mở khóa ADMIN qua API. |
| BR10 | Session cookie là cơ chế xác thực; thiếu session 401; ADMIN dùng giỏ hoặc checkout 403. Logout xóa cookie session. |
| BR11 | Hồ sơ chỉ sửa name/phone/address. Đổi mật khẩu phải đúng mật khẩu cũ, mật khẩu mới hợp lệ và khác cũ. |
| BR12 | Danh mục cố định ID 1 CPU, 2 RAM, 3 VGA, 4 PSU; không có CRUD danh mục. |
| BR13 | Tên sản phẩm 3–100, hãng 1–50 bắt buộc, mô tả 0–1000; trim trước kiểm tra. |
| BR14 | Giá/giá nhập là số nguyên JSON từ 1000 đến 500000000 VND; không chấp nhận bool, float hoặc chuỗi. |
| BR15 | Tồn kho số nguyên 0–9999, không được âm hoặc vượt trần. |
| BR16 | Tên sản phẩm duy nhất theo casefold trong cùng danh mục, kể cả sản phẩm đã xóa mềm; trùng trả 409. |
| BR17 | Danh sách công khai chỉ gồm is_active=true; ID không tồn tại hoặc đã xóa mềm trả 404. Đơn hàng cũ giữ tên/giá snapshot. |
| BR18 | Tìm kiếm khớp một phần tên không phân biệt hoa thường; lọc category_id, brand, min_price/max_price (bao gồm biên); min_price ≤ max_price. |
| BR19 | Sort hỗ trợ price_asc, price_desc, newest (mặc định); cùng giá/thời gian thì ID giảm dần. Hãng lọc không phân biệt hoa thường. |
| BR20 | Phân trang page 1–1000000, page_size 1–50 mặc định 12. Trang vượt dữ liệu trả items rỗng và total đúng. |
| BR21 | Giỏ lưu server theo customer. Dòng gồm unit_price hiện tại, quantity, subtotal; total là tổng subtotal. Giỏ không giữ giá hoặc giữ chỗ kho. |
| BR22 | Số lượng dòng 1–10; thêm cùng sản phẩm cộng dồn, tổng ≤10 (400) và ≤ tồn kho (409 kèm tên sản phẩm). |
| BR23 | Chỉ chủ sở hữu sửa/xóa dòng giỏ; dòng người khác trả 404. DELETE /cart chỉ xóa giỏ của người gọi. |
| BR24 | Checkout yêu cầu giỏ không trống, người nhận/phone/address hợp lệ, chỉ COD. Kiểm tra mọi dòng còn bán và đủ kho. |
| BR25 | Checkout tạo PENDING, lưu giá/tên tại thời điểm đặt, xóa giỏ trong cùng giao dịch; KHÔNG trừ kho. |
| BR26 | Admin chỉ chuyển PENDING → CONFIRMED → SHIPPING → COMPLETED. Nhảy bước, lặp trạng thái hoặc đi ngược trả 409. |
| BR27 | PENDING → CONFIRMED mới trừ kho. Kiểm tra toàn bộ dòng trước thay đổi; một dòng thiếu kho/xóa mềm thì 409, đơn và mọi tồn kho giữ nguyên. |
| BR28 | Customer chỉ hủy đơn PENDING của mình; xem/hủy đơn người khác 404. |
| BR29 | Admin hủy PENDING hoặc CONFIRMED. Hủy PENDING không thay đổi kho; hủy CONFIRMED hoàn kho đúng một lần. |
| BR30 | SHIPPING/COMPLETED/CANCELLED không thể hủy. Nếu hoàn kho vượt 9999, trả 409 nguyên tử; admin cần điều chỉnh tồn trước. |
| BR31 | Customer xem đơn mình; admin xem tất cả; có lọc status và phân trang. |
| BR32 | Phiếu nhập chỉ admin tạo, quantity nguyên 1–1000, unit_cost theo BR14, note 0–1000; tăng kho ngay; vượt 9999 trả 409. |
| BR33 | Phiếu nhập bất biến: chỉ POST/GET; không có API sửa/xóa. |
| BR34 | Kho thấp gồm sản phẩm đang bán stock ≤ threshold; mặc định 5, threshold nguyên 0–9999; có phân trang. |
| BR35 | Customer đánh giá sản phẩm đang bán, không bắt buộc đã mua: rating nguyên 1–5, comment trim 10–500. |
| BR36 | Mỗi customer có tối đa một đánh giá mỗi sản phẩm; gửi trùng 409. Customer sửa/xóa của mình; admin chỉ xóa bất kỳ đánh giá. |
| BR37 | Danh sách đánh giá công khai, mới nhất trước, phân trang; chi tiết sản phẩm có average_rating làm tròn 2 chữ số, chưa có đánh giá là 0. |
| BR38 | Doanh thu chỉ tính COMPLETED, sum(unit_price snapshot × quantity), nhóm theo completed_at UTC ngày hoặc tháng. |
| BR39 | from/to bắt buộc cho doanh thu, YYYY-MM-DD hợp lệ, năm 0001–9998, from ≤ to, bao gồm hai đầu ngày; chỉ trả kỳ có doanh thu. |
| BR40 | Top 10 bán chạy tính tổng quantity của COMPLETED, giảm dần, hòa thì product_id tăng; from/to tùy chọn nhưng đi cùng nhau. |
| BR41 | Mặc định APP_ENV=test. POST reset/seed-orders không yêu cầu login; APP_ENV khác test trả 404, đặc biệt prod. |
| BR42 | Reset xóa dữ liệu nghiệp vụ, seed 4 user/100 product/10 order/3 review với ID, giá, kho, thời gian cố định; không random dữ liệu nghiệp vụ. Hash mật khẩu có salt. |
| BR43 | Seed-orders count nguyên 1–1000; thêm đơn luân phiên 5 trạng thái, dùng giá hiện tại và ngày mẫu cố định; trừ kho cho CONFIRMED/SHIPPING/COMPLETED. Thiếu kho rollback toàn bộ. |
| BR44 | Ghi dữ liệu dùng giao dịch SQLite BEGIN IMMEDIATE trước đọc kiểm tra; WAL và busy_timeout=30000ms. Request xác nhận trùng không trừ kho nhiều lần. |
| BR45 | Input JSON phải là object; trường body/query ngoài hợp đồng hoặc query lặp bị từ chối 400. Thông báo chỉ rõ trường vi phạm đầu tiên. |
| BR46 | Không mã giảm giá, thanh toán online, CRUD danh mục hoặc tự đăng ký admin. Frontend hiện là placeholder. |

## Trạng thái đơn

| Mã API | Nhãn |
|---|---|
| PENDING | Chờ xác nhận |
| CONFIRMED | Đã xác nhận |
| SHIPPING | Đang giao |
| COMPLETED | Hoàn thành |
| CANCELLED | Đã hủy |

## Dữ liệu chuẩn kiểm tra báo cáo ngay sau reset

Từ `2026-01-01` đến `2026-03-31`: có 2 đơn hoàn thành, tổng doanh thu **22.800.000 VND**. Các ngày có doanh thu là `2026-01-06` (4.200.000) và `2026-01-11` (18.600.000). Báo cáo tháng 1/2026 có cùng tổng. Dữ liệu sau seed-orders sẽ thay đổi tương ứng.
