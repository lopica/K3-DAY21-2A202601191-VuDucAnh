# BÁO CÁO LAB MLOPS — DAY 21: CI/CD CHO AI SYSTEMS

**Họ tên:** Vũ Đức Anh  
**MSSV:** 2A202601191 | **Khoá:** K3  
**Môn:** AI in Action — VinUni  

---

## 1. Bộ siêu tham số đã chọn và lý do

Sau khi thực nghiệm với nhiều bộ tham số khác nhau và theo dõi kết quả bằng MLflow Tracking, bộ tham số tốt nhất được chọn là:

| Tham số | Giá trị |
|---|---|
| `n_estimators` | 500 |
| `max_features` | `sqrt` |
| `min_samples_leaf` | 1 |
| **Accuracy (eval set)** | **0.7640** |
| **F1 Score (weighted)** | **0.7629** |

**Lý do lựa chọn:**

- **`n_estimators = 500`**: Tăng số cây giúp giảm variance của mô hình ensemble. So sánh thực nghiệm cho thấy n=50 đạt acc=0.588, n=200 đạt acc=0.744, và n=500 đạt acc=0.764 — xu hướng tăng đơn điệu với tập 5 996 mẫu, cho thấy dữ liệu đủ lớn để hưởng lợi từ nhiều cây hơn.

- **`max_features = sqrt`**: Sử dụng căn bậc hai số đặc trưng tại mỗi nút phân nhánh tạo ra sự đa dạng giữa các cây, giảm correlation và cải thiện khả năng tổng quát hoá. Thực nghiệm với `max_features = None` (dùng toàn bộ đặc trưng) cho kết quả kém hơn do các cây trở nên quá giống nhau.

- **`min_samples_leaf = 1`**: Cho phép cây phân nhánh đến mức tối đa, phù hợp với bài toán phân loại 3 lớp có ranh giới phức tạp (chất lượng rượu vang thấp/trung bình/cao dựa trên 16 đặc trưng hoá học, trong đó có các đặc trưng phái sinh từ `WineFeatureEngineer`).

- **Feature Engineering**: Bổ sung 7 đặc trưng phái sinh (tỷ lệ SO₂, mật độ cồn, tổng axit, log-transform 4 cột lệch phân phối) giúp mô hình học được các quan hệ phi tuyến và vượt qua ngưỡng 0.70.

---

## 2. Khó khăn gặp phải và cách giải quyết

**Khó khăn 1 — Chính sách tổ chức chặn SA key (`iam.disableServiceAccountKeyCreation`)**  
GitHub Actions không thể xác thực với GCP qua file JSON credentials theo cách thông thường. Giải pháp: triển khai **Workload Identity Federation (WIF)** — GitHub Actions xác thực trực tiếp với GCP thông qua OIDC token, không cần SA key. Cần tạo Workload Identity Pool, cấu hình attribute mapping, và bind `principalSet` với service account.

**Khó khăn 2 — OS Login yêu cầu quyền sudo trên GCE**  
VM bật `constraints/compute.requireOsLogin`; username SSH tự động đổi thành `ducanhtcp_gmail_com`. Lệnh `sudo systemctl restart` thất bại vì service account chỉ có `roles/compute.osLogin`. Giải pháp: cấp thêm `roles/compute.osAdminLogin` để có quyền sudo.

**Khó khăn 3 — Forked repository chặn workflow tự động**  
Repo fork từ template của giảng viên khiến GitHub yêu cầu phê duyệt thủ công khi workflow dùng secrets. Pipeline không tự trigger khi push. Giải pháp: gọi GitHub API (`PUT /repos/{owner}/{repo}/actions/permissions/workflow`) để bật chế độ `allow_all`, sau đó xác nhận lại bằng lệnh `gh workflow run`.

**Khó khăn 4 — `ModuleNotFoundError: src` khi serve model trên VM**  
VM thiếu `features.py` và `serve.py` cũ không có `sys.path.insert`, khiến `joblib.load()` không tìm được `WineFeatureEngineer`. Giải pháp: thêm bước SCP trong job Deploy để copy source files vào `/tmp/` rồi `sudo mv` đến đúng vị trí, đảm bảo VM luôn có phiên bản code mới nhất trước khi restart service.

**Khó khăn 5 — Accuracy dưới ngưỡng 0.70 ở Bước 1 (phase 1 data)**  
Với chỉ 2 998 mẫu huấn luyện, accuracy tốt nhất chỉ đạt 0.698 — không vượt eval gate. Bổ sung 2 998 mẫu mới ở Bước 3 (Simulate New Data) đẩy accuracy lên 0.764, pipeline 4-job chạy thành công end-to-end, và model được tự động deploy lên VM.

---

*Toàn bộ pipeline (Unit Test → Train → Eval Gate → Deploy) đã hoạt động ổn định, model phục vụ tại endpoint `/predict` trên GCE VM qua FastAPI.*
