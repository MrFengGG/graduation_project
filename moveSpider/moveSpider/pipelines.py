#coding=utf-8

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from moveSpider.items import MovespiderItem,OpetaItem
class MovespiderPipeline(object):
		def __init__(self):
			self.client = pymongo.MongoClient(host="127.0.0.1",port=27017)
			self.db = self.client['film']
			self.move = self.db['move']
			self.opera = self.db['opera']
		def process_item(self, item, spider):
			if isinstance(item,MovespiderItem):
				try:
					self.move.insert(dict(item))
					print("插入一部电影")
				except Exception as e:
					print("电影已存在"+str(e))
			if isinstance(item,OpetaItem):
				try:
					self.opera.insert(dict(item))
					print("插入一部电视剧")
				except:
					print("电视剧已存在")
