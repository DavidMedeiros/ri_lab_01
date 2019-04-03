# -*- coding: utf-8 -*-
import scrapy
import json

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class Brasil247Spider(scrapy.Spider):
	name = 'brasil_247'
	allowed_domains = ['brasil247.com']
	start_urls = []

	def __init__(self, *a, **kw):
		super(Brasil247Spider, self).__init__(*a, **kw)
		with open('seeds/brasil_247.json') as json_file:
			data = json.load(json_file)
		self.start_urls = list(data.values())

	def parse(self, response):
		links = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "section-column", " " ))]//a/@href').getall()

		for i in range(0, len(links), 2):
			yield response.follow(links[i], callback=self.parse_article_detail)
 

	def parse_article_detail(self, response):
		item= RiLab01Item()
		item['title'] = response.css('h1::text').get()
		item['sub_title'] = response.xpath('//p[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]/text()').get()
		item['author'] = response.css('.entry p::text, p a::text, entry span::text, strong::text').getall()[1]
		item['date'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "meta", " " ))]/text()').get()
		item['section'] = response.url.split('/')[5]
		brute_text = response.css('.entry p::text, p a::text, entry span::text, strong::text').getall()
		item['text'] =  self.format_text(brute_text)
		item['url'] = response.url
		yield item
        
	def format_text(self, text):
		formated_text = ''
		if (text != None):
			for i in range(2, len(text) - 1):
				formated_text = formated_text + text[i] + '\n'
			formated_text = formated_text + text[len(text) - 1]
			
			return formated_text
