import xlrd
from pymongo import MongoClient
conn = MongoClient('localhost', 27017)
db = conn.followsell


# 这个模块用来处理excel表格 对数据进行初始化
# 其中可能会存在asin重复的情况
# 这时候要查看sku 只存入sku最长的那个 因为最后面有 “-g” 代表了跟卖
def handleExcel(filePath):
	book = xlrd.open_workbook(filePath)
	sh = book.sheet_by_index(0)
	cols = sh.ncols
	rows = sh.nrows
	sku_list = []
	asin_list = []
	for r in range(rows):
		sku_list.append(sh.cell_value(rowx=r, colx=0).strip())
		asin_list.append(sh.cell_value(rowx=r, colx=1).strip())
	sku_list = sku_list[1:]
	asin_list = asin_list[1:]
	asinDict = {}
	for asin, sku in zip(asin_list, sku_list):
		old = asinDict.get(asin, '')
		if len(sku) > len(old):
			asinDict[asin] = sku
	asin = db.asin
	if asin.find_one({'flag': 'zj'}):
		pass
	else:
		asin.insert({'flag': 'zj', 'asin': []})
	asin.update({'flag': 'zj'}, {'$set': {'asin': asinDict}})


# 在所有的基础上抽取出比较重要的那部分
def makeHeavyAsin():
	keys = ['ME5-0002', 'ME5-0010', 'ME5-0012', 'ME5-0062']
	heavyAsinDict = {}
	asinDict = db.asin.find_one()['asin']
	print(asinDict)
	heavyasin = db.heavyasin
	for key in keys:
		heavyAsinDict.update({item[0]: item[1] for item in asinDict.items() if key in item[1]})
	heavyasin.update({'flag': 'zj'}, {'$set': {'asin': heavyAsinDict}})


if __name__ == '__main__':
	"""
	handleExcel('子ASIN-2018.12.26-Iris.xlsx')
	"""
	makeHeavyAsin()
