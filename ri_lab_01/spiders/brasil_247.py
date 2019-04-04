# -*- coding: utf-8 -*-
import scrapy
import json

from ri_lab_01.items import RiLab01Item


class Brasil247Spider(scrapy.Spider):
	name = 'brasil_247'
	allowed_domains = ['brasil247.com']
	start_urls = []

	def __init__(self, *a, **kw):
		super(Brasil247Spider, self).__init__(*a, **kw)
		with open('seeds/brasil_247.json') as json_file:
			data = json.load(json_file)
		self.start_urls = list(data.values())

	months = {"Jan": "01", "Fev": "02", "Mar": "03",
			  "Abr": "04", "Mai": "05", "Jun": "06", "Jul": "07",
			  "Ago": "08", "Set": "09", "Out": "10",
			  "Nov": "11", "Dez": "12", }

	def parse(self, response):
		"""
            Crawl seed and find links to other articles
        """
		links = response.css('h3 a::attr(href)').getall()[2:]
		main_article = response.css('h2 a::attr(href)').get()

		links.append(main_article)

		# Follow found links to capture details about the articles
		for i in range(0, len(links)):
			yield response.follow(links[i], callback=self.parse_article_detail)

	def parse_article_detail(self, response):
		"""
        Crawls article and get informations from it

        :param response: HTML code of article page
        :return: Item to include in CSV
        """
		item = RiLab01Item()

		item['title'] = response.css('h1::text').get()

		item['sub_title'] = response.xpath('//p[(((count(preceding-sibling::*) + 1) = 4) and parent::*)]/text()').get()

		formatted_author = self.format_author(response.css('section p strong::text, strong a::text').get())
		item['author'] = formatted_author

		formatted_date = self.format_date(
			response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "meta", " " ))]/text()').get())
		item['date'] = formatted_date

		item['section'] = response.url.split('/')[5]

		formatted_text = self.format_text(
			response.css('.entry p::text, p span::text, p a::text, entry span::text, strong::text').getall())
		item['text'] = formatted_text

		item['url'] = response.url

		yield item

	def format_text(self, texts):
		"""
        Join the texts paragraphs with white space

        :param text: Receives a list of paragraphs from text
        :return: Returns the formatted article text. The author is included in
         the text, because in the site it belongs to the text article.
        """
		formatted_text = ''
		if texts is not None:
			for i in range(1, len(texts) - 1):
				formatted_text = formatted_text + texts[i] + ' '
			formatted_text = formatted_text + texts[len(texts) - 1]

		return formatted_text

	def format_author(self, author_text):
		"""
        Remove noises from author text

        :param author_text: Receives an author name with special characters in the end
        :return: Returns an author name without some special characters
        in the end: '-' or ','
        """
		dash_split = author_text.split('-')
		comma_split = author_text.split(',')

		if len(dash_split) > 1:
			return dash_split[0]
		elif len(comma_split) > 1:
			return comma_split[0]
		else:
			return author_text

	def format_date(self, text_date):
		"""
        Change the date format

        :param text_date: Receives a date in the format 'DD de Month de YYYY HH:MM'
        :return: Returns a date following the new format "DD/MM/YYYY HH:MM:00"
        """
		splitted_date = text_date.split(' ')
		day = splitted_date[0]
		if len(day) < 2:
			day = '0' + day
		month = self.months[splitted_date[2][0:3]]
		year = splitted_date[4]
		hour = splitted_date[6].split('\n')[0]

		return day + '/' + month + '/' + year + ' ' + hour + ":00"