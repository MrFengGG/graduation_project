#encoding=utf-8
import scrapy
import re
import os
from moveSpider.items import MovespiderItem,OpetaItem
from lxml import html
class MoveSpider(scrapy.Spider):
	name = "dytt"
	allowed_domains = ["ygdy8.net"]
	start_urls = [
		"http://www.ygdy8.net/"
		]
	def __init__(self):
		super(MoveSpider,self).__init__()
		self.domain = "http://www.ygdy8.net"	
	def parseUrl(self,htmlBody):
		urls = []
		links = htmlBody.xpath(".//a/@href")		
		for link in links:
			if not link.startswith("http://"):
				link = self.domain + link
			urls.append(link)
		return urls
	def parseMove(self,html):
		content = re.search("<!--Content Start-->[\s\S]*/table",html)
		moveItem = None
		if content:
			text = content.group(0)
			moveName = re.search("译　　名(.*?)<br",text)
			if moveName:
				print("获得一部电影")
				#如果正则表达式匹配,为电影页面
				moveName = "".join(moveName.group(1).split())
				classification = re.search("类　　别(.*?)<br",text)
				if classification:
					classification = "".join(classification.group(1).split())
				actor = re.search("主　　演(.*?)<br",text)
				if actor:
					actor = "".join(actor.group(1).split())
				year = re.search("上映日期(.*?)<br",text)
				if year:
					year = "".join(year.group(1).split())
				imdbScore = re.search("IMDb评分(.*?)<br",text)
				if imdbScore:
					imdbScore = "".join(imdbScore.group(1).split())
				doubanScore = re.search("豆瓣评分(.*?)<br",text)
				if doubanScore:
					doubanScore = "".join(doubanScore.group(1).split())
				director = re.search("导　　演(.*?)<br",text)
				if director:
					director = "".join(director.group(1).split())
				country = re.search("产　　地(.*?)<br",text)
				if country:
					country = "".join(country.group(1).split())
				summary = re.search("简　　介(.*?)<img",text)
				if summary:
					summary = summary.group(1)
				source = re.search('(ftp://.*?)"',text)
				if source:
					source = source.group(1)
				images = re.findall("http.*?jpg",text)
				titleImage = images[0]
				summaryImage = None
				if len(images) >= 2:
					summaryImage = images[1]
				moveItem =  MovespiderItem(
					moveName = moveName,
					titleImage = titleImage,
					classification = classification,
					actor = actor,
					year = year,
					imdbScore = imdbScore,
					doubanScore = doubanScore,
					director = director,
					country = country,
					summary = summary,
					summaryImage = summaryImage,
					source = source)	
				return moveItem
			elif re.search("[剧名]:(.*?)<br",text):
				print("发现一部电视剧")
				operaName = "".join(re.search("[剧名]:(.*?)<br",text).group(1))
				actor = re.search("[演员]:(.*?)<br",text)
				if actor:
					actor = actor.group(1)
				classification = re.search("[类型]:(.*?)<br",text)
				if classification:
					classification = classification.group(1)
				summary = re.search("[简介]:(.*)?</",text)
				if summary:
					summary = summary.group(1)
				summaryImage = re.search("http.*jpg",text)
				source = re.search('(ftp://.*)"',text)
				if source:
					source = source.group(0)
				return OpetaItem(
					operaName = operaName,
					actor = actor,
					classification = classification,
					summary = summary,
					summaryImage = summaryImage,
					source = source)
	def parse(self,response):
		htmlBody = html.fromstring(response.body)
		urls = self.parseUrl(htmlBody)
		content = self.parseMove(response.body.decode("gbk"))
		if content:
			yield content
		for url in urls:
			yield scrapy.Request(url,callback=self.parse)		

