針對性的爬蟲腳本

首先執行
``
python main.py
``
進行第一遍的爬取，爬取的結果放在result.txt中

由於爬取頁面不穩定，因此有些頁面上的元素不能被正常訪問並下載下來。因此要打印爬取失敗的元素信息到main.log文件中，方便第二輪爬取。

第一遍結束後，運行
`python get_error_page.py`用來從日誌中獲取第一輪爬取失敗的元素並直接通過網址訪問並下載。這一次得到的數據都放在error.txt文件中。

第二輪之後如果沒有爬取錯誤，就運行
`python delete_lines.py`刪除result.txt中爬取失敗的元素所在的行。

最後，手動將errors.txt中的數據append在result.txt文件的下方。