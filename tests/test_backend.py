import json
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from waitress import create_server
from app import create_app
from app.models import db

SHIPPING = {"recipient_name": "Nguyễn Văn An", "phone": "0912345678", "address": "123 Nguyễn Trãi, Hà Nội"}

class BackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.app = create_app({"TESTING": True, "SECRET_KEY": "isolated-test-key", "APP_ENV": "test", "SQLALCHEMY_DATABASE_URI": "sqlite:///" + (Path(cls.temp.name) / "test.db").as_posix()})

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.engine.dispose()
        cls.temp.cleanup()

    def call(self, client, method, path, data=None, expected=200):
        response = client.open(path, method=method, json=data)
        self.assertEqual(response.status_code, expected, (path, response.get_json()))
        result = response.get_json()
        self.assertEqual(result["success"], expected < 400)
        return result.get("data") if expected < 400 else result

    def login(self, mail="customer1@test.com", password="Customer@123"):
        client = self.app.test_client()
        self.call(client, "POST", "/api/auth/login", {"email": mail, "password": password})
        return client

    def setUp(self):
        self.public = self.app.test_client()
        self.call(self.public, "POST", "/api/test/reset")
        self.customer = self.login()
        self.admin = self.login("admin@test.com", "Admin@123")

    def product(self, id=4):
        return self.call(self.public, "GET", f"/api/products/{id}")

    def checkout(self, client=None, product_id=4, quantity=2):
        client = client or self.customer
        self.call(client, "POST", "/api/cart/items", {"product_id": product_id, "quantity": quantity}, 201)
        return self.call(client, "POST", "/api/orders", SHIPPING, 201)

    def test_smoke_register_checkout_confirm_cancel(self):
        data = {"name": "Người kiểm thử", "email": "NEW@Test.com", "password": "Testing@123", "phone": SHIPPING["phone"], "address": SHIPPING["address"]}
        self.call(self.public, "POST", "/api/auth/register", data, 201)
        customer = self.login("new@test.com", "Testing@123")
        stock = self.product()["stock"]
        order = self.checkout(customer)
        self.assertEqual(self.product()["stock"], stock)
        self.assertEqual(self.call(customer, "GET", "/api/cart")["items"], [])
        self.call(self.admin, "PUT", f"/api/admin/orders/{order['id']}/status", {"status": "CONFIRMED"})
        self.assertEqual(self.product()["stock"], stock-2)
        self.call(self.admin, "PUT", f"/api/orders/{order['id']}/cancel")
        self.assertEqual(self.product()["stock"], stock)
        self.call(self.admin, "PUT", f"/api/orders/{order['id']}/cancel", expected=409)
        self.assertEqual(self.product()["stock"], stock)

    def test_lockout_and_unlock(self):
        for i in range(5):
            self.call(self.public, "POST", "/api/auth/login", {"email": "customer1@test.com", "password": "wrong"}, 403 if i == 4 else 401)
        self.call(self.customer, "GET", "/api/auth/me", expected=403)
        self.call(self.admin, "PUT", "/api/admin/users/2/lock", {"is_locked": False})
        self.login()
        self.call(self.admin, "PUT", "/api/admin/users/1/lock", {"is_locked": True}, 403)
        self.call(self.public, "POST", "/api/auth/login", {"email": "absent@test.com", "password": "wrong"}, 401)

    def test_profile_password_logout(self):
        self.call(self.customer, "PUT", "/api/auth/profile", {"name": "An", "phone": "0312345678"})
        self.call(self.customer, "PUT", "/api/auth/password", {"old_password": "wrong", "new_password": "Changed@123"}, 400)
        self.call(self.customer, "PUT", "/api/auth/password", {"old_password": "Customer@123", "new_password": "Customer@123"}, 400)
        self.call(self.customer, "PUT", "/api/auth/password", {"old_password": "Customer@123", "new_password": " Changed@123 "})
        self.login(password=" Changed@123 ")
        self.call(self.customer, "POST", "/api/auth/logout")
        self.call(self.customer, "GET", "/api/auth/me", expected=401)

    def test_validation_boundaries(self):
        good = {"name": "An", "email": "valid@test.com", "password": "Abcdef1!", "phone": "0312345678", "address": "1234567890"}
        for key, value in [("name", " "), ("name", "a"*51), ("email", "bad"), ("email", "a"*95+"@a.com"), ("password", "Abcd1!a"), ("password", "aB1!"+"a"*29), ("password", "abcdef1!"), ("password", "ABCDEF1!"), ("password", "Abcdefg!"), ("password", "Abcdef12"), ("phone", "0612345678"), ("phone", "03123456789"), ("address", "123456789"), ("address", "a"*201)]:
            with self.subTest(key=key, value=value):
                result = self.call(self.public, "POST", "/api/auth/register", {**good, key: value}, 400)
                self.assertIn(key, result["errors"])
        self.call(self.public, "POST", "/api/auth/register", good, 201)
        self.call(self.public, "POST", "/api/auth/register", {**good, "email": "VALID@TEST.COM"}, 409)
        self.call(self.public, "POST", "/api/auth/register", {**good, "role": "ADMIN"}, 400)
        for field, values in {"price": [999, 500000001, True, 1000.5, "1000"], "stock": [-1, 10000, False], "name": ["ab", "a"*101], "brand": ["", "x"*51], "description": ["x"*1001]}.items():
            for value in values:
                self.call(self.admin, "PUT", "/api/admin/products/4", {field: value}, 400)
        for price in (1000, 500000000):
            self.call(self.admin, "PUT", "/api/admin/products/4", {"price": price})
        for stock in (0, 9999):
            self.call(self.admin, "PUT", "/api/admin/products/4", {"stock": stock})

    def test_catalog_permissions_filters_and_soft_delete(self):
        self.call(self.public, "GET", "/api/cart", expected=401)
        self.call(self.admin, "GET", "/api/cart", expected=403)
        self.call(self.customer, "GET", "/api/admin/users", expected=403)
        self.assertEqual(self.call(self.public, "GET", "/api/products")["total"], 100)
        self.assertEqual(len(self.call(self.public, "GET", "/api/categories")), 4)
        result = self.call(self.public, "GET", "/api/products?search=INTEL&category_id=1&brand=intel&sort=price_asc")
        prices = [x["price"] for x in result["items"]]
        self.assertEqual(prices, sorted(prices))
        for query in ("page=0", "page_size=51", "min_price=20&max_price=10", "sort=bad", "category_id=9", "page=1.5"):
            self.call(self.public, "GET", "/api/products?"+query, expected=400)
        self.call(self.admin, "POST", "/api/admin/products", {"name": "INTEL CORE I5-12400F", "category_id": 1, "brand": "Intel", "price": 1000, "stock": 1}, 409)
        order = self.checkout()
        self.call(self.admin, "DELETE", "/api/admin/products/4")
        self.call(self.public, "GET", "/api/products/4", expected=404)
        self.assertEqual(self.call(self.customer, "GET", f"/api/orders/{order['id']}")["items"][0]["product_name"], "Intel Core i5-12400F")
        self.assertEqual(self.call(self.public, "GET", "/api/products")["total"], 99)

    def test_cart_limits_and_ownership(self):
        self.call(self.customer, "POST", "/api/cart/items", {"product_id": 1, "quantity": 1}, 409)
        self.call(self.customer, "POST", "/api/cart/items", {"product_id": 2, "quantity": 2}, 409)
        for quantity in (0, 11, True, "2"):
            self.call(self.customer, "POST", "/api/cart/items", {"product_id": 4, "quantity": quantity}, 400)
        cart = self.call(self.customer, "POST", "/api/cart/items", {"product_id": 4, "quantity": 10}, 201)
        id = cart["items"][0]["id"]
        self.call(self.customer, "POST", "/api/cart/items", {"product_id": 4, "quantity": 1}, 400)
        self.call(self.login("customer2@test.com"), "PUT", f"/api/cart/items/{id}", {"quantity": 1}, 404)
        self.call(self.customer, "PUT", f"/api/cart/items/{id}", {"quantity": 1})
        self.call(self.customer, "DELETE", f"/api/cart/items/{id}")
        self.call(self.customer, "POST", "/api/orders", SHIPPING, 400)

    def test_atomic_confirmation_and_state_machine(self):
        stock = self.product()["stock"]
        self.call(self.customer, "POST", "/api/cart/items", {"product_id": 4, "quantity": 2}, 201)
        order = self.checkout(product_id=5)
        self.call(self.admin, "PUT", "/api/admin/products/5", {"stock": 0})
        path = f"/api/admin/orders/{order['id']}/status"
        self.call(self.admin, "PUT", path, {"status": "CONFIRMED"}, 409)
        self.assertEqual(self.product()["stock"], stock)
        self.assertEqual(self.call(self.customer, "GET", f"/api/orders/{order['id']}")["status"], "PENDING")
        self.call(self.admin, "PUT", path, {"status": "SHIPPING"}, 409)
        self.call(self.admin, "PUT", "/api/admin/products/5", {"stock": 10})
        self.call(self.admin, "PUT", path, {"status": "CONFIRMED"})
        self.call(self.customer, "PUT", f"/api/orders/{order['id']}/cancel", expected=409)
        self.call(self.login("customer2@test.com"), "GET", f"/api/orders/{order['id']}", expected=404)
        self.call(self.admin, "PUT", path, {"status": "SHIPPING"})
        self.call(self.admin, "PUT", f"/api/orders/{order['id']}/cancel", expected=409)
        self.call(self.admin, "PUT", path, {"status": "COMPLETED"})
        self.call(self.admin, "PUT", path, {"status": "SHIPPING"}, 409)
        self.call(self.admin, "PUT", path, {"status": []}, 400)

    def test_receipts_and_reviews(self):
        stock = self.product()["stock"]
        self.call(self.admin, "POST", "/api/admin/receipts", {"product_id": 4, "quantity": 1000, "unit_cost": 1000}, 201)
        self.assertEqual(self.product()["stock"], stock+1000)
        self.call(self.admin, "POST", "/api/admin/receipts", {"product_id": 4, "quantity": 1001, "unit_cost": 1000}, 400)
        self.call(self.admin, "PUT", "/api/admin/products/4", {"stock": 9999})
        self.call(self.admin, "POST", "/api/admin/receipts", {"product_id": 4, "quantity": 1, "unit_cost": 1000}, 409)
        self.assertEqual(self.call(self.admin, "GET", "/api/admin/receipts")["total"], 1)
        self.assertEqual(self.call(self.admin, "GET", "/api/admin/inventory/low-stock?threshold=0")["total"], 4)
        review = self.call(self.customer, "POST", "/api/products/5/reviews", {"rating": 5, "comment": "Sản phẩm rất tốt"}, 201)
        self.call(self.customer, "POST", "/api/products/5/reviews", {"rating": 4, "comment": "Sản phẩm rất tốt"}, 409)
        path = f"/api/reviews/{review['id']}"
        self.call(self.login("customer2@test.com"), "DELETE", path, expected=403)
        self.call(self.customer, "PUT", path, {"rating": 1, "comment": "Nội dung đã sửa"})
        self.assertEqual(self.product(5)["average_rating"], 1)
        self.call(self.admin, "DELETE", path)
        self.assertEqual(self.product(5)["average_rating"], 0)

    def test_reports_reset_prod_and_swagger(self):
        daily = self.call(self.admin, "GET", "/api/admin/reports/revenue?from=2026-01-01&to=2026-03-31")
        self.assertEqual(sum(x["order_count"] for x in daily), 2)
        self.assertEqual(sum(x["revenue"] for x in daily), 22800000)
        monthly = self.call(self.admin, "GET", "/api/admin/reports/revenue?from=2026-01-01&to=2026-03-31&group_by=month")
        self.assertEqual(sum(x["revenue"] for x in monthly), 22800000)
        self.assertEqual(len(self.call(self.admin, "GET", "/api/admin/reports/top-products")), 2)
        for query in ("from=2026-02-30&to=2026-03-31", "from=2026-03-31&to=2026-01-01", "from=2026-01-01", "from=2026-1-1&to=2026-03-31"):
            self.call(self.admin, "GET", "/api/admin/reports/revenue?"+query, expected=400)
        before = self.call(self.public, "GET", "/api/products?page_size=50")
        self.call(self.public, "POST", "/api/test/seed-orders", {"count": 20}, 201)
        start = time.perf_counter()
        self.call(self.public, "POST", "/api/test/reset")
        elapsed = time.perf_counter()-start
        self.assertLess(elapsed, 3)
        self.assertEqual(before, self.call(self.public, "GET", "/api/products?page_size=50"))
        self.app.config["APP_ENV"] = "prod"
        try:
            self.call(self.public, "POST", "/api/test/reset", expected=404)
            self.call(self.public, "POST", "/api/test/seed-orders", {"count": 1}, 404)
        finally:
            self.app.config["APP_ENV"] = "test"
        spec = self.public.get("/apispec_1.json").json
        operations = sum(len(verbs) for verbs in spec["paths"].values())
        expected = sum(len(rule.methods - {"HEAD", "OPTIONS"}) for rule in self.app.url_map.iter_rules() if rule.rule.startswith("/api/"))
        self.assertEqual(operations, expected)
        self.assertEqual(operations, 36)
        self.assertEqual(self.public.get("/apidocs/").status_code, 200)
        self.assertEqual(self.public.get("/").status_code, 200)
        print(f"Reset: {elapsed:.3f}s; Swagger: {operations} operations")

    def test_waitress_100_requests_and_concurrent_confirmation(self):
        order = self.checkout(quantity=1)
        self.call(self.admin, "PUT", "/api/admin/products/4", {"stock": 1})
        second = self.checkout(self.login("customer2@test.com"), quantity=1)
        cookie = self.admin.get_cookie("session").value
        server = create_server(self.app, host="127.0.0.1", port=0, threads=16)
        runner = threading.Thread(target=server.run, daemon=True)
        runner.start()
        base = "http://127.0.0.1:" + str(server.effective_port)
        def read(_):
            with urlopen(base+"/api/products?page_size=12", timeout=30) as response:
                return response.status, json.load(response)["data"]["total"]
        def confirm(id):
            request = Request(base+f"/api/admin/orders/{id}/status", data=b'{"status":"CONFIRMED"}', method="PUT", headers={"Content-Type": "application/json", "Cookie": "session="+cookie})
            try:
                with urlopen(request, timeout=30) as response:
                    return response.status
            except HTTPError as error:
                return error.code
        try:
            start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=100) as pool:
                results = list(pool.map(read, range(100)))
            self.assertTrue(all(result == (200, 100) for result in results))
            print(f"Waitress: 100 HTTP requests, 0 failures, {time.perf_counter()-start:.3f}s")
            with ThreadPoolExecutor(max_workers=20) as pool:
                statuses = list(pool.map(confirm, [order["id"], second["id"]]*10))
            self.assertEqual(statuses.count(200), 1)
            self.assertEqual(statuses.count(409), 19)
            self.assertEqual(self.product()["stock"], 0)
        finally:
            server.task_dispatcher.shutdown()
            server.close()
            runner.join(timeout=5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
