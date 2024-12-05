import time
from playwright.sync_api import Page

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

    with page.expect_response("**/home/related/") as response_info:
        time.sleep(time_sleep)
        page.click('i.el-icon.el-icon-arrow-right')
        response = response_info.value

        if response.status == 200:
            container.new_current_page_number += 1
            container.n_p += 1
            return
        else:
            print(f"Request failed with status: {response.status} on page {container.new_current_page_number + 1}")
            container.new_current_page_number += 1
            click_next_new_page(container, time_sleep, page)
