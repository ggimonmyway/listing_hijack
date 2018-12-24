from pymongo import MongoClient
conn = MongoClient('localhost', 27017)


class DealSql(object):
    def __init__(self):
        self.db = conn.followsell

    # 获取一个字典， 为所有的asin 及 售卖店家数
    # more 为可输入参数 即寻找number 大于 more 的字典
    # more为0 则获取全部 more为1 则获取被跟卖的
    def get_all_asin_number(self, more=0):
        eachAsinSaleNum = self.db.eachAsinSaleNum
        asin_number_list = {each['asin']: each['number'] for each in eachAsinSaleNum.find({'number': {'$gt': more}})}
        return asin_number_list

    # 如果已发送名单里面的asin的number变成1 则又开始进行检测
    def get_has_post(self):
        haspost = self.db.haspost
        eachAsinSaleNum = self.db.eachAsinSaleNum
        try:
            haspostlist = [i['asin'] for i in haspost.find()]
        except:
            haspostlist = []
        for asin in haspostlist:
            if eachAsinSaleNum.find_one({'asin': asin})['number'] == 1:
                haspost.remove({'asin': asin})

    # 输出还没发送的被跟卖的名单
    def output_asin(self):
        haspost = self.db.haspost
        isfollow_list = self.get_all_asin_number(1)
        try:
            haspostlist = [i['asin'] for i in haspost.find()]
        except:
            haspostlist = []

        need_posted = []
        for asin in isfollow_list:
            if asin not in haspostlist:
                need_posted.append(asin)
        return need_posted

    # 在每次发送过后
    # 把asin和商家数对应的数据清除掉
    # 开始新一轮的爬取
    def del_each_asin_number(self):
        eachAsinSaleNum = self.db.eachAsinSaleNum
        eachAsinSaleNum.remove()

    # 在asin 发送过后 将其写入数据库
    def has_post_asin(self):
        has_post = self.output_asin()
        haspost = self.db.haspost
        for asin in has_post:
            haspost.insert(asin)
