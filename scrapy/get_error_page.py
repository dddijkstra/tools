import logging
import math
import re
import time

from playwright.sync_api import sync_playwright, TimeoutError

from utils.config import Config
from utils.containers import NewContainer
from utils.utils import click_next_new_page

logging.basicConfig(filename='log/error.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
def get_error_page():
    # 读取日志文件
    with open('log/main.log', 'r', encoding='utf-8') as file:
        logs = file.read()

    # 正则表达式匹配ERROR行中的中药名称
    error_pattern = r'WARNING.*\[(.*?)\]'

    # 查找所有符合条件的中药名称
    medicines = re.findall(error_pattern, logs)

    return medicines
def run(pw, p_c, medicines):
    browser = pw.chromium.launch_persistent_context(
        user_data_dir=p_c.user_data_dir, headless=False
    )
    new_page = browser.new_page()
    new_page.set_default_timeout(50000)
    new_page.set_default_navigation_timeout(50000)
    new_page.on('route', lambda route, request: route.abort() if 'image' in request.resource_type else route.continue_())
    for m in medicines:
        new_page.goto(p_c.web_path+f'/{m}')
        my_new_container = NewContainer()
        with open(p_c.result_file_path, "a", encoding="utf-8") as f:
            f.write(f"[{m}]")
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
                logging.info(f"[{m}]不存在'候选靶标谱'")
                break
        except TimeoutError:
            logging.warning(f"[{m}]的'候选靶标谱'不存在,或是本元素page加载失败")
            break
        while my_new_container.new_max_page >= my_new_container.new_current_page_number:
            new_page_count = my_new_container.n_p + my_new_container.o_page
            new_column_count = my_new_container.o_column + 4 * my_new_container.n_p
            try:
                new_page.wait_for_selector(f"td.el-table_{new_page_count}_column_{new_column_count}.el-table__cell",timeout=100000)
                new_table_cells = new_page.locator(f"td.el-table_{new_page_count}_column_{new_column_count}.el-table__cell")
            except TimeoutError:
                logging.error(f"[{m}]的靶标加载失败，稍后手动尝试下载")
                break
            for j in range(new_table_cells.count()):
                spans = new_table_cells.nth(j).locator("div > div span").all_inner_texts()
                one_line = ','.join(spans)
                with open(p_c.result_file_path, "a", encoding="utf-8") as f:
                    f.write(f"({one_line})")
            new_page.wait_for_selector('i.el-icon.el-icon-arrow-right', timeout=50000)
            click_next_new_page(my_new_container, p_c.time_sleep, new_page)
            my_new_container.new_current_page_number += 1
        time.sleep(p_c.time_sleep)
        with open(p_c.result_file_path, "a", encoding="utf-8") as f:
            f.write("\n")

# Function to extract plant names from file lines

if __name__ == '__main__':
    # single_medicine = ['']
    error_medicines = get_error_page()
    with sync_playwright() as playwright:
        page_config = Config(
            "error.txt",
            "Storage",
            "http://www.tcmip.cn/ETCM2/front/#/Detail/herb",
            0.5
        )
        run(playwright, page_config,error_medicines)
