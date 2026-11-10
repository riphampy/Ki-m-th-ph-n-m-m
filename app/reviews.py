from flask import Blueprint, g
from .models import db, Product, Review
from .core import *

bp = Blueprint("reviews", __name__, url_prefix="/api")

def review_values():
    data = body("rating comment")
    return dict(rating=integer(data, "rating", 1, 5), comment=string(data, "comment", 10, 500))

@bp.get("/products/<int:id>/reviews")
def reviews(id):
    get_or_404(Product, id)
    return ok(paginate(Review.query.filter_by(product_id=id).order_by(Review.created_at.desc(), Review.id.desc())))

@bp.post("/products/<int:id>/reviews")
@auth("CUSTOMER")
def create(id):
    get_or_404(Product, id)
    values = review_values()
    if Review.query.filter_by(user_id=g.user.id, product_id=id).first():
        fail("product_id", "Bạn đã đánh giá sản phẩm này", 409)
    review = Review(user_id=g.user.id, product_id=id, **values)
    db.session.add(review)
    db.session.flush()
    return ok(serialize(review), "Đã tạo đánh giá", 201)

@bp.put("/reviews/<int:id>")
@auth("CUSTOMER")
def update(id):
    review = get_or_404(Review, id)
    if review.user_id != g.user.id:
        raise ApiError("Bạn chỉ được sửa đánh giá của chính mình", 403)
    get_or_404(Product, review.product_id)
    for key, value in review_values().items():
        setattr(review, key, value)
    return ok(serialize(review))

@bp.delete("/reviews/<int:id>")
@auth()
def delete(id):
    review = get_or_404(Review, id)
    if g.user.role != "ADMIN" and review.user_id != g.user.id:
        raise ApiError("Bạn chỉ được xóa đánh giá của chính mình", 403)
    db.session.delete(review)
    return ok(message="Đã xóa đánh giá")
