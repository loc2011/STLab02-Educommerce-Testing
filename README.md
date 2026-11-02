# STLab02 - EduCommerce Requirement-based Testing

Bộ bài thực hành môn Software Testing: đọc requirement, thiết kế test condition/scenario/test case, chạy data-driven bằng Python từ CSV và xuất báo cáo HTML/CSV.

## 1. Phạm vi

Các requirement được chọn (không trùng ba requirement mẫu trong Instruction):

- `REQ-01` Catalog - chỉ truy vấn được sản phẩm active.
- `REQ-02` Cart - quantity là số nguyên dương và cộng dồn cùng SKU.
- `REQ-03` Pricing - subtotal dùng `Decimal`.
- `REQ-04` Authentication - chỉ customer đã đăng nhập được checkout.
- `REQ-09` Shipping - phí ship theo khu vực và ngưỡng subtotal.
- `REQ-10` Payment - COD là `PENDING_COD`; ONLINE chỉ `PAID` khi approved; declined không tạo order.
- `REQ-14` Cart Integrity - cart rỗng không checkout được.
- `REQ-16` Payment Safety - từ chối payment method ngoài COD/ONLINE.

Bộ dữ liệu có 24 test case (3 case/REQ), bao gồm positive, negative và boundary. `REQ-06`, `REQ-08`, `REQ-11` không được chọn làm phạm vi chấm chính vì đã là worked example trong Instruction.

## 2. Cấu trúc repository

```text
STLab02_EduCommerce/
├── ecommerce_app.py
├── test_runner.py
├── test_cases.csv
├── traceability_matrix.csv
├── README.md
├── GITHUB_UPLOAD_GUIDE.md
├── STLab02_EduCommerce.ipynb
├── docs/
│   ├── requirement_analysis.md
│   ├── test_design_summary.md
│   ├── problem_solving.md
│   └── report_summary.md
├── report/
│   └── STLab02_Report.pdf
└── reports/
    ├── test_execution.csv
    ├── summary_by_requirement.csv
    ├── run_summary.json
    └── test_dashboard.html
```

PDF báo cáo đầy đủ được đặt trong `report/STLab02_Report.pdf` và cung cấp riêng để tải xuống.

## 3. Chạy trên máy tính

Yêu cầu Python 3.10 trở lên. Project dùng thư viện chuẩn Python, không cần cài package ngoài.

1. Giải nén repository.
2. Mở terminal tại thư mục có `ecommerce_app.py`.
3. Chạy:

```bash
python test_runner.py
```

4. Mở `reports/test_dashboard.html` bằng trình duyệt.
5. Xem kết quả chi tiết tại `reports/test_execution.csv` và tổng hợp theo requirement tại `reports/summary_by_requirement.csv`.

Expected gốc nằm trong `test_cases.csv`. Runner chỉ đọc file này và tạo actual ở thư mục `reports/`, không sửa expected.

## 4. Chạy trên Google Colab

1. Upload ZIP repository lên Colab hoặc clone repository từ GitHub (nếu đã publish).
2. Giải nén ZIP (nếu upload ZIP), chuyển working directory vào thư mục `STLab02_EduCommerce`.
3. Chạy cell:

```python
!python test_runner.py
```

4. Mở `reports/test_dashboard.html` từ tab Files hoặc tải về để xem bằng trình duyệt. Kết quả `test_execution.csv` cũng nằm trong thư mục `reports/`.

Có thể mở notebook `STLab02_EduCommerce.ipynb` và chạy các cell theo thứ tự.

## 5. Quy tắc kết quả

- PASS: actual đúng expected được xây từ acceptance criteria.
- FAIL: ứng dụng trả kết quả khác expected hoặc sai trạng thái kiểm tra.
- BLOCKED: dữ liệu test/setup không hợp lệ hoặc không thể tạo precondition; row vẫn được tính vào tổng, không bị bỏ qua âm thầm.
- Không chỉnh expected để biến FAIL thành PASS.
- Mỗi test case gọi `fixture()` riêng để tránh shared state.

## 6. Kết quả chạy kèm theo

Lần chạy đóng gói ngày 02/11/2026: **24 test cases, 24 PASS, 0 FAIL, 0 BLOCKED (pass rate 100%)**. Đây là kết quả thực thi local bằng Python đối với module mô phỏng in-memory trong Instruction, không phải kiểm thử website production hay gateway thật.

Lưu ý khi review: test `TC-PAY-003` nhận đúng `PAYMENT_DECLINED` và không tạo order, nhưng snapshot ghi nhận stock SKU A giảm từ 20 xuống 18. Quan sát này không làm test REQ-10 fail (expected của REQ-10 chỉ yêu cầu declined không tạo order), nhưng là một rủi ro liên module cần xác nhận và mở rộng kiểm thử rollback inventory ở phạm vi khác.

## 7. Thông tin cá nhân và GitHub

Trước khi nộp, điền MSSV, họ tên, lớp trong PDF. Tên PDF theo mẫu: `MSSV_HoTenSinhVien_STLab02.pdf`.

Repository name đề xuất: `stlab02-educommerce-testing`. Hướng dẫn tạo repository public bằng GitHub Desktop hoặc GitHub website nằm trong `GITHUB_UPLOAD_GUIDE.md`. Hiện tại gói này chưa có URL public thực tế; không dùng URL giả làm bằng chứng repo đã publish.
