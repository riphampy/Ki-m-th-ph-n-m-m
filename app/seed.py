from datetime import datetime, timedelta
from functools import lru_cache
from flask import Blueprint, current_app, session
from werkzeug.security import generate_password_hash
from .models import db, User, Category, Product, CartItem, Order, OrderItem, Review, Receipt
from .core import *

bp = Blueprint("test_support", __name__, url_prefix="/api/test")
SEED_DATE = datetime(2026, 1, 1, 9)

@lru_cache(maxsize=2)
def seed_hash(value):
    return generate_password_hash(value)

CATALOG = {
    "CPU": [
        ("Intel", "Core i3-12100F"), ("Intel", "Core i3-13100F"), ("Intel", "Core i3-14100F"),
        ("Intel", "Core i5-12400F"), ("Intel", "Core i5-12500"), ("Intel", "Core i5-12600K"),
        ("Intel", "Core i5-13400F"), ("Intel", "Core i5-13500"), ("Intel", "Core i5-13600K"),
        ("Intel", "Core i5-14400F"), ("Intel", "Core i5-14600K"), ("Intel", "Core i7-12700K"),
        ("Intel", "Core i7-13700K"), ("Intel", "Core i7-14700K"), ("Intel", "Core i9-14900K"),
        ("AMD", "Ryzen 5 5500"), ("AMD", "Ryzen 5 5600"), ("AMD", "Ryzen 5 5600X"),
        ("AMD", "Ryzen 5 7500F"), ("AMD", "Ryzen 5 7600"), ("AMD", "Ryzen 7 5700X"),
        ("AMD", "Ryzen 7 5800X3D"), ("AMD", "Ryzen 7 7700"), ("AMD", "Ryzen 7 7800X3D"), ("AMD", "Ryzen 9 7950X")],
    "RAM": [(brand, model + " " + capacity) for brand, model in [
        ("Corsair", "Vengeance"), ("Kingston", "Fury Beast"), ("G.Skill", "Trident Z5"),
        ("ADATA", "XPG Lancer"), ("TeamGroup", "T-Force Delta")]
        for capacity in ["16GB DDR5-5200", "32GB DDR5-5200", "32GB DDR5-5600", "32GB DDR5-6000", "64GB DDR5-6000"]],
    "VGA": [(brand, model) for brand in ["NVIDIA", "MSI", "ASUS", "Gigabyte", "Zotac"]
        for model in ["GeForce RTX 3060 12GB", "GeForce RTX 4060 8GB", "GeForce RTX 4060 Ti 8GB", "GeForce RTX 4070 12GB", "GeForce RTX 4080 16GB"]],
    "PSU": [(brand, model + " " + watt) for brand, model in [
        ("Corsair", "RM"), ("Cooler Master", "MWE Gold"), ("MSI", "MAG"),
        ("ASUS", "TUF Gaming"), ("Gigabyte", "UD Gold")]
        for watt in ["550W", "650W", "750W", "850W", "1000W"]],
}

def add_sample_orders(count):
    products = Product.query.filter(Product.is_active.is_(True), Product.stock >= 10).order_by(Product.id).all()
    customers = User.query.filter_by(role="CUSTOMER").order_by(User.id).all()
    if not products or not customers:
        fail("count", "Cần có customer và sản phẩm đang bán có tồn kho ít nhất 10", 409)
    statuses = ["PENDING", "CONFIRMED", "SHIPPING", "COMPLETED", "CANCELLED"]
    ids = []
    for i in range(count):
        product, customer = products[i % len(products)], customers[i % len(customers)]
        status, quantity = statuses[i % 5], i % 3 + 1
        if status in ("CONFIRMED", "SHIPPING", "COMPLETED"):
            if product.stock < quantity:
                fail("stock", f"Không đủ tồn kho để seed: {product.name}", 409)
            product.stock -= quantity
        created = SEED_DATE + timedelta(days=i % 60)
        order = Order(user_id=customer.id, recipient_name=customer.name, phone=customer.phone, address=customer.address, status=status, created_at=created, completed_at=created + timedelta(days=2) if status == "COMPLETED" else None)
        order.items.append(OrderItem(product_id=product.id, product_name=product.name, unit_price=product.price, quantity=quantity))
        db.session.add(order)
        db.session.flush()
        ids.append(order.id)
    return ids

def seed_data():
    for model in (Review, Receipt, CartItem, OrderItem, Order, Product, Category, User):
        db.session.query(model).delete(synchronize_session=False)
    db.session.expire_all()
    db.session.add(User(id=1, name="Quản trị viên", email="admin@test.com", password_hash=seed_hash("Admin@123"), role="ADMIN", phone="0900000000", address="123 Nguyễn Trãi, Hà Nội"))
    for i in range(1, 4):
        db.session.add(User(id=i+1, name=f"Khách hàng {i}", email=f"customer{i}@test.com", password_hash=seed_hash("Customer@123"), role="CUSTOMER", phone=f"090000000{i}", address="123 Nguyễn Trãi, Hà Nội"))
    db.session.flush()
    for category_id, (category, products) in enumerate(CATALOG.items(), 1):
        db.session.add(Category(id=category_id, name=category))
        db.session.flush()
        for i, (brand, model) in enumerate(products):
            name = brand + " " + model
            base = {"CPU": 1800000, "RAM": 600000, "VGA": 6500000, "PSU": 800000}[category]
            step = {"CPU": 400000, "RAM": 150000, "VGA": 1000000, "PSU": 120000}[category]
            stock = [0, 1, 5][i] if i < 3 else 100 + i
            db.session.add(Product(id=(category_id-1)*25+i+1, category_id=category_id, name=name, name_key=name.casefold(), brand=brand, description=f"{category} {name}. Dữ liệu mô phỏng phục vụ kiểm thử, giá không phải báo giá thị trường.", price=base+i*step, stock=stock, created_at=SEED_DATE))
    db.session.flush()
    add_sample_orders(10)
    for i in range(1, 4):
        db.session.add(Review(id=i, user_id=i+1, product_id=4, rating=i+2, comment="Sản phẩm hoạt động ổn định, đóng gói cẩn thận.", created_at=SEED_DATE))
    db.session.flush()

@bp.post("/reset")
def reset():
    if current_app.config["APP_ENV"] != "test":
        raise ApiError("Không tìm thấy API", 404)
    seed_data()
    session.clear()
    return ok({"users": 4, "products": 100, "orders": 10, "reviews": 3}, "Đã khôi phục dữ liệu ban đầu")

@bp.post("/seed-orders")
def seed_orders():
    if current_app.config["APP_ENV"] != "test":
        raise ApiError("Không tìm thấy API", 404)
    data = body("count")
    ids = add_sample_orders(integer(data, "count", 1, 1000))
    return ok({"count": len(ids), "order_ids": ids}, "Đã tạo đơn hàng mẫu", 201)
