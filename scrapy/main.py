import logging
import math
import os
import re

from playwright.sync_api import sync_playwright, TimeoutError
from config import Config
from containers import Container, NewContainer
from utils import *

def run(pw, p_c):
    global page_number
    my_container = Container()

    browser = pw.chromium.launch_persistent_context(
        user_data_dir=p_c.user_data_dir, headless=False
    )

    page = browser.new_page()
    page.set_default_timeout(50000)
    page.set_default_navigation_timeout(50000)
    page.on('route', lambda route, request: route.abort() if 'image' in request.resource_type else route.continue_())

    try:
        page.goto(p_c.web_path)
        page_number = get_page_number()
        logging.basicConfig(filename=f'begin_at_{page_number}.log', level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        if os.path.exists(p_c.result_file_path):
            os.remove(p_c.result_file_path)
        my_container.current_page_number = int(page_number)
        my_container.max_page = int(page.locator("li.number").last.inner_text())
        logging.info("Page number: {}".format(page_number))
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
                logging.error("未找到匹配的 input 元素")
        while (my_container.current_page_number - 1) < my_container.max_page:
            column_count = 1 + (5 * my_container.p)
            page_count = my_container.p + 1
            page.wait_for_selector(f"td.el-table_{page_count}_column_{column_count}.el-table__cell",timeout=50000)
            table_cells = page.locator(f"td.el-table_{page_count}_column_{column_count}.el-table__cell")
            aaa = table_cells.locator("div > div span a")
            for i in range(table_cells.count()):
                my_new_container = NewContainer()
                with open(p_c.result_file_path, "a", encoding="utf-8") as f:
                    f.write(f"[{aaa.nth(i).inner_text()}]")
                with browser.expect_page() as new_page_info:
                    aaa.nth(i).click()

                new_page = new_page_info.value

                try:
                    # 等待"候选靶标谱"并尝试点击
                    new_page.wait_for_selector('span.el-radio-button__inner',timeout=50000)
                    target_span = new_page.locator('span.el-radio-button__inner').filter(has_text="候选靶标谱")

                    if target_span.count() > 0:
                        target_span.click()
                        new_page.wait_for_selector('div.cell >> text=基因符号', timeout=50000)
                        outer_class_str = new_page.locator('div.cell >> text=基因符号').locator('..').get_attribute(
                            'class')
                        match = re.search(r'el-table_(\d+)_column_(\d+)', outer_class_str)
                        my_new_container.o_page = int(match.group(1))  # First number (5)
                        my_new_container.o_column = int(match.group(2))  # Second number (23)
                        my_new_container.new_max_page =  math.ceil(int(new_page.locator('span.el-pagination__total').nth(0).text_content().split()[-1])/20)
                    else:
                        logging.info(f"第{my_container.current_page_number}页[{aaa.nth(i).inner_text()}]不存在'候选靶标谱'")
                        my_new_container.new_max_page = -1
                except TimeoutError:
                    logging.warning(f"第{my_container.current_page_number}页[{aaa.nth(i).inner_text()}]的'候选靶标谱'不存在,或是本元素page加载失败")
                    my_new_container.new_max_page = -1
                while my_new_container.new_max_page >= my_new_container.new_current_page_number:
                    new_page_count = my_new_container.n_p + my_new_container.o_page
                    new_column_count = my_new_container.o_column + 4 * my_new_container.n_p
                    try:
                        new_page.wait_for_selector(f"td.el-table_{new_page_count}_column_{new_column_count}.el-table__cell",timeout=100000)
                        new_table_cells = new_page.locator(f"td.el-table_{new_page_count}_column_{new_column_count}.el-table__cell")
                    except TimeoutError:
                        logging.error(f"第{my_container.current_page_number}页[{aaa.nth(i).inner_text()}]的靶标加载失败，稍后手动尝试下载")
                        break
                    for j in range(new_table_cells.count()):
                        spans = new_table_cells.nth(j).locator("div > div span").all_inner_texts()
                        one_line = ','.join(spans)
                        with open(p_c.result_file_path, "a", encoding="utf-8") as f:
                            f.write(f"({one_line})")
                    new_page.wait_for_selector('i.el-icon.el-icon-arrow-right', timeout=50000)
                    click_next_new_page(my_new_container, p_c.time_sleep, new_page)
                    my_new_container.new_current_page_number += 1
                new_page.close()
                time.sleep(p_c.time_sleep)
                with open(p_c.result_file_path, "a", encoding="utf-8") as f:
                    f.write("\n")
            click_next_page(my_container, p_c.time_sleep, page)
            my_container.current_page_number += 1
    except TimeoutError:
        print(f"{my_container.current_page_number}页面加载超时！")
        old_file_path = p_c.result_file_path
        new_file_path = p_c.dir_path + "page"+ page_number + "-" + str(my_container.current_page_number-1)+ ".txt"
        rename_file(old_file_path, new_file_path)
        TimeoutError.message()
    browser.close()
def rename_file(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        print(f"File renamed from {old_path} to {new_path}")
    except FileNotFoundError:
        print(f"File {old_path} not found.")
    except PermissionError:
        print(f"Permission denied while renaming {old_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        page_config = Config(
            "result.txt",
            "Storage",
            "http://www.tcmip.cn/ETCM2/front/#/browse/herb",
            0.5
        )
        run(playwright, page_config)
