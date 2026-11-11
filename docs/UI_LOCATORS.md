# UI locators — PC Parts Shop

Thuộc tính `data-testid` là hợp đồng định vị ổn định cho kiểm thử. Dùng CSS `[data-testid="login-email-input"]`. Các hậu tố `{productId}`, `{orderId}`, `{reviewId}`, `{receiptId}`, `{userId}` là ID backend, không phải vị trí dòng. `{period}` là `YYYY-MM-DD` hoặc `YYYY-MM` từ báo cáo.

Mọi trang dùng HTML riêng, render dữ liệu ngay sau fetch. Chờ `loading-indicator` ẩn và phần tử kết quả mong đợi xuất hiện; không dùng thời gian chờ cố định. Nút gửi disabled trong thời gian request. Toast không tự đóng. Form `novalidate` để không thay thế lỗi server bằng thông báo native của trình duyệt.

## Thành phần chung trên mọi trang

| data-testid | Ý nghĩa |
|---|---|
| `nav-skip-link` | Đến nội dung chính bằng bàn phím |
| `nav-brand-link` | Logo về trang chủ |
| `nav-home-link` | Danh sách sản phẩm |
| `nav-login-link` | Đăng nhập khi là khách |
| `nav-register-link` | Đăng ký khi là khách |
| `nav-cart-link` | Giỏ hàng CUSTOMER |
| `nav-orders-link` | Đơn hàng CUSTOMER |
| `nav-admin-link` | Quản trị ADMIN |
| `nav-profile-link` | Hồ sơ sau đăng nhập |
| `nav-user-name` | Tên tài khoản đang đăng nhập |
| `nav-logout-button` | Đăng xuất |
| `loading-indicator` | Trạng thái có request đang chờ |
| `toast-message` | Thông báo toàn cục; data-type=success hoặc error |
| `toast-close-button` | Đóng toast |
| `confirm-dialog` | Hộp thoại HTML xác nhận xóa/hủy/khóa |
| `confirm-dialog-message` | Nội dung xác nhận |
| `confirm-dialog-yes-button` | Đồng ý thao tác |
| `confirm-dialog-no-button` | Giữ nguyên, đóng hộp thoại |
| `access-denied-message` | Thông báo Bạn không có quyền truy cập |
| `access-denied-home-link` | Về trang chủ sau lỗi quyền |
| `{page}-page-error-message` | Lỗi cấp trang; page theo bảng dưới |
| `{page}-empty-message` | Kết quả rỗng nếu trang sử dụng vùng rỗng chung |

`{page}` lần lượt là `index`, `product`, `login`, `register`, `profile`, `cart`, `checkout`, `orders`, `order-detail`, `admin-dashboard`, `admin-products`, `admin-inventory`, `admin-orders`, `admin-users`. Phần tử có điều kiện chỉ tồn tại/hiển thị ở vai trò hoặc trạng thái tương ứng.

## Phân trang dùng chung

| data-testid | Ý nghĩa |
|---|---|
| `pagination-previous-button` | Trang trước; index, cart không dùng phân trang; orders, admin/products, admin/inventory, admin/orders, admin/users |
| `pagination-next-button` | Trang sau; index, cart không dùng phân trang; orders, admin/products, admin/inventory, admin/orders, admin/users |
| `pagination-current-page` | Trang hiện tại / tổng số trang; index, cart không dùng phân trang; orders, admin/products, admin/inventory, admin/orders, admin/users |
| `review-pagination-previous-button` | Trang trước; product: đánh giá |
| `review-pagination-next-button` | Trang sau; product: đánh giá |
| `review-pagination-current-page` | Trang hiện tại / tổng số trang; product: đánh giá |
| `low-stock-pagination-previous-button` | Trang trước; admin/index: tồn kho thấp |
| `low-stock-pagination-next-button` | Trang sau; admin/index: tồn kho thấp |
| `low-stock-pagination-current-page` | Trang hiện tại / tổng số trang; admin/index: tồn kho thấp |

## Điều hướng quản trị

| data-testid | Ý nghĩa |
|---|---|
| `admin-nav-index-link` | Tổng quan |
| `admin-nav-products-link` | Sản phẩm |
| `admin-nav-inventory-link` | Nhập kho |
| `admin-nav-orders-link` | Đơn hàng |
| `admin-nav-users-link` | Người dùng |

## index.html — Trang chủ

| data-testid | Ý nghĩa |
|---|---|
| `home-category-link-{categoryId}` | Lọc nhanh CPU=1, RAM=2, VGA=3, PSU=4 |
| `home-results-count` | Tổng số sản phẩm phù hợp |
| `home-products-results` | Vùng danh sách sản phẩm |
| `search-input` | Tên cần tìm |
| `search-button` | Tìm kiếm |
| `home-search-error` | Lỗi theo trường search |
| `home-search-error-message` | Lỗi chung tìm kiếm |
| `filter-category-select` | Lọc danh mục |
| `filter-brand-select` | Lọc hãng |
| `filter-min-price-input` | Giá tối thiểu |
| `filter-max-price-input` | Giá tối đa |
| `sort-select` | newest, price_asc, price_desc |
| `filter-apply-button` | Áp dụng bộ lọc |
| `filter-reset-button` | Xóa bộ lọc, tìm kiếm và sắp xếp |
| `filter-category-id-error` | Lỗi category_id |
| `filter-brand-error` | Lỗi brand |
| `filter-min-price-error` | Lỗi min_price |
| `filter-max-price-error` | Lỗi max_price |
| `filter-error-message` | Lỗi chung form, nguyên văn message của server |
| `product-card-{productId}` | Thẻ sản phẩm |
| `product-card-image-link-{productId}` | Minh họa, liên kết chi tiết |
| `product-card-name-{productId}` | Tên và liên kết chi tiết |
| `product-card-price-{productId}` | Giá bán |
| `product-card-stock-{productId}` | Tồn kho hoặc Hết hàng |
| `product-add-to-cart-button-{productId}` | Thêm vào giỏ; khách chuyển đăng nhập; hết hàng disabled |

## product.html?id={productId} — Chi tiết sản phẩm

| data-testid | Ý nghĩa |
|---|---|
| `product-back-link` | Về danh sách |
| `product-name-text` | Tên sản phẩm |
| `product-rating-value` | Điểm trung bình |
| `product-price-amount` | Giá bán |
| `product-stock-quantity` | Tồn kho |
| `product-description-text` | Mô tả |
| `product-reviews-results` | Danh sách đánh giá |
| `product-review-login-link` | Đăng nhập để đánh giá |
| `product-review-submit-button` | Gửi đánh giá |
| `product-add-to-cart-button-{productId}` | Thêm với số lượng đã nhập |
| `product-quantity-input` | Số lượng |
| `product-quantity-error` | Lỗi trường số lượng, nguyên văn errors của server |
| `product-error-message` | Lỗi chung form, nguyên văn message của server |
| `product-review-rating-select` | Điểm đánh giá |
| `product-review-rating-error` | Lỗi trường điểm đánh giá, nguyên văn errors của server |
| `product-review-comment-textarea` | Nội dung |
| `product-review-comment-error` | Lỗi trường nội dung, nguyên văn errors của server |
| `product-review-error-message` | Lỗi chung form, nguyên văn message của server |
| `product-review-item-{reviewId}` | Một đánh giá |
| `product-review-rating-{reviewId}` | Điểm |
| `product-review-date-{reviewId}` | Ngày đánh giá |
| `product-review-comment-{reviewId}` | Bình luận |
| `product-review-edit-button-{reviewId}` | Mở form sửa của chính mình |
| `product-review-delete-button-{reviewId}` | Xóa đánh giá của mình; admin xóa mọi đánh giá |
| `review-edit-{reviewId}-rating-select` | Điểm sửa |
| `review-edit-{reviewId}-rating-error` | Lỗi trường điểm sửa, nguyên văn errors của server |
| `review-edit-{reviewId}-comment-textarea` | Bình luận sửa |
| `review-edit-{reviewId}-comment-error` | Lỗi trường bình luận sửa, nguyên văn errors của server |
| `review-edit-{reviewId}-error-message` | Lỗi chung form, nguyên văn message của server |
| `review-edit-{reviewId}-submit-button` | Lưu đánh giá |
| `review-edit-{reviewId}-cancel-button` | Bỏ thay đổi |

## login.html — Đăng nhập

| data-testid | Ý nghĩa |
|---|---|
| `login-email-input` | Email |
| `login-email-error` | Lỗi trường email, nguyên văn errors của server |
| `login-password-input` | Mật khẩu |
| `login-password-error` | Lỗi trường mật khẩu, nguyên văn errors của server |
| `login-error-message` | Lỗi chung form, nguyên văn message của server |
| `login-submit-button` | Đăng nhập |
| `login-register-link` | Sang đăng ký |

## register.html — Đăng ký

| data-testid | Ý nghĩa |
|---|---|
| `register-name-input` | Họ tên |
| `register-name-error` | Lỗi trường họ tên, nguyên văn errors của server |
| `register-email-input` | Email |
| `register-email-error` | Lỗi trường email, nguyên văn errors của server |
| `register-password-input` | Mật khẩu |
| `register-password-error` | Lỗi trường mật khẩu, nguyên văn errors của server |
| `register-phone-input` | Điện thoại |
| `register-phone-error` | Lỗi trường điện thoại, nguyên văn errors của server |
| `register-address-textarea` | Địa chỉ |
| `register-address-error` | Lỗi trường địa chỉ, nguyên văn errors của server |
| `register-error-message` | Lỗi chung form, nguyên văn message của server |
| `register-submit-button` | Tạo tài khoản |
| `register-login-link` | Sang đăng nhập |

## profile.html — Hồ sơ và mật khẩu

| data-testid | Ý nghĩa |
|---|---|
| `profile-name-input` | Họ tên |
| `profile-name-error` | Lỗi trường họ tên, nguyên văn errors của server |
| `profile-phone-input` | Điện thoại |
| `profile-phone-error` | Lỗi trường điện thoại, nguyên văn errors của server |
| `profile-address-textarea` | Địa chỉ |
| `profile-address-error` | Lỗi trường địa chỉ, nguyên văn errors của server |
| `profile-old-password-input` | Mật khẩu cũ |
| `profile-old-password-error` | Lỗi trường mật khẩu cũ, nguyên văn errors của server |
| `profile-new-password-input` | Mật khẩu mới |
| `profile-new-password-error` | Lỗi trường mật khẩu mới, nguyên văn errors của server |
| `profile-confirm-password-input` | Nhập lại mật khẩu mới |
| `profile-confirm-password-error` | Lỗi trường nhập lại mật khẩu mới, nguyên văn errors của server |
| `profile-error-message` | Lỗi chung form, nguyên văn message của server |
| `profile-password-error-message` | Lỗi chung form, nguyên văn message của server |
| `profile-email-text` | Email chỉ đọc |
| `profile-submit-button` | Lưu hồ sơ |
| `profile-password-submit-button` | Đổi mật khẩu |

## cart.html — Giỏ hàng

| data-testid | Ý nghĩa |
|---|---|
| `cart-clear-button` | Xóa cả giỏ có xác nhận |
| `cart-total-amount` | Tổng tiền, kể cả giỏ rỗng |
| `cart-checkout-button` | Đến checkout |
| `cart-shop-link` | Chọn sản phẩm khi giỏ rỗng |
| `cart-item-row-{productId}` | Dòng giỏ |
| `cart-item-product-link-{productId}` | Tên và liên kết sản phẩm |
| `cart-item-stock-{productId}` | Kho hiện tại hoặc sản phẩm ngừng bán |
| `cart-item-price-{productId}` | Đơn giá |
| `cart-item-quantity-input-{productId}` | Số lượng chỉnh sửa |
| `cart-item-update-button-{productId}` | Gửi cập nhật số lượng |
| `cart-item-subtotal-{productId}` | Thành tiền dòng |
| `cart-item-remove-button-{productId}` | Xóa dòng có xác nhận |
| `cart-item-{productId}-quantity-error` | Lỗi số lượng |
| `cart-item-{productId}-error-message` | Lỗi chung form dòng |

## checkout.html — Đặt hàng

| data-testid | Ý nghĩa |
|---|---|
| `checkout-recipient-name-input` | Họ tên người nhận |
| `checkout-recipient-name-error` | Lỗi trường họ tên người nhận, nguyên văn errors của server |
| `checkout-phone-input` | Điện thoại |
| `checkout-phone-error` | Lỗi trường điện thoại, nguyên văn errors của server |
| `checkout-address-textarea` | Địa chỉ |
| `checkout-address-error` | Lỗi trường địa chỉ, nguyên văn errors của server |
| `checkout-error-message` | Lỗi chung form, nguyên văn message của server |
| `checkout-payment-method` | Thanh toán khi nhận hàng |
| `checkout-submit-button` | Xác nhận đặt hàng |
| `checkout-order-summary` | Tóm tắt giỏ |
| `checkout-item-{productId}` | Dòng tóm tắt |
| `checkout-item-quantity-{productId}` | Số lượng |
| `checkout-item-subtotal-{productId}` | Thành tiền |
| `checkout-total-amount` | Tổng tiền |
| `checkout-cart-link` | Chỉnh sửa giỏ |
| `checkout-shop-link` | Chọn sản phẩm khi giỏ rỗng |

## orders.html — Đơn của tôi

| data-testid | Ý nghĩa |
|---|---|
| `orders-results` | Vùng danh sách |
| `orders-shop-link` | Chọn sản phẩm khi chưa có đơn |
| `order-row-{orderId}` | Dòng đơn (dùng chung trang admin/orders) |
| `order-detail-link-{orderId}` | Mở chi tiết |
| `order-date-{orderId}` | Ngày đặt |
| `order-total-amount-{orderId}` | Tổng tiền |
| `order-status-{orderId}` | Nhãn trạng thái tiếng Việt |
| `order-cancel-button-{orderId}` | Customer hủy PENDING có xác nhận |

## order-detail.html?id={orderId} — Chi tiết đơn chung customer/admin

| data-testid | Ý nghĩa |
|---|---|
| `order-detail-back-link` | Về danh sách đúng vai trò |
| `order-detail-recipient-name` | Tên người nhận |
| `order-detail-phone-text` | Điện thoại |
| `order-detail-payment-method` | COD |
| `order-detail-address-text` | Địa chỉ |
| `order-detail-items-results` | Bảng dòng đơn |
| `order-detail-item-{productId}` | Dòng snapshot sản phẩm |
| `order-detail-price-{productId}` | Đơn giá snapshot |
| `order-detail-quantity-{productId}` | Số lượng |
| `order-detail-subtotal-{productId}` | Thành tiền |
| `order-detail-total-amount` | Tổng tiền |
| `order-status-{orderId}` | Nhãn trạng thái |
| `order-cancel-button-{orderId}` | Nút hủy dành cho customer PENDING |

## admin/index.html — Tổng quan và báo cáo

| data-testid | Ý nghĩa |
|---|---|
| `admin-report-from-input` | Từ ngày |
| `admin-report-from-error` | Lỗi trường từ ngày, nguyên văn errors của server |
| `admin-report-to-input` | Đến ngày |
| `admin-report-to-error` | Lỗi trường đến ngày, nguyên văn errors của server |
| `admin-report-group-by-select` | Nhóm ngày/tháng |
| `admin-report-group-by-error` | Lỗi trường nhóm ngày/tháng, nguyên văn errors của server |
| `admin-report-error-message` | Lỗi chung form, nguyên văn message của server |
| `admin-report-submit-button` | Xem báo cáo |
| `admin-report-total-amount` | Tổng doanh thu |
| `admin-report-revenue-results` | Bảng doanh thu |
| `admin-report-revenue-row-{period}` | Dòng kỳ |
| `admin-report-order-count-{period}` | Số đơn hoàn thành trong kỳ |
| `admin-report-revenue-amount-{period}` | Doanh thu trong kỳ |
| `admin-report-top-results` | Bảng bán chạy |
| `admin-report-top-row-{productId}` | Dòng sản phẩm bán chạy |
| `admin-report-top-quantity-{productId}` | Số lượng đã bán |
| `admin-report-top-amount-{productId}` | Doanh thu sản phẩm |
| `admin-report-top-empty-message` | Không có sản phẩm bán trong khoảng ngày |
| `admin-low-stock-threshold-input` | Ngưỡng tồn kho |
| `admin-low-stock-threshold-error` | Lỗi trường ngưỡng tồn kho, nguyên văn errors của server |
| `admin-low-stock-error-message` | Lỗi chung form, nguyên văn message của server |
| `admin-low-stock-submit-button` | Xem tồn kho thấp |
| `admin-low-stock-results` | Bảng tồn kho thấp |
| `admin-low-stock-row-{productId}` | Dòng sản phẩm |
| `admin-low-stock-quantity-{productId}` | Tồn kho |
| `admin-low-stock-empty-message` | Không có sản phẩm dưới ngưỡng |

## admin/products.html — Quản lý sản phẩm

| data-testid | Ý nghĩa |
|---|---|
| `admin-product-add-button` | Mở form thêm |
| `admin-product-search-input` | Tìm tên |
| `admin-product-search-button` | Tìm kiếm |
| `admin-product-search-error` | Lỗi search |
| `admin-product-search-error-message` | Lỗi chung tìm kiếm |
| `admin-product-row-{productId}` | Dòng sản phẩm |
| `admin-product-name-{productId}` | Tên |
| `admin-product-price-{productId}` | Giá bán |
| `admin-product-stock-{productId}` | Tồn kho |
| `admin-product-edit-button-{productId}` | Mở form sửa |
| `admin-product-delete-button-{productId}` | Xóa mềm có xác nhận |
| `admin-product-submit-button` | Lưu form thêm/sửa |
| `admin-product-cancel-button` | Đóng form |
| `admin-products-count` | Số sản phẩm |
| `admin-products-results` | Bảng sản phẩm |
| `admin-product-error-message` | Lỗi chung form, nguyên văn message của server |
| `admin-product-name-input` | Tên |
| `admin-product-name-error` | Lỗi trường tên, nguyên văn errors của server |
| `admin-product-category-id-select` | Danh mục |
| `admin-product-category-id-error` | Lỗi trường danh mục, nguyên văn errors của server |
| `admin-product-brand-input` | Hãng |
| `admin-product-brand-error` | Lỗi trường hãng, nguyên văn errors của server |
| `admin-product-price-input` | Giá |
| `admin-product-price-error` | Lỗi trường giá, nguyên văn errors của server |
| `admin-product-stock-input` | Tồn kho |
| `admin-product-stock-error` | Lỗi trường tồn kho, nguyên văn errors của server |
| `admin-product-description-textarea` | Mô tả |
| `admin-product-description-error` | Lỗi trường mô tả, nguyên văn errors của server |

## admin/inventory.html — Nhập kho

| data-testid | Ý nghĩa |
|---|---|
| `admin-inventory-product-id-select` | Sản phẩm |
| `admin-inventory-product-id-error` | Lỗi trường sản phẩm, nguyên văn errors của server |
| `admin-inventory-quantity-input` | Số lượng nhập |
| `admin-inventory-quantity-error` | Lỗi trường số lượng nhập, nguyên văn errors của server |
| `admin-inventory-unit-cost-input` | Giá nhập |
| `admin-inventory-unit-cost-error` | Lỗi trường giá nhập, nguyên văn errors của server |
| `admin-inventory-note-textarea` | Ghi chú |
| `admin-inventory-note-error` | Lỗi trường ghi chú, nguyên văn errors của server |
| `admin-inventory-error-message` | Lỗi chung form, nguyên văn message của server |
| `admin-inventory-submit-button` | Tạo phiếu nhập |
| `admin-inventory-count` | Số phiếu |
| `admin-inventory-results` | Danh sách phiếu |
| `admin-inventory-row-{receiptId}` | Dòng phiếu |
| `admin-inventory-quantity-{receiptId}` | Số lượng nhập |
| `admin-inventory-cost-{receiptId}` | Giá nhập mỗi sản phẩm |
| `admin-inventory-date-{receiptId}` | Ngày nhập |

## admin/orders.html — Quản lý đơn

| data-testid | Ý nghĩa |
|---|---|
| `admin-orders-status-select` | Lọc trạng thái |
| `admin-orders-status-error` | Lỗi trường lọc trạng thái, nguyên văn errors của server |
| `admin-orders-error-message` | Lỗi chung form, nguyên văn message của server |
| `admin-orders-filter-button` | Lọc đơn |
| `admin-orders-count` | Tổng đơn phù hợp |
| `admin-orders-results` | Danh sách đơn; row/date/total/status/detail dùng chung nhóm order-* ở orders.html |
| `admin-order-confirm-button-{orderId}` | PENDING → CONFIRMED |
| `admin-order-ship-button-{orderId}` | CONFIRMED → SHIPPING |
| `admin-order-complete-button-{orderId}` | SHIPPING → COMPLETED |
| `admin-order-cancel-button-{orderId}` | Hủy PENDING hoặc CONFIRMED có xác nhận |

Bốn nút `admin-order-*` trên cũng dùng trong order-detail.html khi ADMIN truy cập. Lỗi 409 hiển thị tại toast-message với data-type=error và vùng lỗi cấp trang; không đổi trạng thái hiển thị khi request thất bại.

## admin/users.html — Người dùng

| data-testid | Ý nghĩa |
|---|---|
| `admin-users-count` | Tổng tài khoản |
| `admin-users-results` | Bảng tài khoản |
| `admin-user-row-{userId}` | Dòng tài khoản |
| `admin-user-name-{userId}` | Tên người dùng |
| `admin-user-status-{userId}` | Đang hoạt động hoặc Đã khóa |
| `admin-user-lock-button-{userId}` | Khóa customer, có xác nhận |
| `admin-user-unlock-button-{userId}` | Mở khóa customer |

## Quy ước bổ sung

- Lỗi từng trường nằm ngay dưới ô nhập, liên kết bằng aria-describedby và aria-invalid. Các input sinh từ tên API có dấu gạch dưới được đổi sang kebab-case (recipient_name → recipient-name).
- Mật khẩu nhập lại là trường chỉ có frontend. Nếu không khớp, profile-confirm-password-error hiển thị “Mật khẩu nhập lại không khớp với mật khẩu mới.”; các lỗi khác nguyên văn từ server.
- Đăng nhập thành công: CUSTOMER về index.html, ADMIN về admin/index.html. Đăng ký thành công: về login.html. Checkout thành công: về order-detail.html?id={orderId}.
- Ngày giờ hiển thị dd/MM/yyyy HH:mm theo Asia/Ho_Chi_Minh. Ngày lọc báo cáo theo UTC đúng hợp đồng backend.
- Không dùng alert/confirm/prompt native; Escape trong confirm-dialog tương đương nút Giữ nguyên.
- Không có test Selenium dựng sẵn. Tài liệu này là căn cứ để sinh viên tự viết test.
