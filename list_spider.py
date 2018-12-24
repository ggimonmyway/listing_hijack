import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
conn = MongoClient('localhost', 27017)
db = conn.followsell


class IsFollow(object):
    def __init__(self):
        """
        获取数据库asin信息
        生成对应的链接
        """
        self.headers = {'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        self.asin_list = db.asin.find_one()['asin']
        demo_url = 'https://www.amazon.com/dp/%s?ie=UTF8&th=1&psc=1'
        self.urls_to_sc = (demo_url % asin for asin in self.asin_list)

    def output(self):
        for url in self.urls_to_sc:
            print(url)

    def get_html(self, url):
        try:
            html = requests.get(url, headers=self.headers)
            # html.encoding = html.apparent_encoding # 可以写 没必要 编码一样 不用变 降低很多速度
            return html.text
        except:
            pass

    # 或许正在销售此商品的卖家数
    def get_sale_number(self, url):
        html_text = self.get_html(url)
        soup = BeautifulSoup(html_text, 'lxml')
        text = soup.select('#olp-upd-new > span > a')[0].text
        sale_number = text.split('(')[-1].split(')')[0]
        return sale_number

    def insert_mongo(self):
        number_list = []
        eachAsinSaleNum = db.eachAsinSaleNum
        for url in self.urls_to_sc:
            number_list.append(self.get_sale_number(url))
        for asin, number in zip(self.asin_list, number_list):
            eachAsinSaleNum.insert({'asin': asin, 'number': int(number)})
