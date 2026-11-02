# Hướng dẫn tạo GitHub repository (cho người mới)

> Mục tiêu: tạo một repository **Public** có `ecommerce_app.py`, `test_runner.py`, `test_cases.csv`, `README.md`, thư mục `reports/` và PDF report. Không cần biết Git command line.

## A. Chuẩn bị

1. Tải file ZIP của project từ ChatGPT và giải nén vào một thư mục dễ tìm, ví dụ `Desktop/STLab02_EduCommerce`.
2. Tạo tài khoản tại https://github.com/ (nếu chưa có) và đăng nhập.
3. Cài GitHub Desktop tại https://desktop.github.com/ rồi mở ứng dụng.

## B. Tạo repository bằng GitHub Desktop

1. Trong GitHub Desktop, chọn **File → New repository**.
2. Repository name nhập: `stlab02-educommerce-testing`.
3. Local path chọn thư mục cha muốn lưu (ví dụ `Desktop`). Lưu ý GitHub Desktop sẽ tạo thư mục repository riêng theo tên ở bước 2.
4. Chọn **Create repository**. Nếu GitHub Desktop tạo một thư mục rỗng mới, copy toàn bộ nội dung trong thư mục ZIP đã giải nén vào thư mục repository vừa tạo. Đảm bảo `ecommerce_app.py` nằm ngay ở thư mục gốc, không bị lồng thêm một cấp thư mục.
5. Quay lại GitHub Desktop. Danh sách file mới sẽ xuất hiện ở tab **Changes**.
6. Ở ô Summary, nhập `Initial commit - STLab02 EduCommerce testing`; chọn **Commit to main**.
7. Nhấn **Publish repository** ở phía trên. Bỏ chọn **Keep this code private** để repo là Public (chỉ public khi bạn không chứa dữ liệu cá nhân/secret). Nhấn **Publish repository**.
8. Chọn **View on GitHub**. Copy địa chỉ trang repository, ví dụ `https://github.com/<your-username>/stlab02-educommerce-testing`.
9. Mở repository trên GitHub và kiểm tra thấy `ecommerce_app.py`, `test_runner.py`, `test_cases.csv`, `README.md`, `reports/` và PDF report. Nếu thiếu thì chưa upload đầy đủ.

## C. Cập nhật PDF sau khi có link GitHub

Trong PDF hiện tại, trường GitHub URL được đánh dấu **chưa publish** vì chưa có quyền truy cập tài khoản để tạo repository. Sau khi copy được URL thật:

1. Ghi URL vào trang thông tin sinh viên trong PDF (hoặc gửi lại URL để cập nhật PDF).
2. Copy PDF cuối cùng vào repository, thư mục `report/`.
3. Mở GitHub Desktop, nhập Summary `Add final STLab02 PDF report`, chọn **Commit to main**, rồi **Push origin**.
4. Mở GitHub trên trình duyệt và kiểm tra PDF đã xuất hiện.

## D. Link repo cần nộp

Dán URL public của trang repository vào PDF và email nộp bài. Không dán link ZIP local hoặc link `sandbox:/...` vào mục GitHub URL.

## E. Lưu ý bảo mật

Không upload mật khẩu, API key, token, file `.env`, dữ liệu khách hàng hoặc thông tin thanh toán thật. Với bài mô phỏng hiện tại, dữ liệu đều là dữ liệu thử nghiệm giả lập.
