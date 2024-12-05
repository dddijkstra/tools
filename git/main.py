import math
import os
import tkinter as tk
from tkinter import simpledialog

from numpy.lib.user_array import container
from playwright.sync_api import sync_playwright, TimeoutError
from config import Config
from containers import Container, NewContainer
from click import click_next_page, click_next_new_page
def get_page_number():
    """弹出输入框获取页码"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    page_number = simpledialog.askstring("输入页码", "请输入要访问的页码:")
    if page_number is None or page_number == '':  # 如果用户取消了输入
        print("用户取消了输入，默认使用第1页")
        return "1"
    return page_number
def run(pw, p_c):
    my_container = Container()
    if os.path.exists(p_c.result_file_path):
        os.remove(p_c.result_file_path)

    browser = pw.chromium.launch_persistent_context(
        user_data_dir=p_c.user_data_dir, headless=False
    )

    page = browser.new_page()
    page.set_default_timeout(100000)
    page.set_default_navigation_timeout(100000)
    page.on('route', lambda route, request: route.abort() if 'image' in request.resource_type else route.continue_())

    try:
        page.goto(p_c.web_path)
        page_number = get_page_number()
        my_container.current_page_number = int(page_number)
        my_container.max_page = int(page.locator("li.number").last.inner_text())
        page.wait_for_selector("text='简体中文'")
        page.click("text='简体中文'")
        page.wait_for_selector("#allDataTable")
        my_container.p = 0

        if int(page_number) > 1:
            inputs = page.query_selector_all('input[type="number"].el-input__inner')
            if inputs:
                inputs[-1].fill(page_number)
                page.keyboard.press("Enter")
                my_container.p = 1
            else:
                print("未找到匹配的 input 元素")

        while (my_container.current_page_number - 1) < my_container.max_page:
            column_count = 1 + (5 * my_container.p)
            page_count = my_container.p + 1
            page.wait_for_selector(f"td.el-table_{page_count}_column_{column_count}.el-table__cell")
            table_cells = page.locator(f"td.el-table_{page_count}_column_{column_count}.el-table__cell")
            for i in range(table_cells.count()):

                my_new_container = NewContainer()
                aaa = table_cells.locator("div > div span a")
                with open(p_c.result_file_path, "a", encoding="utf-8") as f:
                    f.write(f"\n[{aaa.nth(i).inner_text()}]")
                with browser.expect_page() as new_page_info:
                    aaa.nth(i).click()

                new_page = new_page_info.value
                try:
                    # 等待并尝试点击
                    new_page.locator('span.el-radio-button__inner', has_text='候选靶标谱').click()  # 设置超时时间为 5 秒
                    my_new_container.new_max_page =  math.ceil(int(new_page.locator('span.el-pagination__total').nth(0).text_content().split()[-1])/20)
                except TimeoutError:
                    print(f"未能定位第{my_container.current_page_number}页元素{aaa.nth(i).inner_text()}的'候选靶标谱'")
                    my_new_container.new_max_page = -1
                while my_new_container.new_max_page >= my_new_container.new_current_page_number:
                    new_page_count = my_new_container.n_p + 5
                    new_column_count = 23 + 4 * my_new_container.n_p
                    new_page.wait_for_selector(f"td.el-table_{new_page_count}_column_{new_column_count}.el-table__cell")
                    new_table_cells = new_page.locator(f"td.el-table_{new_page_count}_column_{new_column_count}.el-table__cell")
                    for j in range(new_table_cells.count()):
                        spans = new_table_cells.nth(j).locator("div > div span").all_inner_texts()
                        one_line = ','.join(spans)
                        with open(p_c.result_file_path, "a", encoding="utf-8") as f:
                            f.write(f"({one_line})")
                    click_next_new_page(my_new_container, p_c.time_sleep, new_page)
                new_page.close()
            click_next_page(my_container, p_c.time_sleep, page)
            my_container.current_page_number += 1

    except TimeoutError:
        print("页面加载超时！")
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        page_config = Config(
            "result.txt",
            "Storage",
            "http://www.tcmip.cn/ETCM2/front/#/browse/herb",
            0
        )
        run(playwright, page_config)
