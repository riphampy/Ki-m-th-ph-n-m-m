from flask import Blueprint, request
from sqlalchemy import func
from .models import db, Product, Category, Review
from .core import *

bp = Blueprint("products", __name__, url_prefix="/api")

def product_json(product):
    data = serialize(product)
    data["average_rating"] = round(db.session.query(func.avg(Review.rating)).filter_by(product_id=product.id).scalar() or 0, 2)
    return data

@bp.get("/products")
def products():
    query = Product.query.filter_by(is_active=True)
    if "search" in request.args:
        term = string(request.args, "search", 0, 100).casefold()
        query = query.filter(Product.name_key.contains(term, autoescape=True))
    if "category_id" in request.args:
        category_id = integer(request.args, "category_id", 1, 4, query=True)
        query = query.filter_by(category_id=category_id)
    if "brand" in request.args:
        brand = string(request.args, "brand", 1, 50)
        query = query.filter(func.lower(Product.brand) == brand.lower())
    low = integer(request.args, "min_price", 0, 500000000, 0, True)
    high = integer(request.args, "max_price", 0, 500000000, 500000000, True)
    if low > high:
        fail("min_price", "Giá tối thiểu không được lớn hơn giá tối đa")
    query = query.filter(Product.price.between(low, high))
    sort = request.args.get("sort", "newest")
    sorts = {"price_asc": Product.price.asc(), "price_desc": Product.price.desc(), "newest": Product.created_at.desc()}
    if sort not in sorts:
        fail("sort", "sort chỉ nhận price_asc, price_desc hoặc newest")
    return ok(paginate(query.order_by(sorts[sort], Product.id.desc()), product_json))

@bp.get("/products/<int:id>")
def detail(id):
    return ok(product_json(get_or_404(Product, id)))

@bp.get("/categories")
def categories():
    return ok([serialize(x) for x in Category.query.order_by(Category.id)])

@bp.get("/brands")
def brands():
    return ok([x[0] for x in db.session.query(Product.brand).filter_by(is_active=True).distinct().order_by(Product.brand)])

def validate_product(data, product=None):
    if not data:
        fail("body", "Cần ít nhất một trường sản phẩm")
    values = {}
    for key, low, high in [("name", 3, 100), ("brand", 1, 50), ("description", 0, 1000)]:
        if product is None or key in data:
            values[key] = string({"description": "", **data}, key, low, high)
    for key, low, high in [("price", 1000, 500000000), ("stock", 0, 9999), ("category_id", 1, 4)]:
        if product is None or key in data:
            values[key] = integer(data, key, low, high)
    name = values.get("name", product.name if product else "")
    category = values.get("category_id", product.category_id if product else None)
    duplicate = Product.query.filter_by(name_key=name.casefold(), category_id=category).first()
    if duplicate and (not product or duplicate.id != product.id):
        fail("name", "Tên sản phẩm đã tồn tại trong danh mục này", 409)
    values["name_key"] = name.casefold()
    return values

@bp.post("/admin/products")
@auth("ADMIN")
def create():
    data = body("name brand description category_id price stock")
    product = Product(**validate_product(data))
    db.session.add(product)
    db.session.flush()
    return ok(product_json(product), "Tạo sản phẩm thành công", 201)

@bp.put("/admin/products/<int:id>")
@auth("ADMIN")
def update(id):
    product = get_or_404(Product, id)
    data = body("name brand description category_id price stock")
    for key, value in validate_product(data, product).items():
        setattr(product, key, value)
    return ok(product_json(product))

@bp.delete("/admin/products/<int:id>")
@auth("ADMIN")
def delete(id):
    get_or_404(Product, id).is_active = False
    return ok(message="Đã xóa mềm sản phẩm")
