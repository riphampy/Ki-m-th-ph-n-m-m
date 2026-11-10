"""Run from project root: python scripts/export_api.py (does not touch shop.db)."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app
from app.models import db
from app.api_docs import CONTRACT, build_spec

with tempfile.TemporaryDirectory() as temp:
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///" + (Path(temp)/"docs.db").as_posix()})
    spec = build_spec(app)
    with app.app_context():
        db.session.remove()
        db.engine.dispose()

(ROOT/"docs/openapi.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
lines = ["# Hợp đồng API PC Parts Shop", "", "Sinh từ `app/api_docs.py`; cập nhật bằng `python scripts/export_api.py`. Base URL: `http://localhost:5000`.", "", "## Quy ước chung", "", "- Body JSON, header `Content-Type: application/json`; xác thực bằng cookie session nhận từ POST /api/auth/login. Không JWT/CSRF.", "- PUBLIC: không cần đăng nhập; LOGIN: ADMIN hoặc CUSTOMER; TEST: công khai chỉ khi APP_ENV=test; ADMIN/CUSTOMER: đúng vai trò.", "- ID trong URL là ID đối tượng; riêng /cart/items/{id} là ID dòng giỏ, không phải product_id.", "- Tiền VND nguyên; thời gian ISO 8601 biểu diễn UTC (không có hậu tố offset).", "- Chuỗi trim hai đầu, trừ mật khẩu. Trường body/query lạ hoặc query lặp trả 400; lỗi validation trả trường đầu tiên vi phạm.", "- Phân trang: data={items: [...], page: 1, page_size: 12, total: N}. page_size tối đa 50.", "- PUT hồ sơ/sản phẩm nhận cập nhật từng phần, tối thiểu một trường; PUT đánh giá yêu cầu cả rating và comment.", "- Dùng mã trạng thái PENDING, CONFIRMED, SHIPPING, COMPLETED, CANCELLED; response đơn có status_label tiếng Việt.", "- Mã lỗi chung: 400 đầu vào; 401 thiếu login/sai login; 403 sai quyền/khóa; 404 không tồn tại; 409 trùng/thiếu kho/chuyển trạng thái sai; 405 sai HTTP method; 413 body >1MB; 503 DB bận quá 30 giây; 500 lỗi nội bộ.", "- Ví dụ dưới đây minh họa cấu trúc; ID/thời gian/giá phụ thuộc dữ liệu thực tế. Các mã lỗi chung được liệt kê cho mỗi endpoint, chỉ phát sinh khi điều kiện tương ứng tồn tại.", "", "## Danh sách endpoint", "", "| Method | Đường dẫn | Quyền | Mục đích |", "|---|---|---|---|"]
for path, methods in spec["paths"].items():
    for method, op in methods.items():
        access = op["description"].split(". ")[0].replace("Quyền: ", "")
        lines.append(f"| {method.upper()} | `{path}` | {access} | {op['summary']} |")
for path, methods in spec["paths"].items():
    for method, op in methods.items():
        lines += ["", f"## {method.upper()} {path}", "", op["summary"], "", op["description"], ""]
        for param in op["parameters"]:
            if param["in"] == "body":
                schema = param["schema"]
                lines += ["Body mẫu:", "", "```json", json.dumps(schema["example"], ensure_ascii=False, indent=2), "```", "", "Trường bắt buộc: " + (", ".join(schema.get("required", [])) or "không cố định; phải có ít nhất một trường") + ".", "", "| Trường | Kiểu và ràng buộc |", "|---|---|"]
                for key, value in schema["properties"].items():
                    constraints = {k: v for k, v in value.items() if k != "example"}
                    lines.append(f"| {key} | `{json.dumps(constraints, ensure_ascii=False)}` |")
            else:
                lines.append(f"- `{param['name']}` ({param['in']}, {param['type']}, {'bắt buộc' if param['required'] else 'tùy chọn'}): {param['description']}")
        if not op["parameters"]:
            lines.append("Không có body hoặc tham số.")
        code = "201" if "201" in op["responses"] else "200"
        lines += ["", f"Response {code}:", "", "```json", json.dumps(op["responses"][code]["examples"]["application/json"], ensure_ascii=False, indent=2), "```", "", "Mã lỗi: " + "; ".join(k + " — " + v["description"] for k, v in op["responses"].items() if int(k) >= 400) + "."]
lines += ["", "## Ví dụ lỗi theo trường", "", "```json", '{"success": false, "message": "Mật khẩu phải có ít nhất 1 chữ hoa", "errors": {"password": "Mật khẩu phải có ít nhất 1 chữ hoa"}}', "```", "", "Lỗi phân quyền hoặc không tìm thấy có thể có `errors: {}`. Chi tiết quy tắc và các tình huống biên xem [BUSINESS_RULES.md](BUSINESS_RULES.md).", ""]
(ROOT/"docs/API.md").write_text("\n".join(lines), encoding="utf-8")
print(f"Exported {sum(len(v) for v in spec['paths'].values())} operations")
