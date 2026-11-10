import os
import secrets
import sqlite3
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError, OperationalError
from werkzeug.exceptions import HTTPException
from flask_swagger_ui import get_swaggerui_blueprint
from .models import db, User
from .core import ApiError, fail

ROOT = Path(__file__).resolve().parent.parent

def create_app(config=None):
    app = Flask(__name__, static_folder=None)
    app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32), APP_ENV=os.environ.get("APP_ENV", "test"), SQLALCHEMY_DATABASE_URI="sqlite:///" + (ROOT / "shop.db").as_posix(), SQLALCHEMY_TRACK_MODIFICATIONS=False, SQLALCHEMY_ENGINE_OPTIONS={"connect_args": {"timeout": 30}, "pool_size": 20, "max_overflow": 0}, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", MAX_CONTENT_LENGTH=1024*1024)
    if config:
        app.config.update(config)
    app.json.ensure_ascii = False
    db.init_app(app)
    with app.app_context():
        @event.listens_for(db.engine, "connect")
        def sqlite_settings(connection, _):
            if isinstance(connection, sqlite3.Connection):
                connection.execute("PRAGMA journal_mode=WAL")
                connection.execute("PRAGMA busy_timeout=30000")
                connection.execute("PRAGMA foreign_keys=ON")
        db.create_all()
        # Acquire the SQLite write lock before reading state used by a mutation.
        db.session.execute(text("BEGIN IMMEDIATE"))
        if not User.query.first():
            from .seed import seed_data
            seed_data()
        db.session.commit()

    from . import auth, products, orders, inventory, reviews, reports, seed
    for module in (auth, products, orders, inventory, reviews, reports, seed):
        app.register_blueprint(module.bp)

    @app.before_request
    def begin_mutation():
        from .api_docs import CONTRACT
        contract = CONTRACT.get(request.endpoint)
        if contract:
            for key in request.args:
                if key not in contract[4]:
                    fail(key, "Tham số truy vấn không được hỗ trợ: " + key)
                if len(request.args.getlist(key)) != 1:
                    fail(key, "Tham số truy vấn không được lặp lại: " + key)
        if request.path.startswith("/api/") and request.method in ("POST", "PUT", "DELETE", "PATCH"):
            db.session.execute(text("BEGIN IMMEDIATE"))

    @app.after_request
    def finish_transaction(response):
        if response.status_code < 400:
            db.session.commit()
        else:
            db.session.rollback()
        return response

    @app.errorhandler(ApiError)
    def api_error(error):
        db.session.rollback()
        return jsonify(success=False, message=error.message, errors=error.errors), error.status

    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        db.session.rollback()
        return jsonify(success=False, message="Dữ liệu bị trùng hoặc xung đột ràng buộc", errors={"database": "Kiểm tra email, tên sản phẩm hoặc đánh giá trùng"}), 409

    @app.errorhandler(OperationalError)
    def database_error(error):
        db.session.rollback()
        app.logger.exception("Database operation failed")
        return jsonify(success=False, message="Cơ sở dữ liệu đang bận, vui lòng thử lại", errors={}), 503

    @app.errorhandler(HTTPException)
    def http_error(error):
        messages = {400: "Yêu cầu không đúng cú pháp", 404: "Không tìm thấy đường dẫn", 405: "Phương thức HTTP không được hỗ trợ", 413: "Nội dung yêu cầu vượt quá 1 MB", 415: "Content-Type phải là application/json"}
        return jsonify(success=False, message=messages.get(error.code, "Không thể xử lý yêu cầu HTTP"), errors={}), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        db.session.rollback()
        app.logger.exception("Unexpected request error")
        return jsonify(success=False, message="Lỗi nội bộ máy chủ", errors={}), 500

    @app.get("/")
    def index():
        return send_from_directory(ROOT / "frontend", "index.html")

    @app.get("/<path:filename>")
    def frontend(filename):
        if filename.startswith("api/"):
            raise ApiError("Không tìm thấy API", 404)
        return send_from_directory(ROOT / "frontend", filename)

    from .api_docs import build_spec
    spec = build_spec(app)

    @app.get("/apispec_1.json")
    def api_spec():
        return jsonify(spec)

    app.register_blueprint(get_swaggerui_blueprint("/apidocs", "/apispec_1.json", config={"app_name": "PC Parts Shop", "validatorUrl": None}))
    return app
