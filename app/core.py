import re
from functools import wraps
from flask import request, session, g, jsonify
from .models import db, User

class ApiError(Exception):
    def __init__(self, message, status=400, errors=None):
        self.message, self.status, self.errors = message, status, errors or {}

def fail(field, message, status=400):
    raise ApiError(message, status, {field: message})

def ok(data=None, message="Thành công", status=200):
    return jsonify(success=True, data=data, message=message), status

def body(allowed):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        fail("body", "Body phải là một đối tượng JSON")
    extra = set(data) - set(allowed.split())
    if extra:
        fail(sorted(extra)[0], "Trường không được hỗ trợ: " + sorted(extra)[0])
    return data

def string(data, key, low, high, optional=False, strip=True):
    if optional and key not in data:
        return None
    value = data.get(key)
    if not isinstance(value, str):
        fail(key, f"{key} phải là chuỗi ký tự")
    value = value.strip() if strip else value
    if not low <= len(value) <= high:
        fail(key, f"{key} phải dài từ {low} đến {high} ký tự")
    return value

def integer(data, key, low, high, default=None, query=False):
    value = data.get(key, default)
    if query and isinstance(value, str) and re.fullmatch(r"[0-9]+", value):
        value = int(value)
    if type(value) is not int or not low <= value <= high:
        fail(key, f"{key} phải là số nguyên từ {low} đến {high}")
    return value

def email(data):
    value = string(data, "email", 3, 100).casefold()
    if not re.fullmatch(r"[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+", value):
        fail("email", "Email không đúng định dạng")
    return value

def password(data, key="password"):
    value = data.get(key)
    if not isinstance(value, str) or not 8 <= len(value) <= 32:
        fail(key, "Mật khẩu phải có từ 8 đến 32 ký tự")
    for pattern, label in [(r"[A-Z]", "chữ hoa"), (r"[a-z]", "chữ thường"), (r"[0-9]", "chữ số"), (r"[^\w\s]", "ký tự đặc biệt")]:
        if not re.search(pattern, value):
            fail(key, "Mật khẩu phải có ít nhất 1 " + label)
    return value

def phone(data):
    value = data.get("phone")
    if not isinstance(value, str) or not re.fullmatch(r"0[35789][0-9]{8}", value):
        fail("phone", "Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 03, 05, 07, 08 hoặc 09")
    return value

def auth(role=None):
    def decorate(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user = db.session.get(User, session.get("user_id")) if session.get("user_id") else None
            if user is None:
                raise ApiError("Bạn chưa đăng nhập", 401)
            if user.is_locked:
                raise ApiError("Tài khoản đã bị khóa", 403)
            if role and user.role != role:
                raise ApiError("Bạn không có quyền thực hiện chức năng này", 403)
            g.user = user
            return fn(*args, **kwargs)
        return wrapped
    return decorate

def serialize(obj):
    result = {}
    for column in obj.__table__.columns:
        if column.name in ("password_hash", "name_key"):
            continue
        value = getattr(obj, column.name)
        result[column.name] = value.isoformat() if hasattr(value, "isoformat") else value
    return result

def paginate(query, serializer=serialize):
    page = integer(request.args, "page", 1, 1000000, 1, True)
    size = integer(request.args, "page_size", 1, 50, 12, True)
    total = query.order_by(None).count()
    return {"items": [serializer(x) for x in query.offset((page-1)*size).limit(size)], "page": page, "page_size": size, "total": total}

def get_or_404(model, id):
    obj = db.session.get(model, id)
    if obj is None or getattr(obj, "is_active", True) is False:
        raise ApiError("Không tìm thấy dữ liệu hoặc sản phẩm đã bị xóa", 404)
    return obj
