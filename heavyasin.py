from HeavyDealSql import HeavyDealSql
from list_spider import IsFollow
import time

if __name__ == '__main__':
    while True:
        start = time.time()
        isf = IsFollow()
        isf.insert_heavy_mongo()  # 占时最长的一部分 看情况 不知道要不要移除到外面 获取asin 然后抓取页面 直接入库
        deal = HeavyDealSql()
        output_asin = deal.output_asin()    # 从爬取的信息和已发送的信息进行对比 把没有发送的发送出去
        deal.get_has_post()  # 获取已发送的asin 如果在新一轮的爬取中 没有跟卖了 就应该从已发送中取出
        text = '   '.join(output_asin)
        with open('heavyasin.text', 'w') as f:
            f.write(text)
        deal.has_post_asin()    # 把发送的asin保存到数据库中
        deal.del_each_asin_number()  # 删除掉全部爬取的数据 等待新一轮的爬取
        end = time.time()
        until_time = end-start
        print(until_time)
        if until_time < 3600:
            time.sleep(3600 - until_time)
