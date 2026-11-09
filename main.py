import os
import sys
import time
import random
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from colorama import init, Fore, Style

import config
from poster import load_templates, get_media_files, post_to_group

init(autoreset=True)

def read_groups(file_path: Path):
    """Đọc danh sách link nhóm từ file txt"""
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    # Lọc bỏ dòng trống hoặc chú thích (#)
    return [l for l in lines if l and not l.startswith("#")]

async def countdown_timer(seconds: int):
    """Hiển thị đồng hồ đếm ngược trên CLI khi chờ vòng tiếp theo"""
    for remaining in range(seconds, 0, -1):
        hrs, rem = divmod(remaining, 3600)
        mins, secs = divmod(rem, 60)
        time_str = f"{hrs:02d}h {mins:02d}m {secs:02d}s"
        sys.stdout.write(f"\r{Fore.MAGENTA}⏳ Đang nghỉ trước vòng tiếp theo: {Fore.YELLOW}{time_str}{Fore.MAGENTA} (Nhấn Ctrl+C để dừng)...{Style.RESET_ALL} ")
        sys.stdout.flush()
        await asyncio.sleep(1)
    print("\n")

async def run_tab_worker(tab_config, p, templates, images):
    """Xử lý đăng bài cho 1 Tab độc lập"""
    tab_id = tab_config["tab_id"]
    name = tab_config["name"]
    profile_dir = Path(tab_config["profile_dir"])
    group_file = Path(tab_config["group_file"])

    groups = read_groups(group_file)
    if not groups:
        print(f"{Fore.YELLOW}[{name}] ⚠️ Danh sách nhóm trống ({group_file.name}). Bỏ qua tab này.")
        return

    print(f"{Fore.GREEN}[{name}] Bắt đầu mở trình duyệt với {len(groups)} nhóm...")

    # Tính toán toạ độ để chia 6 cửa sổ thành lưới 2 hàng x 3 cột trên màn hình
    idx_pos = tab_id - 1
    col = idx_pos % config.GRID_COLS
    row = idx_pos // config.GRID_COLS
    pos_x = col * config.WINDOW_WIDTH
    pos_y = row * config.WINDOW_HEIGHT

    try:
        browser_context = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=config.HEADLESS,
            no_viewport=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                f"--window-position={pos_x},{pos_y}",
                f"--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}",
            ]
        )
        page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()

        # Ép buộc Windows thu nhỏ đúng 510x400 và đặt đúng tọa độ qua CDP
        try:
            cdp = await browser_context.new_cdp_session(page)
            win = await cdp.send("Browser.getWindowForTarget")
            await cdp.send("Browser.setWindowBounds", {
                "windowId": win["windowId"],
                "bounds": {
                    "left": pos_x,
                    "top": pos_y,
                    "width": config.WINDOW_WIDTH,
                    "height": config.WINDOW_HEIGHT,
                    "windowState": "normal"
                }
            })
        except Exception:
            pass

        # Đồng bộ mức thu nhỏ giao diện (Zoom 50%) trên toàn bộ các tab
        zoom_level = getattr(config, "PAGE_ZOOM", "50%")
        await page.add_init_script(f"""
            const applyZoom = () => {{
                if (document.documentElement) {{
                    document.documentElement.style.zoom = '{zoom_level}';
                }}
            }};
            applyZoom();
            window.addEventListener('DOMContentLoaded', applyZoom);
            window.addEventListener('load', applyZoom);
        """)

        for idx, group_url in enumerate(groups, 1):
            # Chọn ngẫu nhiên 1 trong 5 mẫu text
            text_template = random.choice(templates)
            print(f"\n{Fore.BLUE}--- [{name}] Đang đăng nhóm {idx}/{len(groups)} ---")

            success = await post_to_group(page, group_url, text_template, images, name)
            
            # Delay ngẫu nhiên giữa các nhóm (15 - 20s)
            if idx < len(groups):
                delay = random.randint(config.MIN_DELAY_BETWEEN_GROUPS, config.MAX_DELAY_BETWEEN_GROUPS)
                print(f"{Fore.WHITE}[{name}] ⏱️ Nghỉ an toàn {delay}s trước khi sang nhóm tiếp theo...")
                await asyncio.sleep(delay)

        await browser_context.close()
        print(f"{Fore.GREEN}🎉 [{name}] ĐÃ HOÀN THÀNH TOÀN BỘ DANH SÁCH NHÓM!")

    except Exception as e:
        print(f"{Fore.RED}[{name}] Gặp lỗi trong quá trình chạy: {e}")

async def run_round(round_number: int):
    """Chạy 1 vòng hoàn chỉnh gồm 6 tab song song"""
    print(f"\n{Fore.CYAN}{'='*65}")
    print(f"{Fore.GREEN}        BẮT ĐẦU VÒNG ĐĂNG BÀI THỨ #{round_number}")
    print(f"{Fore.CYAN}{'='*65}")

    templates = load_templates()
    images = get_media_files()

    print(f"{Fore.WHITE}✓ Đã nạp: {len(templates)} mẫu text | {len(images)} hình ảnh trong thư mục media.")

    if len(images) < 4:
        print(f"{Fore.YELLOW}⚠️ Lưu ý: Bạn hiện có {len(images)}/4 ảnh trong thư mục media/.")

    async with async_playwright() as p:
        tasks = [
            run_tab_worker(tab_cfg, p, templates, images)
            for tab_cfg in config.TABS_CONFIG
        ]
        # Chạy đồng thời cả 6 tab
        await asyncio.gather(*tasks)

    print(f"\n{Fore.GREEN}✨ VÒNG #{round_number} ĐÃ HOÀN TẤT TRÊN TẤT CẢ CÁC TAB!")

async def main():
    print(f"{Fore.CYAN}{'#'*65}")
    print(f"{Fore.YELLOW}       FACEBOOK AUTO POSTER - 6 TABS CONCURRENT TOOL")
    print(f"{Fore.WHITE}       100% Miễn phí - Mở nguồn - Không checkpoint mật khẩu")
    print(f"{Fore.CYAN}{'#'*65}\n")

    round_counter = 1
    while True:
        try:
            await run_round(round_counter)
            
            # Thời gian nghỉ ngẫu nhiên 1 - 2 tiếng (3600s - 7200s)
            round_delay = random.randint(config.MIN_DELAY_BETWEEN_ROUNDS, config.MAX_DELAY_BETWEEN_ROUNDS)
            hrs = round_delay / 3600
            print(f"\n{Fore.CYAN}Nghỉ ngẫu nhiên: {hrs:.2f} giờ ({round_delay} giây) trước khi đăng vòng tiếp theo...")
            
            await countdown_timer(round_delay)
            round_counter += 1

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Đã nhận lệnh dừng từ bàn phím. Tạm biệt!")
            break
        except Exception as e:
            print(f"\n{Fore.RED}Lỗi hệ thống: {e}")
            print(f"{Fore.YELLOW}Thử lại sau 60 giây...")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nChương trình đã kết thúc.")
