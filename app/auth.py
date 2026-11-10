from flask import Blueprint, g, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User
from .core import *

bp = Blueprint("accounts", __name__, url_prefix="/api")

@bp.post("/auth/register")
def register():
    data = body("name email password phone address")
    values = dict(name=string(data, "name", 2, 50), email=email(data), password_hash=generate_password_hash(password(data)), phone=phone(data), address=string(data, "address", 10, 200))
    if User.query.filter_by(email=values["email"]).first():
        fail("email", "Email đã được sử dụng", 409)
    user = User(**values)
    db.session.add(user)
    db.session.flush()
    return ok(serialize(user), "Đăng ký thành công", 201)

@bp.post("/auth/login")
def login():
    data = body("email password")
    mail = email(data)
    raw = string(data, "password", 1, 200, strip=False)
    user = User.query.filter_by(email=mail).first()
    if user and user.is_locked:
        raise ApiError("Tài khoản đã bị khóa", 403)
    if not user or not check_password_hash(user.password_hash, raw):
        if user:
            user.failed_attempts += 1
            user.is_locked = user.failed_attempts >= 5
            db.session.commit()
            if user.is_locked:
                raise ApiError("Tài khoản đã bị khóa sau 5 lần đăng nhập sai liên tiếp", 403)
        raise ApiError("Email hoặc mật khẩu không đúng", 401)
    user.failed_attempts = 0
    session.clear()
    session["user_id"] = user.id
    return ok(serialize(user), "Đăng nhập thành công")

@bp.post("/auth/logout")
@auth()
def logout():
    session.clear()
    return ok(message="Đăng xuất thành công")

@bp.get("/auth/me")
@auth()
def me():
    return ok(serialize(g.user))

@bp.put("/auth/profile")
@auth()
def profile():
    data = body("name phone address")
    if not data:
        fail("body", "Cần ít nhất một trường để cập nhật")
    for key in data:
        setattr(g.user, key, phone(data) if key == "phone" else string(data, key, 2 if key == "name" else 10, 50 if key == "name" else 200))
    return ok(serialize(g.user))

@bp.put("/auth/password")
@auth()
def change_password():
    data = body("old_password new_password")
    old = string(data, "old_password", 1, 200, strip=False)
    new = password(data, "new_password")
    if not check_password_hash(g.user.password_hash, old):
        fail("old_password", "Mật khẩu cũ không đúng")
    if check_password_hash(g.user.password_hash, new):
        fail("new_password", "Mật khẩu mới phải khác mật khẩu cũ")
    g.user.password_hash = generate_password_hash(new)
    return ok(message="Đổi mật khẩu thành công")

@bp.get("/admin/users")
@auth("ADMIN")
def users():
    return ok(paginate(User.query.order_by(User.id)))

@bp.put("/admin/users/<int:id>/lock")
@auth("ADMIN")
def lock(id):
    data = body("is_locked")
    if type(data.get("is_locked")) is not bool:
        fail("is_locked", "is_locked phải là true hoặc false")
    user = get_or_404(User, id)
    if user.role != "CUSTOMER":
        raise ApiError("Chỉ được khóa hoặc mở khóa tài khoản customer", 403)
    user.is_locked = data["is_locked"]
    if not user.is_locked:
        user.failed_attempts = 0
    return ok(serialize(user))
