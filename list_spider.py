import requests
import re
from pymongo import MongoClient
import random
conn = MongoClient('localhost', 27017)
db = conn.followsell
requests.packages.urllib3.disable_warnings()


class IsFollow(object):
    def __init__(self):
        """
        获取数据库asin信息
        生成对应的链接
        """
        demo_url = 'https://www.amazon.com/dp/%s?ie=UTF8&th=1&psc=1'
        self.user_agent = [
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            #"Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            #"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            #"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        ]

        self.all_asin_list = [i[0] for i in db.asin.find_one()['asin'].items()]
        self.all_urls_to_sc = (demo_url % asin for asin in self.all_asin_list)

        self.heavy_asin_list = [i[0] for i in db.heavyasin.find_one()['asin'].items()]
        self.heavy_urls_to_sc = (demo_url % asin for asin in self.heavy_asin_list)

    def output(self):
        for url in self.heavy_urls_to_sc:
            print(url)

    def get_html(self, url):
        try:
            headers = {'User-Agent': random.choice(self.user_agent)}
            html = requests.get(url, headers=headers, verify=False)
            # html.encoding = html.apparent_encoding # 可以写 没必要 编码一样 不用变 降低很多速度
            return html.text
        except:
            pass

    # 或许正在销售此商品的卖家数
    def get_sale_number(self, url):
        html_text = self.get_html(url)
        sale_number = re.findall(r'\((.*?)\) from', html_text)[0]
        return sale_number

    # 将asin对应卖家数插入数据库
    # 第一步为正常构造的链接能用时 第二步为链接不能用时 要将尾部替换
    # 如果还获取不到 就是没有 应该报错 补零
    # eachAsinSaleNum = db.eachAsinSaleNum 参数为要插入的数据库
    def insert_mongo(self, AsinSaleNum, urls_to_sc, asin_list):
        number_list = []
        for url in urls_to_sc:
            print(url)
            try:
                number_list.append(self.get_sale_number(url))  # 有一些可能在里面出现异常 写入为1 以后好查看
            except:
                try:
                    urlsp = url.split('?')
                    urlsp[-1] = '/ref=dp_prsubs_1'
                    url = ''.join(urlsp)
                    number_list.append(self.get_sale_number(url))
                except:
                    number_list.append(0)
        for asin, number in zip(asin_list, number_list):
            AsinSaleNum.insert({'asin': asin, 'number': int(number)})

    def insert_all_mongo(self):
        eachAsinSaleNum = db.eachAsinSaleNum
        self.insert_mongo(eachAsinSaleNum, self.all_urls_to_sc, self.all_asin_list)

    def insert_heavy_mongo(self):
        heavyAsinSaleNum = db.heavyAsinSaleNum
        self.insert_mongo(heavyAsinSaleNum, self.heavy_urls_to_sc, self.heavy_asin_list)
