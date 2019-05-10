# -*- coding: utf-8 -*-
import csv
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

class DiorspiderPipeline(object):

	def open_spider(self, spider):
		self.file = open('base.csv', 'w')
		fieldnames = ['product_name', 'product_price', 'product_currency',
			'product_SKU', 'product_instock', 'crawl_time', 'product_color', 
			'product_category', 'product_size', 'region', 'product_description']
		self.writer = csv.DictWriter(self.file, fieldnames=fieldnames)
		self.writer.writeheader()

	def close_spider(self, spider):
		self.file.close()

	def process_item(self, item, spider):
		self.writer.writerow({'product_name': item['product_name'], 
						'product_price': item['product_price'],
						'product_currency': item['product_currency'],
						'product_SKU': item['product_SKU'],
						'product_instock': item['product_instock'],
						'crawl_time': item['crawl_time'],
						'product_color': item['product_color'],
						'product_category': item['product_category'],
						'product_size': item['product_size'],
						'region': item['region'],
						'product_description': item['product_description']})
		return item