import pandas as pd
import numpy as np
from diorspider.spiders.spider import DiorSpider
from scrapy.crawler import CrawlerProcess
import time
import logging

def make_test():
	df = pd.read_csv('base.csv')

	region_fr = df['region'] == 'France'
	region_us = df['region'] == 'USA'

	fr_data = df[region_fr]
	us_data = df[region_us]

	sum_fr = np.sum(region_fr)
	sum_us = np.sum(region_us)

	print('NOTE: Here is full sum of all products')
	print('So one product which have 3 differend "ml"')
	print('will give 3 differend products')
	print('---------------')
	print("full products in USA/France: {}/{}".format(sum_us, sum_fr))
	print('---------------')
	print('currency check...')

	curr_fr = fr_data[fr_data['product_currency'] != 'EUR']
	curr_us = us_data[us_data['product_currency'] != 'USD']
	if curr_fr.empty:
		print("The currency of France is ok")
	else:
		print(curr_fr)
	if curr_us.empty:
		print("The currency of USA is ok")
	else:
		print(curr_us)

	print('---------------')
	print('procent check...')

	size_proc = (np.shape(df['product_size'].dropna())[0] + 1) / (np.shape(df)[0] + 1) * 100
	color_proc = (np.shape(df['product_color'].dropna())[0] + 1) / (np.shape(df)[0] + 1)* 100
	description_proc = (np.shape(df['product_description'].dropna())[0] + 1) / (np.shape(df)[0] + 1) * 100

	print('The procent of size is {}%'.format(size_proc))
	print('The procent of color is {}%'.format(color_proc))
	print('The procent of descripton is {}%'.format(description_proc))


if __name__ == '__main__':

	process = CrawlerProcess({
		'ITEM_PIPELINES' : {
					'diorspider.pipelines.DiorspiderPipeline': 300,
					}
		})


	process.crawl(DiorSpider)
	process.start()
	
	make_test()

