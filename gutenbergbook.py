import requests as req
import os
import re
import random
from bs4 import BeautifulSoup as bs

# 建立目錄
folderPath = 'books'
if not os.path.exists(folderPath):
    os.makedirs(folderPath)

# 自訂標頭
my_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 取得中文書籍列表
url = 'https://www.gutenberg.org/browse/languages/zh'
res = req.get(url, headers=my_headers)
soup = bs(res.text, 'lxml')

bookLinks = []
for li in soup.select('li.pgdbetext'):
    a = li.find('a')
    link = 'https://www.gutenberg.org' + a['href']
    title = a.text
    bookLinks.append((title, link))

# 隨機取得  本書籍下載
random.shuffle(bookLinks)
count = 0
for idx, (title, link) in enumerate(bookLinks, 1):
    try:
        # 取得書籍內容頁面
        res = req.get(link, headers=my_headers)
        soup = bs(res.text, 'lxml')

        # 取得內容下載連結
        contentLink = None
        for a in soup.select('a'):
            if 'Plain Text UTF-8' in a.text:
                contentLink = a.get('href')
                if 'www.gutenberg.org' not in contentLink:
                    contentLink = 'https://www.gutenberg.org' + contentLink
                break
        
        if contentLink is None:
            print(f'找不到 {title} 的內容下載連結')
            continue
        
        # 下載書籍內容
        res = req.get(contentLink, headers=my_headers)
        content = res.content.decode('utf-8')

        # 篩選中文內文
        pattern = r'[\u4e00-\u9fff，。；：「」『』【】《》]+'
        content_chinese = ''.join(re.findall(pattern, content))

         # 如果篩選後內容為空就不進行存檔的動作，也不算入計數器
        if not content_chinese:
            print(f'[{count}] {title} 中文內容為空，不進行存檔')
            continue

        # 檢查是否已有同名的檔案存在
        filePath = f'{folderPath}/{title}.txt'
        if os.path.exists(filePath):
            print(f'[{count}] {title} 已下載過，不重複下載')
            continue

        # 存檔
        filePath = f'{folderPath}/{title}.txt'  # 修改檔名為書籍名稱
        with open(filePath, 'w', encoding='utf-8') as f:  # 使用 utf-8 編碼儲存
            f.write(content_chinese)
            
            print(f'[{count+1}] {title} 下載完成')
            count += 1

        if count >= 230:
            break

    except Exception as e:
        print(f'下載 {title} 失敗: {e}')