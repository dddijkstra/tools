from playwright.sync_api import sync_playwright, TimeoutError
import os

def run(pw, p_n):
    if os.path.exists(r"C:\Users\zhang\PycharmProjects\test-play\result.txt"):
        os.remove(r"C:\Users\zhang\PycharmProjects\test-play\result.txt")
    current_page = p_n
    browser = pw.chromium.launch_persistent_context(
        user_data_dir=r"C:\Users\zhang\PycharmProjects\test-play\Storage", headless=False
    )
    page = browser.new_page()
    page.set_default_timeout(100000)
    page.set_default_navigation_timeout(100000)
    page.on('route', lambda route, request: route.abort() if 'image' in request.resource_type else route.continue_())
    page.goto("http://www.tcmip.cn/ETCM2/front/#/browse/traditional_chinese_medicine_formula")
    try:
        page.wait_for_selector("#allDataTable")
        print("页面加载完成！")
        page.click("text='简体中文'")
        last_li_locator = page.locator("li.number").last
        max_page = last_li_locator.inner_text()
        p = 0
        # 进入给出的页码
        if int(p_n) > 1:
            inputs = page.query_selector_all('input[type="number"].el-input__inner')
            if inputs:
                # 点击最后一个 input 元素
                inputs[-1].fill(p_n)
                page.keyboard.press("Enter")
                p = 1
            else:
                print("未找到匹配的 input 元素")
        while (p-1) < (int(max_page) - int(current_page)):
            index1 = 3 + (4 * p)
            index2 = p + 1
            page.wait_for_selector(f"td.el-table_{index2}_column_{index1}.el-table__cell")
            table_cells = page.locator(f"td.el-table_{index2}_column_{index1}.el-table__cell")
            print(f"本页（{int(current_page)}）找到了：{table_cells.count()}个处方")
            for i in range(table_cells.count()):
                spans = table_cells.nth(i).locator("div > div span").all_inner_texts()
                one_line = ''.join(spans)
                with open(r"C:\Users\zhang\PycharmProjects\test-play\result.txt", "a", encoding="utf-8") as f:
                    f.write(one_line)
                    f.write('\n')
            with page.expect_response("**/home/browse/") as response_info:
                # 在这里模拟用户行为，触发 POST 请求
                page.click('i.el-icon.el-icon-arrow-right')

            # 获取响应对象
            response = response_info.value
            print(f"Request URL: {response.url}")
            print(f"Response Status: {response.status}")

            # 检查返回状态码
            if response.status == 200:
                print("Request was successful!")
            else:
                print(f"Request failed with status: {response.status}")
            page.wait_for_function(
                "document.querySelector('.el-loading-mask').style.display === 'none'",
                timeout=30000  # 最长等待 30 秒
            )
            print("遮罩层已消失，继续操作")
            p = p+1

    except TimeoutError:
        print("页面加载超时！")
    browser.close()

with sync_playwright() as playwright:
    print("input the page number...")
    page_number = input()
    run(playwright, page_number)