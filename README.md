# Facebook Auto Group Poster (6 Tabs Concurrent) 🚀

Tool tự động đăng bài vào các nhóm Facebook đa luồng (6 tabs chạy song song), hoàn toàn **miễn phí**, bảo mật cao và sẵn sàng đẩy lên GitHub.

---

## ✨ Điểm nổi bật
- **Chạy 6 Tab đồng thời:** 
  - 2 tài khoản chạy song song cả Nick cá nhân & Fanpage (4 tabs).
  - 2 tài khoản chạy Nick cá nhân (2 tabs).
- **Tránh Checkpoint 100%:** Sử dụng cơ chế lưu Profile Chrome (`launch_persistent_context`). Bạn chỉ cần đăng nhập bằng tay 1 lần duy nhất, tool không lưu hay gửi mật khẩu đi bất kỳ đâu.
- **Nội dung xoay vòng:** Tự động chọn ngẫu nhiên 1 trong 5 mẫu bài viết + đính kèm cùng lúc cả 4 hình ảnh cố định.
- **Giãn cách an toàn:** Nghỉ ngẫu nhiên 15 - 20 giây giữa các nhóm để tránh bị hạn chế tính năng.
- **Tự động lặp lại:** Sau khi tất cả các tab hoàn thành danh sách nhóm, tool tự động nghỉ ngẫu nhiên từ **1 đến 2 tiếng** và chạy lại vòng mới kèm đồng hồ đếm ngược trực quan.
- **Bảo mật GitHub:** Đã tích hợp sẵn `.gitignore` để không bao giờ bị lộ cookie hay dữ liệu đăng nhập cá nhân.

---

## 📁 Cấu trúc thư mục

```text
fb-auto-poster/
│
├── config.py             # Cấu hình thời gian delay, thông số 6 tabs
├── setup_profiles.py     # Tool hỗ trợ đăng nhập 6 profile Facebook ban đầu
├── poster.py             # Module điều khiển đăng bài & upload ảnh
├── main.py               # Chạy chính (6 tabs song song + vòng lặp 1-2h)
├── requirements.txt      # Thư viện Python cần cài đặt
├── .gitignore            # Loại trừ dữ liệu đăng nhập và file riêng tư
│
├── content/
│   └── templates.txt     # 5 mẫu nội dung bài đăng
├── media/                # Đặt 4 hình ảnh cố định vào đây
└── data/
    ├── tab_1_groups.txt  # Link nhóm cho Tab 1 (TK 1 - Cá nhân)
    ├── tab_2_groups.txt  # Link nhóm cho Tab 2 (TK 1 - Fanpage)
    ├── tab_3_groups.txt  # Link nhóm cho Tab 3 (TK 2 - Cá nhân)
    ├── tab_4_groups.txt  # Link nhóm cho Tab 4 (TK 2 - Fanpage)
    ├── tab_5_groups.txt  # Link nhóm cho Tab 5 (TK 3 - Cá nhân)
    └── tab_6_groups.txt  # Link nhóm cho Tab 6 (TK 4 - Cá nhân)
```

---

## 🛠️ Hướng dẫn cài đặt & sử dụng

### Bước 1: Cài đặt môi trường
Mở Terminal / PowerShell tại thư mục dự án và chạy:

```bash
# 1. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 2. Cài đặt trình duyệt cho Playwright
playwright install chromium
```

---

### Bước 2: Chuẩn bị nội dung & hình ảnh
1. **Hình ảnh:** Sao chép đúng **4 bức ảnh** của bạn vào thư mục `media/` (hỗ trợ .png, .jpg, .jpeg, .webp).
2. **Nội dung:** Chỉnh sửa file `content/templates.txt` để thay đổi 5 mẫu text tùy ý.
3. **Danh sách nhóm:** Mở từng file trong thư mục `data/` (`tab_1_groups.txt` đến `tab_6_groups.txt`), dán các đường link nhóm Facebook cần đăng vào (mỗi dòng 1 link).

---

### Bước 3: Đăng nhập sẵn cho 6 Tab (Chỉ làm 1 lần duy nhất)
Chạy lệnh:
```bash
python setup_profiles.py
```
- Chọn số từ `1` đến `6` (hoặc nhập `A` để thiết lập lần lượt tất cả).
- Cửa sổ Chrome sẽ hiện ra, bạn chỉ cần đăng nhập tài khoản Facebook bình thường.
- *Đối với Tab 2 và Tab 4:* Sau khi đăng nhập, hãy bấm góc phải trên Facebook để **chuyển sang Trang/Fanpage**.
- Đăng nhập xong, quay lại giao diện dòng lệnh và nhấn phím **[ENTER]**. Trình duyệt sẽ lưu lại phiên đăng nhập vĩnh viễn trên máy bạn.

---

### Bước 4: Chạy Tool tự động
Chạy lệnh:
```bash
python main.py
```
Tool sẽ tự động:
1. Mở 6 tab Facebook song song tương ứng với 6 danh sách nhóm đã chia.
2. Đăng bài kèm 4 ảnh và delay ngẫu nhiên 15 - 20s giữa các nhóm.
3. Khi đăng xong toàn bộ, hệ thống sẽ đếm ngược 1 - 2 tiếng (ngẫu nhiên) rồi tự động lặp lại vòng tiếp theo.

---

## 📤 Hướng dẫn đưa lên GitHub an toàn

Vì file `.gitignore` đã được cấu hình sẵn, bạn hoàn toàn yên tâm đưa code lên GitHub mà **không sợ bị lộ tài khoản Facebook**:

```bash
git init
git add .
git commit -m "Khoi tao tool dang bai Facebook 6 tab"
git branch -M main
git remote add origin https://github.com/<tai-khoan-cua-ban>/<ten-repo>.git
git push -u origin main
```
