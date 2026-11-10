from flask import Blueprint, g, request
from .models import db, Product, CartItem, Order, OrderItem, now
from .core import *

bp = Blueprint("orders", __name__, url_prefix="/api")
STATUSES = {"PENDING": "Chờ xác nhận", "CONFIRMED": "Đã xác nhận", "SHIPPING": "Đang giao", "COMPLETED": "Hoàn thành", "CANCELLED": "Đã hủy"}

def cart_json():
    items = []
    for item in CartItem.query.filter_by(user_id=g.user.id).order_by(CartItem.id):
        product = db.session.get(Product, item.product_id)
        items.append({**serialize(item), "product_name": product.name, "unit_price": product.price, "subtotal": product.price * item.quantity, "stock": product.stock, "is_active": product.is_active})
    return {"items": items, "total": sum(x["subtotal"] for x in items)}

def check_quantity(product, quantity):
    if quantity > 10:
        fail("quantity", "Tổng số lượng một dòng giỏ hàng không được vượt quá 10")
    if quantity > product.stock:
        fail("quantity", f"Sản phẩm {product.name} chỉ còn {product.stock} trong kho", 409)

@bp.get("/cart")
@auth("CUSTOMER")
def cart():
    return ok(cart_json())

@bp.post("/cart/items")
@auth("CUSTOMER")
def add_cart():
    data = body("product_id quantity")
    product = get_or_404(Product, integer(data, "product_id", 1, 2147483647))
    quantity = integer(data, "quantity", 1, 10)
    item = CartItem.query.filter_by(user_id=g.user.id, product_id=product.id).first()
    quantity += item.quantity if item else 0
    check_quantity(product, quantity)
    if item:
        item.quantity = quantity
    else:
        db.session.add(CartItem(user_id=g.user.id, product_id=product.id, quantity=quantity))
    db.session.flush()
    return ok(cart_json(), "Đã thêm sản phẩm vào giỏ", 201)

@bp.put("/cart/items/<int:id>")
@auth("CUSTOMER")
def update_cart(id):
    item = CartItem.query.filter_by(id=id, user_id=g.user.id).first()
    if not item:
        raise ApiError("Không tìm thấy dòng giỏ hàng", 404)
    data = body("quantity")
    quantity = integer(data, "quantity", 1, 10)
    check_quantity(get_or_404(Product, item.product_id), quantity)
    item.quantity = quantity
    return ok(cart_json())

@bp.delete("/cart/items/<int:id>")
@auth("CUSTOMER")
def delete_cart_item(id):
    item = CartItem.query.filter_by(id=id, user_id=g.user.id).first()
    if not item:
        raise ApiError("Không tìm thấy dòng giỏ hàng", 404)
    db.session.delete(item)
    return ok(message="Đã xóa dòng giỏ hàng")

@bp.delete("/cart")
@auth("CUSTOMER")
def clear_cart():
    CartItem.query.filter_by(user_id=g.user.id).delete()
    return ok(message="Đã xóa giỏ hàng")

def order_json(order):
    items = [{**serialize(item), "subtotal": item.unit_price * item.quantity} for item in order.items]
    return {**serialize(order), "status_label": STATUSES[order.status], "items": items, "total": sum(x["subtotal"] for x in items)}

def visible_order(id):
    order = get_or_404(Order, id)
    if g.user.role == "CUSTOMER" and order.user_id != g.user.id:
        raise ApiError("Không tìm thấy đơn hàng", 404)
    return order

@bp.post("/orders")
@auth("CUSTOMER")
def checkout():
    data = body("recipient_name phone address payment_method")
    values = dict(recipient_name=string(data, "recipient_name", 2, 50), phone=phone(data), address=string(data, "address", 10, 200))
    if data.get("payment_method", "COD") != "COD":
        fail("payment_method", "Chỉ hỗ trợ thanh toán COD")
    cart = CartItem.query.filter_by(user_id=g.user.id).order_by(CartItem.id).all()
    if not cart:
        fail("cart", "Giỏ hàng đang trống")
    order = Order(user_id=g.user.id, **values)
    for item in cart:
        product = get_or_404(Product, item.product_id)
        check_quantity(product, item.quantity)
        order.items.append(OrderItem(product_id=product.id, product_name=product.name, unit_price=product.price, quantity=item.quantity))
        db.session.delete(item)
    db.session.add(order)
    db.session.flush()
    return ok(order_json(order), "Đặt hàng thành công", 201)

@bp.get("/orders")
@auth()
def orders():
    query = Order.query
    if g.user.role == "CUSTOMER":
        query = query.filter_by(user_id=g.user.id)
    if "status" in request.args:
        status = request.args["status"]
        if status not in STATUSES:
            fail("status", "Trạng thái đơn hàng không hợp lệ")
        query = query.filter_by(status=status)
    return ok(paginate(query.order_by(Order.created_at.desc(), Order.id.desc()), order_json))

@bp.get("/orders/<int:id>")
@auth()
def detail(id):
    return ok(order_json(visible_order(id)))

@bp.put("/admin/orders/<int:id>/status")
@auth("ADMIN")
def transition(id):
    data = body("status")
    target = data.get("status")
    if not isinstance(target, str) or target not in STATUSES:
        fail("status", "Trạng thái đơn hàng không hợp lệ")
    order = get_or_404(Order, id)
    if target == "CANCELLED":
        return cancel_order(order)
    next_status = {"PENDING": "CONFIRMED", "CONFIRMED": "SHIPPING", "SHIPPING": "COMPLETED"}
    if next_status.get(order.status) != target:
        fail("status", f"Không thể chuyển từ {STATUSES[order.status]} sang {STATUSES[target]}", 409)
    if target == "CONFIRMED":
        for item in order.items:
            product = db.session.get(Product, item.product_id)
            if not product.is_active or product.stock < item.quantity:
                fail("stock", f"Sản phẩm {item.product_name} đã bị xóa hoặc không đủ tồn kho", 409)
        for item in order.items:
            db.session.get(Product, item.product_id).stock -= item.quantity
    order.status = target
    if target == "COMPLETED":
        order.completed_at = now()
    return ok(order_json(order))

def cancel_order(order):
    allowed = ("PENDING", "CONFIRMED") if g.user.role == "ADMIN" else ("PENDING",)
    if order.status not in allowed:
        fail("status", f"Không được hủy đơn ở trạng thái {STATUSES[order.status]}", 409)
    if order.status == "CONFIRMED":
        for item in order.items:
            product = db.session.get(Product, item.product_id)
            if product.stock + item.quantity > 9999:
                fail("stock", f"Hoàn kho {item.product_name} sẽ vượt quá 9.999; cần điều chỉnh kho trước khi hủy", 409)
        for item in order.items:
            db.session.get(Product, item.product_id).stock += item.quantity
    order.status = "CANCELLED"
    return ok(order_json(order), "Đã hủy đơn hàng")

@bp.put("/orders/<int:id>/cancel")
@auth()
def cancel(id):
    return cancel_order(visible_order(id))
