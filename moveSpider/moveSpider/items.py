# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovespiderItem(scrapy.Item):
		moveName = scrapy.Field()
		titleImage = scrapy.Field()
		classification = scrapy.Field()
		actor = scrapy.Field()
		year = scrapy.Field()
		imdbScore = scrapy.Field()
		doubanScore = scrapy.Field()
		director = scrapy.Field()
		country = scrapy.Field()
		summary = scrapy.Field()
		summaryImage = scrapy.Field()
		source = scrapy.Field()
class OpetaItem(object):
		operaName = scrapy.Field()
		actor = scrapy.Field()
		classification = scrapy.Field()
		summary = scrapy.Field()
		summaryImage = scrapy.Field()
		source = scrapy.Field()
