import os
import random
import asyncio
from pathlib import Path
from colorama import Fore, Style
import config

def load_templates():
    """Đọc 5 mẫu text từ file templates.txt"""
    if not config.TEMPLATES_FILE.exists():
        return ["Chào mọi người! Chúc mọi người một ngày tốt lành!"]
    
    with open(config.TEMPLATES_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    templates = [t.strip() for t in content.split("---TEMPLATE---") if t.strip()]
    return templates if templates else ["Chào cả nhà!"]

def get_media_files():
    """Lấy danh sách tối đa 4 file ảnh trong thư mục media"""
    if not config.MEDIA_DIR.exists():
        return []
    
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    images = [
        str(f.resolve()) for f in config.MEDIA_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in valid_extensions
    ]
    # Lấy đúng 4 ảnh đầu tiên
    return images[:4]

async def post_to_group(page, group_url: str, text: str, images: list, tab_name: str) -> bool:
    """Thực hiện đăng bài viết kèm 4 ảnh vào một nhóm Facebook"""
    print(f"{Fore.CYAN}[{tab_name}] Đang mở nhóm: {Fore.WHITE}{group_url}")
    try:
        await page.goto(group_url, timeout=45000, wait_until="domcontentloaded")
        
        # 1. Ép Zoom 70% và chờ giao diện ổn định hoàn toàn trước khi làm bất kỳ thao tác nào
        zoom_level = getattr(config, "PAGE_ZOOM", "70%")
        try:
            await page.evaluate(f"document.documentElement.style.zoom = '{zoom_level}'")
            print(f"{Fore.WHITE}[{tab_name}] ✓ Đã chỉnh Zoom {zoom_level}, chờ giao diện ổn định...")
        except Exception:
            pass
            
        await asyncio.sleep(3)

        # 1. Tìm nút bấm mở khung "Tạo bài viết"
        post_box_selectors = [
            'div[role="button"]:has-text("Viết gì đó...")',
            'div[role="button"]:has-text("Bạn viết gì đi...")',
            'div[role="button"]:has-text("Tạo bài viết công khai...")',
            'div[role="button"]:has-text("Write something...")',
            'div[role="button"]:has-text("Create a public post...")',
            'div[role="button"]:has-text("Tạo bài viết...")',
            'span:has-text("Viết gì đó...")',
            'span:has-text("Bạn viết gì đi...")',
            'span:has-text("Write something...")'
        ]

        post_trigger = None
        for sel in post_box_selectors:
            try:
                locator = page.locator(sel).first
                if await locator.is_visible(timeout=2000):
                    post_trigger = locator
                    break
            except Exception:
                continue

        if not post_trigger:
            print(f"{Fore.RED}[{tab_name}] Không tìm thấy nút đăng bài ở nhóm này (có thể chưa tham gia hoặc nhóm đóng).")
            return False

        await post_trigger.scroll_into_view_if_needed()
        await post_trigger.click(force=True)
        await asyncio.sleep(2)

        # 2. CHỜ CỬA SỔ ĐĂNG BÀI XUẤT HIỆN HOÀN TOÀN (Tuyệt đối không lấy nhầm khung comment)
        dialog_candidate = page.locator('div[role="dialog"]:visible').filter(
            has_text=["Tạo bài viết", "Create post", "Tạo bài viết công khai", "Create a public post", "Bạn đang nghĩ gì"]
        ).first

        dialog = None
        for attempt in range(2):
            try:
                if await dialog_candidate.is_visible(timeout=8000):
                    dialog = dialog_candidate
                    break
            except Exception:
                pass
            
            # Nếu web tải chậm chưa mở kịp dialog, bấm lại nút tạo bài viết một lần nữa
            print(f"{Fore.YELLOW}[{tab_name}] Đang chờ cửa sổ đăng bài mở ra (lần {attempt+1})...")
            try:
                await post_trigger.click(force=True)
                await asyncio.sleep(3)
            except Exception:
                pass

        if not dialog:
            # Thử lấy bất kỳ dialog nào đang hiển thị có chứa nút Đăng/Post
            fallback_dialog = page.locator('div[role="dialog"]:visible').filter(
                has=page.locator('div[aria-label="Đăng"], div[aria-label="Post"], div[role="button"]:has-text("Đăng")')
            ).first
            if await fallback_dialog.count() and await fallback_dialog.is_visible():
                dialog = fallback_dialog

        if not dialog:
            print(f"{Fore.RED}[{tab_name}] Cửa sổ đăng bài chưa mở kịp do mạng chậm. Bỏ qua nhóm này để tránh đăng nhầm.")
            return False

        # 3. Tìm khung soạn thảo BẮT BUỘC nằm BÊN TRONG cửa sổ dialog vừa mở
        editor = dialog.locator('div[contenteditable="true"][role="textbox"], div[contenteditable="true"]').first
        try:
            await editor.wait_for(state="visible", timeout=10000)
        except Exception:
            print(f"{Fore.RED}[{tab_name}] Không tìm thấy ô soạn thảo trong cửa sổ đăng bài.")
            return False

        # 4. Nhập nội dung văn bản (Text)
        await editor.click(force=True)
        await editor.focus()
        await asyncio.sleep(1)
        
        try:
            await editor.fill(text)
        except Exception:
            await page.keyboard.type(text, delay=10)
        await asyncio.sleep(2)

        # 4. Tải lên hình ảnh (Nạp trực tiếp, chặn hiển thị cửa sổ Windows)
        if images and len(images) > 0:
            print(f"{Fore.YELLOW}[{tab_name}] Đang tải lên {len(images)} hình ảnh trực tiếp...")
            uploaded = False

            # CÁCH 1: Bơm file trực tiếp vào thẻ input ẩn của Facebook (Mượt nhất, không gọi UI)
            file_inputs = page.locator('input[type="file"]')
            count = await file_inputs.count()
            
            if count > 0:
                # Duyệt ngược từ thẻ input cuối cùng (thường là thẻ của hộp thoại Đăng bài vừa mở)
                for i in range(count - 1, -1, -1):
                    try:
                        target_input = file_inputs.nth(i)
                        await target_input.evaluate("el => { el.setAttribute('multiple', 'multiple'); el.multiple = true; }")
                        await target_input.set_input_files(images)
                        uploaded = True
                        print(f"{Fore.GREEN}[{tab_name}] Đã nạp {len(images)} ảnh trực tiếp vào cấu trúc trang.")
                        break
                    except Exception:
                        continue

            # CÁCH 2: Nếu thẻ input chưa render, buộc click nút nhưng SỬ DỤNG BỘ CHẶN (Intercept)
            if not uploaded:
                photo_btn_selectors = [
                    'div[aria-label="Ảnh/video"]',
                    'div[aria-label="Photo/video"]',
                    'div[aria-label*="Ảnh/"]',
                    'div[role="button"]:has-text("Ảnh/video")'
                ]
                for p_sel in photo_btn_selectors:
                    try:
                        btn = dialog.locator(p_sel).first
                        if await btn.is_visible(timeout=1500):
                            # Khối expect_file_chooser này sẽ bắt luồng mở popup và ngăn Windows hiển thị nó
                            async with page.expect_file_chooser(timeout=3000) as fc_info:
                                await btn.click(force=True)
                            
                            file_chooser = await fc_info.value
                            await file_chooser.set_files(images)
                            uploaded = True
                            print(f"{Fore.GREEN}[{tab_name}] Đã nạp ảnh thành công (đã chặn cửa sổ Windows).")
                            break
                    except Exception:
                        continue

            if uploaded:
                print(f"{Fore.YELLOW}[{tab_name}] Đang chờ Facebook tải lên và xử lý hiển thị ảnh...")
                await asyncio.sleep(8)
            else:
                print(f"{Fore.RED}[{tab_name}] Không thể tìm thấy công cụ tải ảnh lên trên giao diện.")

        # 5. Kiểm tra chế độ xem trước hay đăng thật
        if not getattr(config, "AUTO_SUBMIT_POST", True):
            print(f"{Fore.MAGENTA}👁️ [{tab_name}] ĐÃ SOẠN BÀI & NẠP ẢNH XONG (Chế độ xem trước: KHÔNG BẤM ĐĂNG).")
            print(f"{Fore.WHITE}[{tab_name}] Giữ màn hình bài viết để bạn quan sát...")
            await asyncio.sleep(10)
            return True

        # 6. Nhấn nút "Đăng" (Post) khi ở chế độ đăng thật
        post_btn_selectors = [
            'div[role="dialog"] div[aria-label="Đăng"]',
            'div[role="dialog"] div[aria-label="Post"]',
            'div[role="dialog"] div[role="button"]:has-text("Đăng")',
            'div[role="dialog"] div[role="button"]:has-text("Post")'
        ]

        post_button = None
        for p_btn in post_btn_selectors:
            locator = page.locator(p_btn)
            count = await locator.count()
            if count > 0:
                # BẮT BUỘC: Quét ngược từ dưới lên để lấy nút Đăng của hộp thoại MỚI NHẤT
                for i in range(count - 1, -1, -1):
                    btn_candidate = locator.nth(i)
                    if await btn_candidate.is_visible(timeout=1000):
                        post_button = btn_candidate
                        break
            if post_button:
                break

        if post_button:
            # Chờ nút Đăng sẵn sàng (chuyển từ xám sang xanh)
            for wait_cnt in range(15):
                is_disabled = await post_button.get_attribute("aria-disabled")
                if is_disabled != "true":
                    break
                print(f"{Fore.YELLOW}[{tab_name}] Đang chờ ảnh tải xong để bấm Đăng ({wait_cnt+1}/15)...")
                await asyncio.sleep(1)

            # Chờ thêm 1.5 giây để ReactJS trên Facebook kịp gắn sự kiện onClick vào nút
            await asyncio.sleep(1.5)

            try:
                # Bỏ force=True, dùng click thông thường để đảm bảo click trúng đích
                await post_button.click(timeout=3000)
            except Exception:
                # Phương án dự phòng: Bắn luồng click trực tiếp bằng JavaScript nếu giao diện bị đè
                await post_button.evaluate("el => el.click()")
                
            print(f"{Fore.GREEN}[{tab_name}] Đã bấm ĐĂNG. Chờ xử lý...")

            # Đợi modal đóng lại (xác nhận đăng thành công)
            try:
                await dialog.wait_for(state="hidden", timeout=30000)
                print(f"{Fore.GREEN}✓ [{tab_name}] ĐĂNG BÀI THÀNH CÔNG!")
                return True
            except Exception:
                print(f"{Fore.YELLOW}[{tab_name}] Hộp thoại chưa đóng, có thể bài viết đang chờ duyệt hoặc mất nhiều thời gian tải.")
                return True
        else:
            print(f"{Fore.RED}[{tab_name}] Không tìm thấy nút 'Đăng' trên giao diện hiện tại.")
            return False

    # KHỐI EXCEPT TỔNG CỦA HÀM (Cần phải có để không bị lỗi SyntaxError)
    except Exception as e:
        print(f"{Fore.RED}[{tab_name}] Lỗi khi đăng bài: {e}")
        return False
