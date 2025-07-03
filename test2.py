# https://cy-grimoire.netlify.app/items
from bs4 import BeautifulSoup
import requests

url = 'https://cy-grimoire.netlify.app/items'
web = requests.get(url)                        # 取得網頁內容
soup = BeautifulSoup(web.text, "html.parser")
print(soup)