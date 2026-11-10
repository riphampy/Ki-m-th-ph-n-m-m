from flask import Blueprint, request
from .models import db, Product, Receipt
from .core import *

bp = Blueprint("inventory", __name__, url_prefix="/api/admin")

@bp.post("/receipts")
@auth("ADMIN")
def create_receipt():
    data = body("product_id quantity unit_cost note")
    product = get_or_404(Product, integer(data, "product_id", 1, 2147483647))
    quantity = integer(data, "quantity", 1, 1000)
    unit_cost = integer(data, "unit_cost", 1000, 500000000)
    note = string({"note": "", **data}, "note", 0, 1000)
    if product.stock + quantity > 9999:
        fail("quantity", "Tồn kho sau khi nhập không được vượt quá 9.999", 409)
    product.stock += quantity
    receipt = Receipt(product_id=product.id, quantity=quantity, unit_cost=unit_cost, note=note)
    db.session.add(receipt)
    db.session.flush()
    return ok(serialize(receipt), "Tạo phiếu nhập thành công", 201)

@bp.get("/receipts")
@auth("ADMIN")
def receipts():
    return ok(paginate(Receipt.query.order_by(Receipt.created_at.desc(), Receipt.id.desc())))

@bp.get("/inventory/low-stock")
@auth("ADMIN")
def low_stock():
    threshold = integer(request.args, "threshold", 0, 9999, 5, True)
    return ok(paginate(Product.query.filter(Product.is_active.is_(True), Product.stock <= threshold).order_by(Product.stock, Product.id)))
