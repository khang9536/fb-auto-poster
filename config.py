import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Thư mục lưu dữ liệu Profile trình duyệt Chrome (tương đương 6 tài khoản/phiên độc lập)
PROFILES_DIR = BASE_DIR / "profiles"

# Thư mục dữ liệu link nhóm
DATA_DIR = BASE_DIR / "data"

# Thư mục chứa hình ảnh bài đăng
MEDIA_DIR = BASE_DIR / "media"

# Thư mục chứa mẫu bài viết text
CONTENT_DIR = BASE_DIR / "content"
TEMPLATES_FILE = CONTENT_DIR / "templates.txt"

# Cấu hình thời gian delay giữa các nhóm (cố định 15s)
MIN_DELAY_BETWEEN_GROUPS = 15
MAX_DELAY_BETWEEN_GROUPS = 15

# Thời gian nghỉ sau mỗi vòng đăng bài (giây): 1 tiếng = 3600s, 2 tiếng = 7200s
MIN_DELAY_BETWEEN_ROUNDS = 3600
MAX_DELAY_BETWEEN_ROUNDS = 7200

# Chế độ hiển thị trình duyệt: False = Hiện trình duyệt để quan sát, True = Chạy ngầm (Headless)
HEADLESS = False

# Chế độ đăng bài: True = Tự động bấm Đăng bài hoàn chỉnh
AUTO_SUBMIT_POST = True

# Độ thu nhỏ giao diện đồng bộ cho tất cả các tab (60%)
PAGE_ZOOM = "60%"

# Cấu hình bố cục lưới chia đều 6 cửa sổ trên màn hình (Grid 2 hàng x 3 cột)
GRID_COLS = 3
GRID_ROWS = 2
WINDOW_WIDTH = 510   # 510 * 3 = 1530px (vừa khít bề ngang màn hình 1536px của bạn)
WINDOW_HEIGHT = 400  # 400 * 2 = 800px (vừa khít chiều dọc màn hình 864px của bạn)

# Danh sách 6 Tab tương ứng với 6 Profile và 6 File danh sách nhóm
TABS_CONFIG = [
    {
        "tab_id": 1,
        "name": "Tab 1 (TK 1 - Cá nhân)",
        "profile_dir": PROFILES_DIR / "profile_1",
        "group_file": DATA_DIR / "tab_1_groups.txt",
    },
    {
        "tab_id": 2,
        "name": "Tab 2 (TK 1 - Fanpage)",
        "profile_dir": PROFILES_DIR / "profile_2",
        "group_file": DATA_DIR / "tab_2_groups.txt",
    },
    {
        "tab_id": 3,
        "name": "Tab 3 (TK 2 - Cá nhân)",
        "profile_dir": PROFILES_DIR / "profile_3",
        "group_file": DATA_DIR / "tab_3_groups.txt",
    },
    {
        "tab_id": 4,
        "name": "Tab 4 (TK 2 - Fanpage)",
        "profile_dir": PROFILES_DIR / "profile_4",
        "group_file": DATA_DIR / "tab_4_groups.txt",
    },
    {
        "tab_id": 5,
        "name": "Tab 5 (TK 3 - Cá nhân)",
        "profile_dir": PROFILES_DIR / "profile_5",
        "group_file": DATA_DIR / "tab_5_groups.txt",
    },
    {
        "tab_id": 6,
        "name": "Tab 6 (TK 4 - Cá nhân)",
        "profile_dir": PROFILES_DIR / "profile_6",
        "group_file": DATA_DIR / "tab_6_groups.txt",
    },
]
