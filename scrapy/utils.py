import logging
import time
from playwright.sync_api import Page
import tkinter as tk
from tkinter import simpledialog

def click_next_page(container, time_sleep, page: Page):
    if container.current_page_number >= container.max_page:
        print("Reached the maximum number of pages.")
        return

    with page.expect_response("**/home/browse/") as response_info:
        time.sleep(time_sleep)
        page.click('i.el-icon.el-icon-arrow-right')
        response = response_info.value

        if response.status == 200:
            container.p += 1
            return
        else:
            print(f"Request failed with status: {response.status} on page {container.current_page_number + 1}")
            container.current_page_number += 1
            click_next_page(container, time_sleep, page)

def click_next_new_page(container, time_sleep, page: Page):
    if container.new_max_page == container.new_current_page_number:
        container.new_current_page_number += 1
        return

    try:
        page.wait_for_selector('i.el-icon.el-icon-arrow-right',timeout=50000)
        time.sleep(time_sleep)
        page.locator('i.el-icon.el-icon-arrow-right').nth(0).click()
        container.n_p += 1
    except TimeoutError:
        logging.exception("Timed out waiting for page to load")
        print(f"Request failed with timeout on page {container.current_page_number + 1}")
        container.new_max_page = -1

def get_page_number():
    """弹出输入框获取页码"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    page_number = simpledialog.askstring("输入页码", "请输入要访问的页码:")
    if page_number is None or page_number == '':  # 如果用户取消了输入
        print("用户取消了输入，默认使用第1页")
        return "1"
    return page_number