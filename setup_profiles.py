import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from colorama import init, Fore, Style

import config

init(autoreset=True)

def open_profile(tab_info):
    tab_id = tab_info["tab_id"]
    name = tab_info["name"]
    profile_dir = Path(tab_info["profile_dir"])
    profile_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}Đang mở trình duyệt cho: {Fore.GREEN}{name}")
    print(f"{Fore.WHITE}Thư mục Profile: {profile_dir}")
    print(f"{Fore.YELLOW}HƯỚNG DẪN:")
    print(f"1. Đăng nhập tài khoản Facebook trên cửa sổ trình duyệt vừa hiện lên.")
    print(f"2. Nếu là Tab Fanpage (Tab 2 hoặc Tab 4), hãy bấm chuyển Profile sang Trang tương ứng.")
    print(f"3. Sau khi hoàn tất, quay lại đây và nhấn [ENTER] để lưu phiên và đóng trình duyệt.")
    print(f"{Fore.CYAN}{'='*60}\n")

    with sync_playwright() as p:
        browser_context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        page = browser_context.new_page()
        page.goto("https://www.facebook.com", timeout=60000)

        input(f"{Fore.MAGENTA}👉 Nhấn phím [ENTER] khi bạn đã đăng nhập xong để đóng trình duyệt...{Style.RESET_ALL}")
        browser_context.close()
        print(f"{Fore.GREEN}✓ Đã lưu phiên đăng nhập cho {name} thành công!\n")

def main():
    while True:
        print(f"\n{Fore.BLUE}{'='*60}")
        print(f"{Fore.CYAN}       TOOL THIẾT LẬP ĐĂNG NHẬP 6 PROFILE FACEBOOK")
        print(f"{Fore.BLUE}{'='*60}")
        for tab in config.TABS_CONFIG:
            print(f"{Fore.WHITE}[{tab['tab_id']}] {tab['name']}")
        print(f"{Fore.WHITE}[A] Thiết lập lần lượt tất cả từ 1 đến 6")
        print(f"{Fore.WHITE}[0] Thoát ra")
        print(f"{Fore.BLUE}{'='*60}")

        choice = input(f"{Fore.YELLOW}Chọn số profile muốn mở (1-6, A hoặc 0): {Style.RESET_ALL}").strip().upper()

        if choice == '0':
            print(f"{Fore.GREEN}Đã thoát chương trình setup.")
            break
        elif choice == 'A':
            for tab in config.TABS_CONFIG:
                open_profile(tab)
            print(f"{Fore.GREEN}🎉 Chúc mừng bạn đã hoàn tất đăng nhập cho cả 6 Tab!")
            break
        else:
            matched = [t for t in config.TABS_CONFIG if str(t['tab_id']) == choice]
            if matched:
                open_profile(matched[0])
            else:
                print(f"{Fore.RED}Lựa chọn không hợp lệ. Vui lòng thử lại!")

if __name__ == "__main__":
    main()
