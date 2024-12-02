import time

from playwright.sync_api import sync_playwright, TimeoutError, Page
import os

def run(pw, p_c):
    my_container = Container()
    if os.path.exists(p_c.result_file_path):
        os.remove(p_c.result_file_path)
    # 将缓存保存在本地，因为Playwright 默认在每次测试或运行时都使用无状态的新上下文，导致它不会自动保存缓存。
    browser = pw.chromium.launch_persistent_context(
        user_data_dir=p_c.user_data_dir, headless=False
    )
    my_container.page = browser.new_page()
    my_container.page.set_default_timeout(100000)
    my_container.page.set_default_navigation_timeout(100000)
    my_container.page.on('route', lambda route, request: route.abort() if 'image' in request.resource_type else route.continue_())
    try:
        my_container.page.goto(page_config.web_path)
        page_number = input("input the page number...:")
        my_container.current_page_number = int(page_number)
        my_container.max_page = int(my_container.page.locator("li.number").last.inner_text())
        my_container.page.wait_for_selector("#allDataTable")
        my_container.page.click("text='简体中文'")
        # 循环变量默认是0 如果需要切换页码 则置1 因为换页操作后实际上是从第二页开始爬取数据
        my_container.p = 0
        # 进入给出的页码
        if int(page_number) > 1:
            inputs = my_container.page.query_selector_all('input[type="number"].el-input__inner')
            if inputs:
                # 点击最后一个 input 元素
                inputs[-1].fill(page_number)
                my_container.page.keyboard.press("Enter")
                my_container.p = 1
            else:
                print("未找到匹配的 input 元素")
        while (my_container.current_page_number-1) < my_container.max_page:
            column_count = 1 + (7 * my_container.p)
            page_count = my_container.p + 1
            my_container.page.wait_for_selector(f"td.el-table_{page_count}_column_{column_count}.el-table__cell")
            table_cells = my_container.page.locator(f"td.el-table_{page_count}_column_{column_count}.el-table__cell")
            # 一次写一页
            for i in range(table_cells.count()):
                spans = table_cells.nth(i).locator("div > div span").all_inner_texts()
                one_line = ''.join(spans)
                with open(page_config.result_file_path, "a", encoding="utf-8") as f:
                    f.write(one_line)
                    f.write('\n')
            click_next_page(my_container, page_config.time_sleep)
            my_container.current_page_number += 1

    except TimeoutError:
        print("页面加载超时！")
    browser.close()

class Container:
    def __init__(self):
        self.p = 0
        self.current_page_number = 0
        self.max_page = 0
        self.page = None

def click_next_page(container: Container, time_sleep):
    if container.current_page_number >= container.max_page:
        print("Reached the maximum number of pages.")
        return  # 终止递归

    # 监听目标响应
    with container.page.expect_response("**/home/browse/") as response_info:
        time.sleep(time_sleep)
        # 模拟点击行为触发 POST 请求
        container.page.click('i.el-icon.el-icon-arrow-right')

        # 获取响应对象
        response = response_info.value

        # 检查返回状态码
        if response.status == 200:
            print(f"Request was successful on page {container.current_page_number + 1}")
            container.p += 1
            return
            # 递归调用，处理下一页
        else:
            print(f"Request failed with status: {response.status} on page {container.current_page_number + 1}")
            # 如果请求失败，也可以递归调用以继续尝试下一页
            container.current_page_number += 1
            click_next_page(container, time_sleep)
class Config:
    def __init__(self, result_file, user_data, web_path, time_sleep):
        local_path = os.getcwd()
        self.result_file_path = f"{local_path}/{result_file}"
        self.user_data_dir = f"{local_path}/{user_data}"
        self.web_path  = web_path
        self.time_sleep = time_sleep

with sync_playwright() as playwright:
    page_config = Config(
        "result.txt",
        "Storage",
        "http://www.tcmip.cn/ETCM2/front/#/browse/target",
        0
    )
    run(playwright, page_config)
