# Requirement Analysis - Selected Requirements

Scope: REQ-01, REQ-02, REQ-03, REQ-04, REQ-09, REQ-10, REQ-14, REQ-16.

| REQ | Actor | Acceptance rule | Precondition / Input | Expected output | Risk | Open question |
|---|---|---|---|---|---|---|
| REQ-01 | User / Catalog | Chỉ sản phẩm active mới truy vấn để mua | SKU có trong Catalog; kiểm tra `active` | Trả Product nếu active; reject nếu inactive/không có | Sản phẩm ngừng kinh doanh vẫn được bán | Requirement chưa mô tả thông báo UI khi SKU inactive |
| REQ-02 | User / Cart | Quantity là số nguyên dương; cùng SKU được cộng dồn | Cart tồn tại; SKU hợp lệ; quantity đầu vào | CartLine duy nhất cho SKU và quantity là tổng; quantity không hợp lệ bị từ chối | Số lượng sai hoặc một SKU bị tách thành nhiều line | Giới hạn quantity tối đa / giới hạn tổng số lượng chưa nêu |
| REQ-03 | System / Pricing | Subtotal = tổng price × quantity, dùng Decimal | Cart có một hoặc nhiều line; giá sản phẩm là Decimal | Kết quả Decimal, không dùng float làm phép tính tiền | Sai số tiền do floating-point hoặc kiểu dữ liệu không nhất quán | Chính sách rounding cho mọi phép tính ngoài subtotal chưa nêu chi tiết |
| REQ-04 | Customer / Checkout | Chỉ customer đã đăng nhập checkout được | Cart có item; customer.authenticated true/false | Guest nhận LOGIN_REQUIRED; user đã đăng nhập được đi tiếp | Đặt hàng trái phép / tạo order không gắn với account | Requirement không nói guest có thể lưu cart hay không; ngoài scope |
| REQ-09 | System / Shipping | Inner: subtotal >= 500.000 miễn ship; dưới ngưỡng 30.000; outer 50.000 | Decimal subtotal và area inner/outer | Shipping fee theo khu vực/ngưỡng | Tính sai phí, total hiển thị sai | Rule áp dụng subtotal trước hay sau voucher? Instruction ghi rõ dùng subtotal trước giảm |
| REQ-10 | Customer / Payments / Checkout | COD = PENDING_COD; ONLINE chỉ PAID khi approved; declined không tạo order | Customer đăng nhập; cart hợp lệ; method và approved | COD pending; online approved paid; declined reject và không tạo order | Trạng thái payment/order sai, order tạo dù payment fail | Timeout/unknown gateway response chưa mô phỏng trong lab |
| REQ-14 | Customer / Cart | Cart rỗng không được checkout | Cart.lines rỗng | EMPTY_CART và không tạo order | Order không có dòng hàng | UI copy/notification cho cart rỗng chưa nêu |
| REQ-16 | Customer / Payments | Method ngoài COD/ONLINE bị từ chối | Customer đăng nhập; cart hợp lệ; method lạ | INVALID_PAYMENT_METHOD; không tạo order | Method lạ lọt qua và tạo trạng thái thanh toán không hợp lệ | Requirement chưa mô tả danh sách method có thể mở rộng |

Expected oracle được suy ra trực tiếp từ acceptance criteria ở Instruction/Requirement. Những điểm chưa có rule được giữ ở dạng open question, không tự đặt expected.
