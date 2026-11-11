# Định hướng giao diện

Đối tượng: cửa hàng linh kiện PC cho bài tập kiểm thử. Công việc chính: tìm linh kiện, đặt đơn, theo dõi trạng thái và quản lý kho.

## Hệ thống thiết kế

| Vai trò | Giá trị |
|---|---|
| Nền | #F2F5F9 |
| Bề mặt | #FFFFFF |
| Chữ chính | #192E4A |
| Hành động | #245ACA |
| Nền phụ | #DCE7F7 |
| Cảnh báo kho | #A44523 |

Segoe UI cho nội dung và form; Bahnschrift cho tiêu đề, fallback Segoe UI. Cỡ chữ 13/14/16/18/23/36/44px. Căn trái, dòng nội dung tối đa khoảng 75 ký tự. Không font ngoài hoặc tài nguyên CDN.

## So sánh bố cục trước triển khai

Phương án A: bộ lọc ngang và lưới toàn chiều rộng. Gọn ở màn hình nhỏ nhưng 5 điều kiện làm hàng lọc dài và khó quan sát lỗi.

Phương án B được chọn: bộ lọc bên trái, danh sách bên phải; mobile chuyển bộ lọc lên trên. Bảng quản trị ưu tiên dữ liệu và thao tác đúng trạng thái.

```text
[Logo] [Sản phẩm / Giỏ / Đơn]           [Tài khoản]
[Chọn linh kiện cho cấu hình]          [Minh họa CPU]
[Bộ lọc]    [Tìm tên]                  [Tìm kiếm]
[Danh mục]  [Số kết quả]               [Sắp xếp]
[Hãng]      [Sản phẩm] [Sản phẩm] [Sản phẩm]
[Giá]       [Sản phẩm] [Sản phẩm] [Sản phẩm]
[Áp dụng]                  [Trước] [Trang] [Sau]
```

Đã rà lại theo brief: bỏ animation, banner quảng cáo và số liệu trang trí; chỉ dùng minh họa SVG theo danh mục CPU/RAM/VGA/PSU. Các hình là ký hiệu loại linh kiện, không phải ảnh chính xác từng model. Nút, giá, tồn kho và lỗi có thứ bậc rõ ràng. Không shadow lặp trên thẻ; góc bo vừa phải, chỉ toast có shadow để phân biệt lớp nổi.

## QA hình ảnh

Đã xem trực tiếp trang danh sách ở desktop và chiều rộng 390px; mobile đổi bộ lọc thành 2 cột, lưới sản phẩm 2 cột, header xuống dòng. Bảng dài cuộn ngang trong vùng bảng. Keyboard focus có viền rõ, dialog tập trung focus, không animation. Không có overflow ngang toàn trang ở màn hình 390px đã kiểm tra.
