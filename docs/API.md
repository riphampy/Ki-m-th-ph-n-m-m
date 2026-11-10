# Hợp đồng API PC Parts Shop

Sinh từ `app/api_docs.py`; cập nhật bằng `python scripts/export_api.py`. Base URL: `http://localhost:5000`.

## Quy ước chung

- Body JSON, header `Content-Type: application/json`; xác thực bằng cookie session nhận từ POST /api/auth/login. Không JWT/CSRF.
- PUBLIC: không cần đăng nhập; LOGIN: ADMIN hoặc CUSTOMER; TEST: công khai chỉ khi APP_ENV=test; ADMIN/CUSTOMER: đúng vai trò.
- ID trong URL là ID đối tượng; riêng /cart/items/{id} là ID dòng giỏ, không phải product_id.
- Tiền VND nguyên; thời gian ISO 8601 biểu diễn UTC (không có hậu tố offset).
- Chuỗi trim hai đầu, trừ mật khẩu. Trường body/query lạ hoặc query lặp trả 400; lỗi validation trả trường đầu tiên vi phạm.
- Phân trang: data={items: [...], page: 1, page_size: 12, total: N}. page_size tối đa 50.
- PUT hồ sơ/sản phẩm nhận cập nhật từng phần, tối thiểu một trường; PUT đánh giá yêu cầu cả rating và comment.
- Dùng mã trạng thái PENDING, CONFIRMED, SHIPPING, COMPLETED, CANCELLED; response đơn có status_label tiếng Việt.
- Mã lỗi chung: 400 đầu vào; 401 thiếu login/sai login; 403 sai quyền/khóa; 404 không tồn tại; 409 trùng/thiếu kho/chuyển trạng thái sai; 405 sai HTTP method; 413 body >1MB; 503 DB bận quá 30 giây; 500 lỗi nội bộ.
- Ví dụ dưới đây minh họa cấu trúc; ID/thời gian/giá phụ thuộc dữ liệu thực tế. Các mã lỗi chung được liệt kê cho mỗi endpoint, chỉ phát sinh khi điều kiện tương ứng tồn tại.

## Danh sách endpoint

| Method | Đường dẫn | Quyền | Mục đích |
|---|---|---|---|
| POST | `/api/auth/register` | PUBLIC | Đăng ký customer |
| POST | `/api/auth/login` | PUBLIC | Đăng nhập; sai 5 lần liên tiếp sẽ khóa tài khoản |
| POST | `/api/auth/logout` | LOGIN | Đăng xuất và xóa session |
| GET | `/api/auth/me` | LOGIN | Thông tin tài khoản hiện tại |
| PUT | `/api/auth/profile` | LOGIN | Cập nhật một hoặc nhiều trường hồ sơ |
| PUT | `/api/auth/password` | LOGIN | Đổi mật khẩu, kiểm tra mật khẩu cũ và mới khác nhau |
| GET | `/api/admin/users` | ADMIN | Danh sách tài khoản |
| PUT | `/api/admin/users/{id}/lock` | ADMIN | Khóa hoặc mở khóa customer; mở khóa reset số lần sai |
| GET | `/api/products` | PUBLIC | Tìm, lọc và sắp xếp sản phẩm đang bán |
| GET | `/api/products/{id}` | PUBLIC | Chi tiết sản phẩm và điểm trung bình |
| GET | `/api/categories` | PUBLIC | Bốn danh mục cố định |
| GET | `/api/brands` | PUBLIC | Hãng của các sản phẩm đang bán |
| POST | `/api/admin/products` | ADMIN | Thêm sản phẩm, tên duy nhất trong danh mục |
| PUT | `/api/admin/products/{id}` | ADMIN | Sửa một hoặc nhiều trường sản phẩm |
| DELETE | `/api/admin/products/{id}` | ADMIN | Xóa mềm sản phẩm, giữ dữ liệu đơn cũ |
| GET | `/api/cart` | CUSTOMER | Giỏ hàng gồm giá hiện tại và tổng tiền |
| DELETE | `/api/cart` | CUSTOMER | Xóa toàn bộ giỏ hàng của mình |
| POST | `/api/cart/items` | CUSTOMER | Thêm và cộng dồn số lượng giỏ hàng |
| PUT | `/api/cart/items/{id}` | CUSTOMER | Đặt số lượng mới; id là ID dòng giỏ |
| DELETE | `/api/cart/items/{id}` | CUSTOMER | Xóa một dòng giỏ hàng; id là ID dòng giỏ |
| POST | `/api/orders` | CUSTOMER | Tạo đơn COD từ giỏ, lưu giá, xóa giỏ; chưa trừ kho |
| GET | `/api/orders` | LOGIN | Customer xem đơn của mình; admin xem toàn bộ |
| GET | `/api/orders/{id}` | LOGIN | Chi tiết đơn; đơn người khác trả 404 |
| PUT | `/api/admin/orders/{id}/status` | ADMIN | Chuyển từng bước trạng thái; CONFIRMED mới trừ kho; CANCELLED hoàn kho nếu đã xác nhận |
| PUT | `/api/orders/{id}/cancel` | LOGIN | Customer chỉ hủy PENDING của mình; admin hủy PENDING hoặc CONFIRMED |
| POST | `/api/admin/receipts` | ADMIN | Nhập kho ngay, số lượng 1–1000; không sửa/xóa phiếu |
| GET | `/api/admin/receipts` | ADMIN | Danh sách phiếu nhập |
| GET | `/api/admin/inventory/low-stock` | ADMIN | Sản phẩm đang bán có tồn kho nhỏ hơn hoặc bằng threshold |
| GET | `/api/products/{id}/reviews` | PUBLIC | Đánh giá sản phẩm, mới nhất trước |
| POST | `/api/products/{id}/reviews` | CUSTOMER | Một đánh giá cho mỗi customer/sản phẩm, không yêu cầu mua hàng |
| PUT | `/api/reviews/{id}` | CUSTOMER | Sửa đánh giá của mình |
| DELETE | `/api/reviews/{id}` | LOGIN | Customer xóa đánh giá của mình; admin xóa bất kỳ |
| GET | `/api/admin/reports/revenue` | ADMIN | Doanh thu theo ngày hoàn thành UTC, gồm cả from và to; chỉ trả kỳ có doanh thu |
| GET | `/api/admin/reports/top-products` | ADMIN | Top 10 theo số lượng đơn COMPLETED; from/to tùy chọn nhưng phải đi cùng nhau |
| POST | `/api/test/reset` | TEST | Xóa sạch và seed lại cố định; chỉ APP_ENV=test, xóa session của client gọi |
| POST | `/api/test/seed-orders` | TEST | Tạo 1–1000 đơn mẫu luân phiên 5 trạng thái, trừ kho cho trạng thái đã xác nhận trở đi; chỉ APP_ENV=test |

## POST /api/auth/register

Đăng ký customer

Quyền: PUBLIC. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Body mẫu:

```json
{
  "name": "Nguyễn Văn An",
  "email": "new@test.com",
  "password": "Customer@123",
  "phone": "0912345678",
  "address": "123 Nguyễn Trãi, Hà Nội"
}
```

Trường bắt buộc: name, email, password, phone, address.

| Trường | Kiểu và ràng buộc |
|---|---|
| name | `{"type": "string", "minLength": 2, "maxLength": 50}` |
| email | `{"type": "string", "format": "email", "maxLength": 100}` |
| password | `{"type": "string", "minLength": 8, "maxLength": 32}` |
| phone | `{"type": "string", "pattern": "^0[35789][0-9]{8}$"}` |
| address | `{"type": "string", "minLength": 10, "maxLength": 200}` |

Response 201:

```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Khách hàng 1",
    "email": "customer1@test.com",
    "phone": "0900000001",
    "address": "123 Nguyễn Trãi, Hà Nội",
    "role": "CUSTOMER",
    "is_locked": false,
    "failed_attempts": 0
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## POST /api/auth/login

Đăng nhập; sai 5 lần liên tiếp sẽ khóa tài khoản

Quyền: PUBLIC. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Body mẫu:

```json
{
  "email": "new@test.com",
  "password": "Customer@123"
}
```

Trường bắt buộc: email, password.

| Trường | Kiểu và ràng buộc |
|---|---|
| email | `{"type": "string", "format": "email", "maxLength": 100}` |
| password | `{"type": "string", "minLength": 8, "maxLength": 32}` |

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Khách hàng 1",
    "email": "customer1@test.com",
    "phone": "0900000001",
    "address": "123 Nguyễn Trãi, Hà Nội",
    "role": "CUSTOMER",
    "is_locked": false,
    "failed_attempts": 0
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## POST /api/auth/logout

Đăng xuất và xóa session

Quyền: LOGIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Không có body hoặc tham số.

Response 200:

```json
{
  "success": true,
  "data": null,
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/auth/me

Thông tin tài khoản hiện tại

Quyền: LOGIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Không có body hoặc tham số.

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Khách hàng 1",
    "email": "customer1@test.com",
    "phone": "0900000001",
    "address": "123 Nguyễn Trãi, Hà Nội",
    "role": "CUSTOMER",
    "is_locked": false,
    "failed_attempts": 0
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## PUT /api/auth/profile

Cập nhật một hoặc nhiều trường hồ sơ

Quyền: LOGIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Body mẫu:

```json
{
  "name": "Nguyễn Văn An",
  "phone": "0912345678",
  "address": "123 Nguyễn Trãi, Hà Nội"
}
```

Trường bắt buộc: không cố định; phải có ít nhất một trường.

| Trường | Kiểu và ràng buộc |
|---|---|
| name | `{"type": "string", "minLength": 2, "maxLength": 50}` |
| phone | `{"type": "string", "pattern": "^0[35789][0-9]{8}$"}` |
| address | `{"type": "string", "minLength": 10, "maxLength": 200}` |

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Khách hàng 1",
    "email": "customer1@test.com",
    "phone": "0900000001",
    "address": "123 Nguyễn Trãi, Hà Nội",
    "role": "CUSTOMER",
    "is_locked": false,
    "failed_attempts": 0
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## PUT /api/auth/password

Đổi mật khẩu, kiểm tra mật khẩu cũ và mới khác nhau

Quyền: LOGIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Body mẫu:

```json
{
  "old_password": "Customer@123",
  "new_password": "Changed@123"
}
```

Trường bắt buộc: old_password, new_password.

| Trường | Kiểu và ràng buộc |
|---|---|
| old_password | `{"type": "string"}` |
| new_password | `{"type": "string", "minLength": 8, "maxLength": 32}` |

Response 200:

```json
{
  "success": true,
  "data": null,
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/admin/users

Danh sách tài khoản

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `page` (query, integer, tùy chọn): Trang, từ 1
- `page_size` (query, integer, tùy chọn): Số phần tử, từ 1 đến 50

Response 200:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 2,
        "name": "Khách hàng 1",
        "email": "customer1@test.com",
        "phone": "0900000001",
        "address": "123 Nguyễn Trãi, Hà Nội",
        "role": "CUSTOMER",
        "is_locked": false,
        "failed_attempts": 0
      }
    ],
    "page": 1,
    "page_size": 12,
    "total": 1
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## PUT /api/admin/users/{id}/lock

Khóa hoặc mở khóa customer; mở khóa reset số lần sai

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn
Body mẫu:

```json
{
  "is_locked": false
}
```

Trường bắt buộc: is_locked.

| Trường | Kiểu và ràng buộc |
|---|---|
| is_locked | `{"type": "boolean"}` |

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Khách hàng 1",
    "email": "customer1@test.com",
    "phone": "0900000001",
    "address": "123 Nguyễn Trãi, Hà Nội",
    "role": "CUSTOMER",
    "is_locked": false,
    "failed_attempts": 0
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/products

Tìm, lọc và sắp xếp sản phẩm đang bán

Quyền: PUBLIC. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `page` (query, integer, tùy chọn): Trang, từ 1
- `page_size` (query, integer, tùy chọn): Số phần tử, từ 1 đến 50
- `search` (query, string, tùy chọn): Khớp một phần tên, không phân biệt hoa thường, tối đa 100 ký tự
- `category_id` (query, integer, tùy chọn): 1 CPU, 2 RAM, 3 VGA, 4 PSU
- `brand` (query, string, tùy chọn): Tên hãng, không phân biệt hoa thường
- `min_price` (query, integer, tùy chọn): Giá từ 0 đến 500000000
- `max_price` (query, integer, tùy chọn): Giá từ 0 đến 500000000, không nhỏ hơn min_price
- `sort` (query, string, tùy chọn): price_asc, price_desc hoặc newest

Response 200:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 4,
        "name": "Intel Core i5-12400F",
        "category_id": 1,
        "brand": "Intel",
        "description": "CPU phục vụ kiểm thử",
        "price": 3000000,
        "stock": 103,
        "is_active": true,
        "created_at": "2026-01-01T09:00:00",
        "average_rating": 4.0
      }
    ],
    "page": 1,
    "page_size": 12,
    "total": 1
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/products/{id}

Chi tiết sản phẩm và điểm trung bình

Quyền: PUBLIC. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 4,
    "name": "Intel Core i5-12400F",
    "category_id": 1,
    "brand": "Intel",
    "description": "CPU phục vụ kiểm thử",
    "price": 3000000,
    "stock": 103,
    "is_active": true,
    "created_at": "2026-01-01T09:00:00",
    "average_rating": 4.0
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/categories

Bốn danh mục cố định

Quyền: PUBLIC. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Không có body hoặc tham số.

Response 200:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "CPU"
    },
    {
      "id": 2,
      "name": "RAM"
    },
    {
      "id": 3,
      "name": "VGA"
    },
    {
      "id": 4,
      "name": "PSU"
    }
  ],
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/brands

Hãng của các sản phẩm đang bán

Quyền: PUBLIC. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Không có body hoặc tham số.

Response 200:

```json
{
  "success": true,
  "data": [
    "AMD",
    "ASUS",
    "Intel"
  ],
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## POST /api/admin/products

Thêm sản phẩm, tên duy nhất trong danh mục

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Body mẫu:

```json
{
  "name": "Intel Core i5-12400F",
  "category_id": 1,
  "brand": "Intel",
  "description": "CPU phục vụ kiểm thử",
  "price": 3000000,
  "stock": 100
}
```

Trường bắt buộc: name, category_id, brand, price, stock.

| Trường | Kiểu và ràng buộc |
|---|---|
| name | `{"type": "string", "minLength": 3, "maxLength": 100}` |
| category_id | `{"type": "integer", "minimum": 1, "maximum": 4}` |
| brand | `{"type": "string", "minLength": 1, "maxLength": 50}` |
| description | `{"type": "string", "maxLength": 1000}` |
| price | `{"type": "integer", "minimum": 1000, "maximum": 500000000}` |
| stock | `{"type": "integer", "minimum": 0, "maximum": 9999}` |

Response 201:

```json
{
  "success": true,
  "data": {
    "id": 4,
    "name": "Intel Core i5-12400F",
    "category_id": 1,
    "brand": "Intel",
    "description": "CPU phục vụ kiểm thử",
    "price": 3000000,
    "stock": 103,
    "is_active": true,
    "created_at": "2026-01-01T09:00:00",
    "average_rating": 4.0
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## PUT /api/admin/products/{id}

Sửa một hoặc nhiều trường sản phẩm

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn
Body mẫu:

```json
{
  "name": "Intel Core i5-12400F",
  "category_id": 1,
  "brand": "Intel",
  "description": "CPU phục vụ kiểm thử",
  "price": 3000000,
  "stock": 100
}
```

Trường bắt buộc: không cố định; phải có ít nhất một trường.

| Trường | Kiểu và ràng buộc |
|---|---|
| name | `{"type": "string", "minLength": 3, "maxLength": 100}` |
| category_id | `{"type": "integer", "minimum": 1, "maximum": 4}` |
| brand | `{"type": "string", "minLength": 1, "maxLength": 50}` |
| description | `{"type": "string", "maxLength": 1000}` |
| price | `{"type": "integer", "minimum": 1000, "maximum": 500000000}` |
| stock | `{"type": "integer", "minimum": 0, "maximum": 9999}` |

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 4,
    "name": "Intel Core i5-12400F",
    "category_id": 1,
    "brand": "Intel",
    "description": "CPU phục vụ kiểm thử",
    "price": 3000000,
    "stock": 103,
    "is_active": true,
    "created_at": "2026-01-01T09:00:00",
    "average_rating": 4.0
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## DELETE /api/admin/products/{id}

Xóa mềm sản phẩm, giữ dữ liệu đơn cũ

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn

Response 200:

```json
{
  "success": true,
  "data": null,
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/cart

Giỏ hàng gồm giá hiện tại và tổng tiền

Quyền: CUSTOMER. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Không có body hoặc tham số.

Response 200:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 2,
        "product_id": 4,
        "quantity": 2,
        "product_name": "Intel Core i5-12400F",
        "unit_price": 3000000,
        "subtotal": 6000000,
        "stock": 103,
        "is_active": true
      }
    ],
    "total": 6000000
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## DELETE /api/cart

Xóa toàn bộ giỏ hàng của mình

Quyền: CUSTOMER. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Không có body hoặc tham số.

Response 200:

```json
{
  "success": true,
  "data": null,
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## POST /api/cart/items

Thêm và cộng dồn số lượng giỏ hàng

Quyền: CUSTOMER. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Body mẫu:

```json
{
  "product_id": 4,
  "quantity": 2
}
```

Trường bắt buộc: product_id, quantity.

| Trường | Kiểu và ràng buộc |
|---|---|
| product_id | `{"type": "integer", "minimum": 1}` |
| quantity | `{"type": "integer", "minimum": 1, "maximum": 10}` |

Response 201:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 2,
        "product_id": 4,
        "quantity": 2,
        "product_name": "Intel Core i5-12400F",
        "unit_price": 3000000,
        "subtotal": 6000000,
        "stock": 103,
        "is_active": true
      }
    ],
    "total": 6000000
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## PUT /api/cart/items/{id}

Đặt số lượng mới; id là ID dòng giỏ

Quyền: CUSTOMER. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn
Body mẫu:

```json
{
  "quantity": 2
}
```

Trường bắt buộc: quantity.

| Trường | Kiểu và ràng buộc |
|---|---|
| quantity | `{"type": "integer", "minimum": 1, "maximum": 10}` |

Response 200:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 2,
        "product_id": 4,
        "quantity": 2,
        "product_name": "Intel Core i5-12400F",
        "unit_price": 3000000,
        "subtotal": 6000000,
        "stock": 103,
        "is_active": true
      }
    ],
    "total": 6000000
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## DELETE /api/cart/items/{id}

Xóa một dòng giỏ hàng; id là ID dòng giỏ

Quyền: CUSTOMER. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn

Response 200:

```json
{
  "success": true,
  "data": null,
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## POST /api/orders

Tạo đơn COD từ giỏ, lưu giá, xóa giỏ; chưa trừ kho

Quyền: CUSTOMER. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Body mẫu:

```json
{
  "recipient_name": "Nguyễn Văn An",
  "phone": "0912345678",
  "address": "123 Nguyễn Trãi, Hà Nội",
  "payment_method": "COD"
}
```

Trường bắt buộc: recipient_name, phone, address.

| Trường | Kiểu và ràng buộc |
|---|---|
| recipient_name | `{"type": "string", "minLength": 2, "maxLength": 50}` |
| phone | `{"type": "string", "pattern": "^0[35789][0-9]{8}$"}` |
| address | `{"type": "string", "minLength": 10, "maxLength": 200}` |
| payment_method | `{"type": "string", "enum": ["COD"], "default": "COD"}` |

Response 201:

```json
{
  "success": true,
  "data": {
    "id": 11,
    "user_id": 2,
    "recipient_name": "Nguyễn Văn An",
    "phone": "0912345678",
    "address": "123 Nguyễn Trãi, Hà Nội",
    "payment_method": "COD",
    "status": "PENDING",
    "status_label": "Chờ xác nhận",
    "created_at": "2026-01-01T09:00:00",
    "completed_at": null,
    "items": [
      {
        "id": 11,
        "order_id": 11,
        "product_id": 4,
        "product_name": "Intel Core i5-12400F",
        "unit_price": 3000000,
        "quantity": 2,
        "subtotal": 6000000
      }
    ],
    "total": 6000000
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/orders

Customer xem đơn của mình; admin xem toàn bộ

Quyền: LOGIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `page` (query, integer, tùy chọn): Trang, từ 1
- `page_size` (query, integer, tùy chọn): Số phần tử, từ 1 đến 50
- `status` (query, string, tùy chọn): PENDING, CONFIRMED, SHIPPING, COMPLETED, CANCELLED

Response 200:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 11,
        "user_id": 2,
        "recipient_name": "Nguyễn Văn An",
        "phone": "0912345678",
        "address": "123 Nguyễn Trãi, Hà Nội",
        "payment_method": "COD",
        "status": "PENDING",
        "status_label": "Chờ xác nhận",
        "created_at": "2026-01-01T09:00:00",
        "completed_at": null,
        "items": [
          {
            "id": 11,
            "order_id": 11,
            "product_id": 4,
            "product_name": "Intel Core i5-12400F",
            "unit_price": 3000000,
            "quantity": 2,
            "subtotal": 6000000
          }
        ],
        "total": 6000000
      }
    ],
    "page": 1,
    "page_size": 12,
    "total": 1
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/orders/{id}

Chi tiết đơn; đơn người khác trả 404

Quyền: LOGIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 11,
    "user_id": 2,
    "recipient_name": "Nguyễn Văn An",
    "phone": "0912345678",
    "address": "123 Nguyễn Trãi, Hà Nội",
    "payment_method": "COD",
    "status": "PENDING",
    "status_label": "Chờ xác nhận",
    "created_at": "2026-01-01T09:00:00",
    "completed_at": null,
    "items": [
      {
        "id": 11,
        "order_id": 11,
        "product_id": 4,
        "product_name": "Intel Core i5-12400F",
        "unit_price": 3000000,
        "quantity": 2,
        "subtotal": 6000000
      }
    ],
    "total": 6000000
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## PUT /api/admin/orders/{id}/status

Chuyển từng bước trạng thái; CONFIRMED mới trừ kho; CANCELLED hoàn kho nếu đã xác nhận

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn
Body mẫu:

```json
{
  "status": "CONFIRMED"
}
```

Trường bắt buộc: status.

| Trường | Kiểu và ràng buộc |
|---|---|
| status | `{"type": "string", "enum": ["PENDING", "CONFIRMED", "SHIPPING", "COMPLETED", "CANCELLED"]}` |

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 11,
    "user_id": 2,
    "recipient_name": "Nguyễn Văn An",
    "phone": "0912345678",
    "address": "123 Nguyễn Trãi, Hà Nội",
    "payment_method": "COD",
    "status": "PENDING",
    "status_label": "Chờ xác nhận",
    "created_at": "2026-01-01T09:00:00",
    "completed_at": null,
    "items": [
      {
        "id": 11,
        "order_id": 11,
        "product_id": 4,
        "product_name": "Intel Core i5-12400F",
        "unit_price": 3000000,
        "quantity": 2,
        "subtotal": 6000000
      }
    ],
    "total": 6000000
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## PUT /api/orders/{id}/cancel

Customer chỉ hủy PENDING của mình; admin hủy PENDING hoặc CONFIRMED

Quyền: LOGIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 11,
    "user_id": 2,
    "recipient_name": "Nguyễn Văn An",
    "phone": "0912345678",
    "address": "123 Nguyễn Trãi, Hà Nội",
    "payment_method": "COD",
    "status": "PENDING",
    "status_label": "Chờ xác nhận",
    "created_at": "2026-01-01T09:00:00",
    "completed_at": null,
    "items": [
      {
        "id": 11,
        "order_id": 11,
        "product_id": 4,
        "product_name": "Intel Core i5-12400F",
        "unit_price": 3000000,
        "quantity": 2,
        "subtotal": 6000000
      }
    ],
    "total": 6000000
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## POST /api/admin/receipts

Nhập kho ngay, số lượng 1–1000; không sửa/xóa phiếu

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Body mẫu:

```json
{
  "product_id": 4,
  "quantity": 2,
  "unit_cost": 2000000,
  "note": "Nhập hàng kiểm thử"
}
```

Trường bắt buộc: product_id, quantity, unit_cost.

| Trường | Kiểu và ràng buộc |
|---|---|
| product_id | `{"type": "integer", "minimum": 1}` |
| quantity | `{"type": "integer", "minimum": 1, "maximum": 1000}` |
| unit_cost | `{"type": "integer", "minimum": 1000, "maximum": 500000000}` |
| note | `{"type": "string", "maxLength": 1000}` |

Response 201:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "product_id": 4,
    "quantity": 2,
    "unit_cost": 2000000,
    "note": "Nhập hàng kiểm thử",
    "created_at": "2026-01-01T09:00:00"
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/admin/receipts

Danh sách phiếu nhập

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `page` (query, integer, tùy chọn): Trang, từ 1
- `page_size` (query, integer, tùy chọn): Số phần tử, từ 1 đến 50

Response 200:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "product_id": 4,
        "quantity": 2,
        "unit_cost": 2000000,
        "note": "Nhập hàng kiểm thử",
        "created_at": "2026-01-01T09:00:00"
      }
    ],
    "page": 1,
    "page_size": 12,
    "total": 1
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/admin/inventory/low-stock

Sản phẩm đang bán có tồn kho nhỏ hơn hoặc bằng threshold

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `page` (query, integer, tùy chọn): Trang, từ 1
- `page_size` (query, integer, tùy chọn): Số phần tử, từ 1 đến 50
- `threshold` (query, integer, tùy chọn): Ngưỡng 0–9999, mặc định 5

Response 200:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 4,
        "name": "Intel Core i5-12400F",
        "category_id": 1,
        "brand": "Intel",
        "description": "CPU phục vụ kiểm thử",
        "price": 3000000,
        "stock": 103,
        "is_active": true,
        "created_at": "2026-01-01T09:00:00",
        "average_rating": 4.0
      }
    ],
    "page": 1,
    "page_size": 12,
    "total": 1
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/products/{id}/reviews

Đánh giá sản phẩm, mới nhất trước

Quyền: PUBLIC. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn
- `page` (query, integer, tùy chọn): Trang, từ 1
- `page_size` (query, integer, tùy chọn): Số phần tử, từ 1 đến 50

Response 200:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 4,
        "user_id": 2,
        "product_id": 5,
        "rating": 5,
        "comment": "Sản phẩm hoạt động rất tốt",
        "created_at": "2026-01-01T09:00:00"
      }
    ],
    "page": 1,
    "page_size": 12,
    "total": 1
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## POST /api/products/{id}/reviews

Một đánh giá cho mỗi customer/sản phẩm, không yêu cầu mua hàng

Quyền: CUSTOMER. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn
Body mẫu:

```json
{
  "rating": 5,
  "comment": "Sản phẩm hoạt động rất tốt"
}
```

Trường bắt buộc: rating, comment.

| Trường | Kiểu và ràng buộc |
|---|---|
| rating | `{"type": "integer", "minimum": 1, "maximum": 5}` |
| comment | `{"type": "string", "minLength": 10, "maxLength": 500}` |

Response 201:

```json
{
  "success": true,
  "data": {
    "id": 4,
    "user_id": 2,
    "product_id": 5,
    "rating": 5,
    "comment": "Sản phẩm hoạt động rất tốt",
    "created_at": "2026-01-01T09:00:00"
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## PUT /api/reviews/{id}

Sửa đánh giá của mình

Quyền: CUSTOMER. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn
Body mẫu:

```json
{
  "rating": 5,
  "comment": "Sản phẩm hoạt động rất tốt"
}
```

Trường bắt buộc: rating, comment.

| Trường | Kiểu và ràng buộc |
|---|---|
| rating | `{"type": "integer", "minimum": 1, "maximum": 5}` |
| comment | `{"type": "string", "minLength": 10, "maxLength": 500}` |

Response 200:

```json
{
  "success": true,
  "data": {
    "id": 4,
    "user_id": 2,
    "product_id": 5,
    "rating": 5,
    "comment": "Sản phẩm hoạt động rất tốt",
    "created_at": "2026-01-01T09:00:00"
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## DELETE /api/reviews/{id}

Customer xóa đánh giá của mình; admin xóa bất kỳ

Quyền: LOGIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `id` (path, integer, bắt buộc): ID đối tượng trong đường dẫn

Response 200:

```json
{
  "success": true,
  "data": null,
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/admin/reports/revenue

Doanh thu theo ngày hoàn thành UTC, gồm cả from và to; chỉ trả kỳ có doanh thu

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `from` (query, string, bắt buộc): Bắt buộc YYYY-MM-DD
- `to` (query, string, bắt buộc): Bắt buộc YYYY-MM-DD, không trước from
- `group_by` (query, string, tùy chọn): day hoặc month, mặc định day

Response 200:

```json
{
  "success": true,
  "data": [
    {
      "period": "2026-01-06",
      "revenue": 4200000,
      "order_count": 1
    }
  ],
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## GET /api/admin/reports/top-products

Top 10 theo số lượng đơn COMPLETED; from/to tùy chọn nhưng phải đi cùng nhau

Quyền: ADMIN. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

- `from` (query, string, tùy chọn): YYYY-MM-DD
- `to` (query, string, tùy chọn): YYYY-MM-DD

Response 200:

```json
{
  "success": true,
  "data": [
    {
      "product_id": 7,
      "product_name": "Intel Core i5-13400F",
      "quantity": 1,
      "revenue": 4200000
    }
  ],
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## POST /api/test/reset

Xóa sạch và seed lại cố định; chỉ APP_ENV=test, xóa session của client gọi

Quyền: TEST. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Không có body hoặc tham số.

Response 200:

```json
{
  "success": true,
  "data": {
    "users": 4,
    "products": 100,
    "orders": 10,
    "reviews": 3
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## POST /api/test/seed-orders

Tạo 1–1000 đơn mẫu luân phiên 5 trạng thái, trừ kho cho trạng thái đã xác nhận trở đi; chỉ APP_ENV=test

Quyền: TEST. Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.

Body mẫu:

```json
{
  "count": 20
}
```

Trường bắt buộc: count.

| Trường | Kiểu và ràng buộc |
|---|---|
| count | `{"type": "integer", "minimum": 1, "maximum": 1000}` |

Response 201:

```json
{
  "success": true,
  "data": {
    "count": 5,
    "order_ids": [
      11,
      12,
      13,
      14,
      15
    ]
  },
  "message": "Thành công"
}
```

Mã lỗi: 400 — Dữ liệu đầu vào vi phạm quy tắc của trường; 401 — Bạn chưa đăng nhập hoặc email/mật khẩu không đúng; 403 — Không đủ quyền hoặc tài khoản đã bị khóa; 404 — Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa; 409 — Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép.

## Ví dụ lỗi theo trường

```json
{"success": false, "message": "Mật khẩu phải có ít nhất 1 chữ hoa", "errors": {"password": "Mật khẩu phải có ít nhất 1 chữ hoa"}}
```

Lỗi phân quyền hoặc không tìm thấy có thể có `errors: {}`. Chi tiết quy tắc và các tình huống biên xem [BUSINESS_RULES.md](BUSINESS_RULES.md).
