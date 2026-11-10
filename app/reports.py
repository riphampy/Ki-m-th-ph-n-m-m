import re
from datetime import date, datetime, time, timedelta
from flask import Blueprint, request
from sqlalchemy import func
from .models import db, Order, OrderItem, Product
from .core import *

bp = Blueprint("reports", __name__, url_prefix="/api/admin/reports")

def date_range():
    values = []
    for key in ("from", "to"):
        raw = request.args.get(key, "")
        try:
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", raw):
                raise ValueError
            value = date.fromisoformat(raw)
            if value.year >= 9999:
                raise ValueError
        except ValueError:
            fail(key, f"{key} phải là ngày hợp lệ dạng YYYY-MM-DD, năm từ 0001 đến 9998")
        values.append(value)
    if values[0] > values[1]:
        fail("from", "Ngày bắt đầu không được sau ngày kết thúc")
    return datetime.combine(values[0], time.min), datetime.combine(values[1] + timedelta(days=1), time.min)

@bp.get("/revenue")
@auth("ADMIN")
def revenue():
    start, end = date_range()
    group = request.args.get("group_by", "day")
    if group not in ("day", "month"):
        fail("group_by", "group_by chỉ nhận day hoặc month")
    period = func.strftime("%Y-%m-%d" if group == "day" else "%Y-%m", Order.completed_at)
    rows = db.session.query(period.label("period"), func.sum(OrderItem.unit_price * OrderItem.quantity).label("revenue"), func.count(func.distinct(Order.id)).label("order_count")).join(OrderItem, OrderItem.order_id == Order.id).filter(Order.status == "COMPLETED", Order.completed_at >= start, Order.completed_at < end).group_by(period).order_by(period).all()
    return ok([dict(row._mapping) for row in rows])

@bp.get("/top-products")
@auth("ADMIN")
def top_products():
    query = db.session.query(OrderItem.product_id, Product.name.label("product_name"), func.sum(OrderItem.quantity).label("quantity"), func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue")).join(Order, Order.id == OrderItem.order_id).join(Product, Product.id == OrderItem.product_id).filter(Order.status == "COMPLETED")
    if "from" in request.args or "to" in request.args:
        start, end = date_range()
        query = query.filter(Order.completed_at >= start, Order.completed_at < end)
    rows = query.group_by(OrderItem.product_id, Product.name).order_by(func.sum(OrderItem.quantity).desc(), OrderItem.product_id).limit(10).all()
    return ok([dict(row._mapping) for row in rows])
