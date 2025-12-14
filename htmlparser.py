import requests
from bs4 import BeautifulSoup
import pandas as pd
url = "http://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
books = []
for item in soup.find_all('article', class_='product_pod'):
    title = item.find('h3').find('a')['title']
    price = item.find('p', class_='price_color').text
    books.append({'Название': title, 'Цена': price})
pd.DataFrame(books).to_excel('books.xlsx', index=False)
