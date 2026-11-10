"""Single API contract used by Swagger and the Markdown endpoint reference."""
import re

FIELDS = {
    "name": {"type": "string", "minLength": 2, "maxLength": 50, "example": "Nguyễn Văn An"},
    "email": {"type": "string", "format": "email", "maxLength": 100, "example": "new@test.com"},
    "password": {"type": "string", "minLength": 8, "maxLength": 32, "example": "Customer@123"},
    "old_password": {"type": "string", "example": "Customer@123"},
    "new_password": {"type": "string", "minLength": 8, "maxLength": 32, "example": "Changed@123"},
    "phone": {"type": "string", "pattern": "^0[35789][0-9]{8}$", "example": "0912345678"},
    "address": {"type": "string", "minLength": 10, "maxLength": 200, "example": "123 Nguyễn Trãi, Hà Nội"},
    "recipient_name": {"type": "string", "minLength": 2, "maxLength": 50, "example": "Nguyễn Văn An"},
    "product_id": {"type": "integer", "minimum": 1, "example": 4},
    "category_id": {"type": "integer", "minimum": 1, "maximum": 4, "example": 1},
    "brand": {"type": "string", "minLength": 1, "maxLength": 50, "example": "Intel"},
    "description": {"type": "string", "maxLength": 1000, "example": "CPU phục vụ kiểm thử"},
    "price": {"type": "integer", "minimum": 1000, "maximum": 500000000, "example": 3000000},
    "stock": {"type": "integer", "minimum": 0, "maximum": 9999, "example": 100},
    "quantity": {"type": "integer", "minimum": 1, "maximum": 10, "example": 2},
    "unit_cost": {"type": "integer", "minimum": 1000, "maximum": 500000000, "example": 2000000},
    "note": {"type": "string", "maxLength": 1000, "example": "Nhập hàng kiểm thử"},
    "rating": {"type": "integer", "minimum": 1, "maximum": 5, "example": 5},
    "comment": {"type": "string", "minLength": 10, "maxLength": 500, "example": "Sản phẩm hoạt động rất tốt"},
    "is_locked": {"type": "boolean", "example": False},
    "status": {"type": "string", "enum": ["PENDING", "CONFIRMED", "SHIPPING", "COMPLETED", "CANCELLED"], "example": "CONFIRMED"},
    "payment_method": {"type": "string", "enum": ["COD"], "default": "COD", "example": "COD"},
    "count": {"type": "integer", "minimum": 1, "maximum": 1000, "example": 20},
}
PAGING = {"page": ("integer", "Trang, từ 1", 1), "page_size": ("integer", "Số phần tử, từ 1 đến 50", 12)}
# endpoint: summary, access, body fields, required fields, query fields, response kind
CONTRACT = {
    "accounts.register": ("Đăng ký customer", "PUBLIC", "name email password phone address", "name email password phone address", {}, "user"),
    "accounts.login": ("Đăng nhập; sai 5 lần liên tiếp sẽ khóa tài khoản", "PUBLIC", "email password", "email password", {}, "user"),
    "accounts.logout": ("Đăng xuất và xóa session", "LOGIN", "", "", {}, "null"),
    "accounts.me": ("Thông tin tài khoản hiện tại", "LOGIN", "", "", {}, "user"),
    "accounts.profile": ("Cập nhật một hoặc nhiều trường hồ sơ", "LOGIN", "name phone address", "", {}, "user"),
    "accounts.change_password": ("Đổi mật khẩu, kiểm tra mật khẩu cũ và mới khác nhau", "LOGIN", "old_password new_password", "old_password new_password", {}, "null"),
    "accounts.users": ("Danh sách tài khoản", "ADMIN", "", "", PAGING, "page:user"),
    "accounts.lock": ("Khóa hoặc mở khóa customer; mở khóa reset số lần sai", "ADMIN", "is_locked", "is_locked", {}, "user"),
    "products.products": ("Tìm, lọc và sắp xếp sản phẩm đang bán", "PUBLIC", "", "", {**PAGING, "search": ("string", "Khớp một phần tên, không phân biệt hoa thường, tối đa 100 ký tự", "Intel"), "category_id": ("integer", "1 CPU, 2 RAM, 3 VGA, 4 PSU", 1), "brand": ("string", "Tên hãng, không phân biệt hoa thường", "Intel"), "min_price": ("integer", "Giá từ 0 đến 500000000", 0), "max_price": ("integer", "Giá từ 0 đến 500000000, không nhỏ hơn min_price", 500000000), "sort": ("string", "price_asc, price_desc hoặc newest", "newest")}, "page:product"),
    "products.detail": ("Chi tiết sản phẩm và điểm trung bình", "PUBLIC", "", "", {}, "product"),
    "products.categories": ("Bốn danh mục cố định", "PUBLIC", "", "", {}, "categories"),
    "products.brands": ("Hãng của các sản phẩm đang bán", "PUBLIC", "", "", {}, "brands"),
    "products.create": ("Thêm sản phẩm, tên duy nhất trong danh mục", "ADMIN", "name category_id brand description price stock", "name category_id brand price stock", {}, "product"),
    "products.update": ("Sửa một hoặc nhiều trường sản phẩm", "ADMIN", "name category_id brand description price stock", "", {}, "product"),
    "products.delete": ("Xóa mềm sản phẩm, giữ dữ liệu đơn cũ", "ADMIN", "", "", {}, "null"),
    "orders.cart": ("Giỏ hàng gồm giá hiện tại và tổng tiền", "CUSTOMER", "", "", {}, "cart"),
    "orders.add_cart": ("Thêm và cộng dồn số lượng giỏ hàng", "CUSTOMER", "product_id quantity", "product_id quantity", {}, "cart"),
    "orders.update_cart": ("Đặt số lượng mới; id là ID dòng giỏ", "CUSTOMER", "quantity", "quantity", {}, "cart"),
    "orders.delete_cart_item": ("Xóa một dòng giỏ hàng; id là ID dòng giỏ", "CUSTOMER", "", "", {}, "null"),
    "orders.clear_cart": ("Xóa toàn bộ giỏ hàng của mình", "CUSTOMER", "", "", {}, "null"),
    "orders.checkout": ("Tạo đơn COD từ giỏ, lưu giá, xóa giỏ; chưa trừ kho", "CUSTOMER", "recipient_name phone address payment_method", "recipient_name phone address", {}, "order"),
    "orders.orders": ("Customer xem đơn của mình; admin xem toàn bộ", "LOGIN", "", "", {**PAGING, "status": ("string", "PENDING, CONFIRMED, SHIPPING, COMPLETED, CANCELLED", "PENDING")}, "page:order"),
    "orders.detail": ("Chi tiết đơn; đơn người khác trả 404", "LOGIN", "", "", {}, "order"),
    "orders.transition": ("Chuyển từng bước trạng thái; CONFIRMED mới trừ kho; CANCELLED hoàn kho nếu đã xác nhận", "ADMIN", "status", "status", {}, "order"),
    "orders.cancel": ("Customer chỉ hủy PENDING của mình; admin hủy PENDING hoặc CONFIRMED", "LOGIN", "", "", {}, "order"),
    "inventory.create_receipt": ("Nhập kho ngay, số lượng 1–1000; không sửa/xóa phiếu", "ADMIN", "product_id quantity unit_cost note", "product_id quantity unit_cost", {}, "receipt"),
    "inventory.receipts": ("Danh sách phiếu nhập", "ADMIN", "", "", PAGING, "page:receipt"),
    "inventory.low_stock": ("Sản phẩm đang bán có tồn kho nhỏ hơn hoặc bằng threshold", "ADMIN", "", "", {**PAGING, "threshold": ("integer", "Ngưỡng 0–9999, mặc định 5", 5)}, "page:product"),
    "reviews.reviews": ("Đánh giá sản phẩm, mới nhất trước", "PUBLIC", "", "", PAGING, "page:review"),
    "reviews.create": ("Một đánh giá cho mỗi customer/sản phẩm, không yêu cầu mua hàng", "CUSTOMER", "rating comment", "rating comment", {}, "review"),
    "reviews.update": ("Sửa đánh giá của mình", "CUSTOMER", "rating comment", "rating comment", {}, "review"),
    "reviews.delete": ("Customer xóa đánh giá của mình; admin xóa bất kỳ", "LOGIN", "", "", {}, "null"),
    "reports.revenue": ("Doanh thu theo ngày hoàn thành UTC, gồm cả from và to; chỉ trả kỳ có doanh thu", "ADMIN", "", "", {"from": ("string", "Bắt buộc YYYY-MM-DD", "2026-01-01"), "to": ("string", "Bắt buộc YYYY-MM-DD, không trước from", "2026-03-31"), "group_by": ("string", "day hoặc month, mặc định day", "day")}, "revenue"),
    "reports.top_products": ("Top 10 theo số lượng đơn COMPLETED; from/to tùy chọn nhưng phải đi cùng nhau", "ADMIN", "", "", {"from": ("string", "YYYY-MM-DD", "2026-01-01"), "to": ("string", "YYYY-MM-DD", "2026-03-31")}, "top"),
    "test_support.reset": ("Xóa sạch và seed lại cố định; chỉ APP_ENV=test, xóa session của client gọi", "TEST", "", "", {}, "reset"),
    "test_support.seed_orders": ("Tạo 1–1000 đơn mẫu luân phiên 5 trạng thái, trừ kho cho trạng thái đã xác nhận trở đi; chỉ APP_ENV=test", "TEST", "count", "count", {}, "seed"),
}
EXAMPLES = {
    "null": None,
    "user": {"id": 2, "name": "Khách hàng 1", "email": "customer1@test.com", "phone": "0900000001", "address": "123 Nguyễn Trãi, Hà Nội", "role": "CUSTOMER", "is_locked": False, "failed_attempts": 0},
    "product": {"id": 4, "name": "Intel Core i5-12400F", "category_id": 1, "brand": "Intel", "description": "CPU phục vụ kiểm thử", "price": 3000000, "stock": 103, "is_active": True, "created_at": "2026-01-01T09:00:00", "average_rating": 4.0},
    "categories": [{"id": 1, "name": "CPU"}, {"id": 2, "name": "RAM"}, {"id": 3, "name": "VGA"}, {"id": 4, "name": "PSU"}],
    "brands": ["AMD", "ASUS", "Intel"],
    "cart": {"items": [{"id": 1, "user_id": 2, "product_id": 4, "quantity": 2, "product_name": "Intel Core i5-12400F", "unit_price": 3000000, "subtotal": 6000000, "stock": 103, "is_active": True}], "total": 6000000},
    "order": {"id": 11, "user_id": 2, "recipient_name": "Nguyễn Văn An", "phone": "0912345678", "address": "123 Nguyễn Trãi, Hà Nội", "payment_method": "COD", "status": "PENDING", "status_label": "Chờ xác nhận", "created_at": "2026-01-01T09:00:00", "completed_at": None, "items": [{"id": 11, "order_id": 11, "product_id": 4, "product_name": "Intel Core i5-12400F", "unit_price": 3000000, "quantity": 2, "subtotal": 6000000}], "total": 6000000},
    "receipt": {"id": 1, "product_id": 4, "quantity": 2, "unit_cost": 2000000, "note": "Nhập hàng kiểm thử", "created_at": "2026-01-01T09:00:00"},
    "review": {"id": 4, "user_id": 2, "product_id": 5, "rating": 5, "comment": "Sản phẩm hoạt động rất tốt", "created_at": "2026-01-01T09:00:00"},
    "revenue": [{"period": "2026-01-06", "revenue": 4200000, "order_count": 1}],
    "top": [{"product_id": 7, "product_name": "Intel Core i5-13400F", "quantity": 1, "revenue": 4200000}],
    "reset": {"users": 4, "products": 100, "orders": 10, "reviews": 3},
    "seed": {"count": 5, "order_ids": [11, 12, 13, 14, 15]},
}
CREATED = {"accounts.register", "products.create", "orders.add_cart", "orders.checkout", "inventory.create_receipt", "reviews.create", "test_support.seed_orders"}

def response_example(kind):
    if kind.startswith("page:"):
        return {"items": [EXAMPLES[kind[5:]]], "page": 1, "page_size": 12, "total": 1}
    return EXAMPLES[kind]

def build_spec(app):
    paths = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint not in CONTRACT:
            continue
        summary, access, fields, required, queries, kind = CONTRACT[rule.endpoint]
        params = [{"name": name, "in": "path", "required": True, "type": "integer", "minimum": 1, "description": "ID đối tượng trong đường dẫn"} for name in rule.arguments]
        for name, (type_, description, example) in queries.items():
            params.append({"name": name, "in": "query", "required": rule.endpoint == "reports.revenue" and name in ("from", "to"), "type": type_, "description": description, "x-example": example})
        if fields:
            properties = {name: dict(FIELDS[name]) for name in fields.split()}
            if rule.endpoint.startswith("products.") and "name" in properties:
                properties["name"].update(minLength=3, maxLength=100, example="Intel Core i5-12400F")
            if rule.endpoint == "inventory.create_receipt":
                properties["quantity"]["maximum"] = 1000
            params.append({"name": "body", "in": "body", "required": True, "schema": {"type": "object", "additionalProperties": False, "properties": properties, "required": required.split(), "example": {k: v["example"] for k, v in properties.items()}}})
        status = "201" if rule.endpoint in CREATED else "200"
        responses = {status: {"description": "Thành công", "examples": {"application/json": {"success": True, "data": response_example(kind), "message": "Thành công"}}}}
        for code, message in [(400, "Dữ liệu đầu vào vi phạm quy tắc của trường"), (401, "Bạn chưa đăng nhập hoặc email/mật khẩu không đúng"), (403, "Không đủ quyền hoặc tài khoản đã bị khóa"), (404, "Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa"), (409, "Xung đột: email/tên/đánh giá trùng, thiếu tồn kho hoặc trạng thái đơn không cho phép")]:
            responses[str(code)] = {"description": message, "examples": {"application/json": {"success": False, "message": message, "errors": {"field": "Thông báo lỗi cụ thể của trường, nếu có"}}}}
        path = re.sub(r"<int:(\w+)>", r"{\1}", rule.rule)
        paths[path] = paths.get(path, {})
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            paths[path][method.lower()] = {"summary": summary, "description": "Quyền: " + access + ". Sử dụng session cookie sau khi đăng nhập. Các thay đổi ghi dữ liệu được xử lý nguyên tử.", "tags": [rule.endpoint.split(".")[0]], "operationId": rule.endpoint.replace(".", "_"), "parameters": params, "responses": responses}
    return {"swagger": "2.0", "info": {"title": "PC Parts Shop API", "version": "1.0.0", "description": "Backend phục vụ kiểm thử. Tiền VND nguyên. Thời gian UTC. Đăng nhập qua /api/auth/login; Swagger dùng cookie cùng origin."}, "consumes": ["application/json"], "produces": ["application/json"], "paths": paths}
