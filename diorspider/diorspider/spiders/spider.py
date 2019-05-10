from scrapy.spiders import CrawlSpider
from ..items import DiorspiderItem
import datetime
import re
from pprint import pprint
import json
from scrapy.selector import Selector
import logging
from scrapy.utils.log import configure_logging

class DiorSpider(CrawlSpider):
	name = 'diorspider'

	start_urls = [
		'https://www.dior.com/en_us/',
		'https://www.dior.com/fr_fr/'
	]

	# to save log
	configure_logging(install_root_handler=False)
	logging.basicConfig(
    	filename='log.txt',
		format='%(levelname)s: %(message)s',
		level=logging.INFO
	)

	def parse_start_url(self, response):
		# take navigation block
		navigation_block = response.css('.navigation-items')

		# take all ulrs with contain all-links(like all-product, etc.)
		allproduct_urls = self.take_allproduct_liks(navigation_block) 
		# take all urls without alll-links
		withoutall_ulrs = self.take_links_without_all(navigation_block)

		base = 'https://www.dior.com'
		# lets start to parse products
		# for each url in all-links
		for url in allproduct_urls:
			# base of ulr
			new_url = base + url
			# follow the link which contain all products with all categories
			yield response.follow(url=new_url, callback=self.parse_all_link)

		for urls in withoutall_ulrs:
			for url in urls:
				new_url = base + url
				yield response.follow(url=new_url, callback=self.parse_withoutall_link)

	def parse_withoutall_link(self, response):
		"""
		1. Take all product links
		2. parse product
		"""
		# take all links with products
		links = response.css('.product-link').xpath('@href').getall()
		
		base = 'https://www.dior.com'

		# for each link	
		for link in links:
			if 'collection' in link:
				continue
			new_url = base + link
			yield response.follow(url=new_url, callback=self.parse_page)


	def parse_all_link(self, response):
		"""
		take all links with products
		and follow it
		"""
		
		blocks = response.css('div .grid-view')

		base = 'https://www.dior.com'
		# for each block
		for block in blocks:
			# take all links form category block
			product_links = block.css('.product-link').xpath('@href').getall()
			# follow each link
			for url in product_links:
				new_url = base + url
				yield response.follow(url=new_url, callback=self.parse_page)


	def find_needed_json(self, response):
		"""
		1. Take full body HTML
		2. Take only scripts
		3. Find needed script
		4. Cut it for JSON
		5. Find needed JSON block
		6. Return in
		"""

		# take all js scripts
		all_scripts = response.css('script')
		
		# find needed script with full info
		for script in all_scripts:
			if script.get().find('window.initialState') > 0:
				needed_script = script

		# take the data of the script
		script_data = needed_script.get()

		# find start and end pos of the script
		json_start_pos = script_data.find('{')
		json_end_pos = script_data.rindex('}')

		# cut the script
		tmp = script_data[json_start_pos:json_end_pos + 1]

		# convert to json
		my_json = json.loads(tmp)

		# take all elements from page
		try:
			elements = my_json['CONTENT']['cmsContent']['elements']
		except:
			return [], []
		#find product info block
		variation_json = []
		description_json = []
		for element in elements:
			# i dont know why, but sometimes
			# it contains empty list
			if type(element) != type({}):
				continue
			if element['type'] == 'PRODUCTVARIATIONS' or element['type'] == 'PRODUCTUNIQUE':
				variation_json = element
			if element['type'] == 'PRODUCTSECTIONDESCRIPTION':
				description_json = element
		if description_json == []:
			return variation_json, []
		return variation_json, description_json['sections']


	def parse_size(self, my_json,
						_sku,
						_price,
						_instock,
						_sizes,
						_name,
						_color):
		try:
			_name = my_json[0]['tracking'][0]['ecommerce']['add']['products'][0]['name']
			_price = [str(my_json[0]['price']['value'])]
			_color = my_json[0]['tracking'][0]['ecommerce']['add']['products'][0]['variant']
			for needed_json in my_json:
				_sku.append(needed_json['sku'])
				size = needed_json['detail']
				if 'Taille' in size:
					size = size.replace('Taille : ', '')
				elif 'Size' in size:
					size = size.replace('Size : ', '')
				_sizes.append(size)
				if needed_json['status'] == 'AVAILABLE':
					_instock.append(True)
				else:
					_instock.append(False)
		except:
			return _sku, _price, _instock, _sizes, _name, _color
		return _sku, _price, _instock, _sizes, _name, _color


	def parse_capaciry(self, my_json,
						_sku,
						_price,
						_instock,
						_sizes,
						_name,
						_color):
		try:
			_name = my_json[0]['tracking'][0]['ecommerce']['add']['products'][0]['name']
			_instock = [True]

			for needed_json in my_json:
				# take sku
				_sku.append(needed_json['sku'])
				# take price
				_price.append(str(needed_json['price']['value']))
				# take size
				_sizes.append(needed_json['tracking'][0]['ecommerce']['add']['products'][0]['variant'])
		except:
			return _sku, _price, _instock, _sizes, _name, None
		return _sku, _price, _instock, _sizes, _name, None


	def parse_swatch(self, my_json,
						_sku,
						_price,
						_instock,
						_sizes,
						_name,
						_color):
		try:
			_name = my_json[0]['tracking'][0]['ecommerce']['add']['products'][0]['name']
			_price = [str(my_json[0]['price']['value'])]
			_instock = [True]
			for needed_json in my_json:
				# take sku
				_sku.append(needed_json['sku'])
				# take color
				_color.append(needed_json['title'])
		except:
			return _sku, _price, _instock, None, _name, _color
		return _sku, _price, _instock, None, _name, _color

	def parse_uniq(sku, my_json,
						_sku,
						_price,
						_instock,
						_sizes,
						_name,
						_color,
						_category,
						_currency):
		try:
			_price = [str(my_json['price']['value'])]
			_sku = [my_json['sku']]
			_currency = my_json['price']['currency']
			_color = my_json['tracking'][0]['ecommerce']['add']['products'][0]['variant']
			_name = my_json['tracking'][0]['ecommerce']['add']['products'][0]['name']
			_category = my_json['tracking'][0]['ecommerce']['add']['products'][0]['category']
			if my_json['status'] == 'AVAILABLE':
				_instock = [True]
			else:
				_instock = [False]
		except:
			return _category, _currency, _sku, _price, _instock, None, _name, _color
		return _category, _currency, _sku, _price, _instock, None, _name, _color

	def parse_another(self, my_json,
						_sku,
						_price,
						_instock,
						_sizes,
						_name,
						_color):
		try:
			_sku = [my_json[0]['sku']]
			_price = [str(my_json[0]['price']['value'])]
			if my_json[0]['status'] == 'AVAILABLE':
				_instock = [True]
			else:
				_instock = [False]
			_name = my_json[0]['tracking'][0]['ecommerce']['add']['products'][0]['name']
			_color = my_json[0]['tracking'][0]['ecommerce']['add']['products'][0]['variant']
		except:
			return _sku, _price, _instock, None, _name, _color
		return _sku, _price, _instock, None, _name, _color

	def parse_page(self, response):
		"""
		Parse product page
		Take the:
			- product_color (цвет)
 			- crawl_time (время сбора)
			- product_category (категория)
 			- region (регион)
			- product_name (название)
 			- product_SKU (SKU)
			- product_price (цена)
 			- product_currency (валюта)
 			- product_instock (наличие)
 			- product_size (размер)
			- product_description (описание)
		"""
	
		# get json with full info
		variation_jsons, description_json = self.find_needed_json(response)
		if variation_jsons == []:
			return
		items = DiorspiderItem()
		_description = []

		# take region
		_region = ''
		if 'en_us' in response.url:
			_region = 'USA'
		elif 'fr_fr' in response.url:
			_region = 'France'

		# take description
		for needed_json in description_json:
			if 'TEXT' != needed_json['type']:
				continue
			text = Selector(text=needed_json['content'])
			text = text.css('::text').getall()
			_description.append(' '.join(text))

		# take crawl time
		_crawl_time = datetime.datetime.now().strftime('%H:%M:%S')

		_sku = []
		_price = []
		_instock = []
		_sizes = []
		_name = []
		_color = []
		_category = ''
		_currency = ''

		# if its uniq category
		if variation_jsons['type'] == 'PRODUCTUNIQUE':
			_category, _currency, _sku, _price, _instock, _sizes, _name, _color = self.parse_uniq(variation_jsons,
																								_sku,
																								_price,
																								_instock,
																								_sizes,
																								_name,
																								_color,
																								_category,
																								_currency)
		else:
			# take a variation tipe for right parse colour/size/etc
			variation_type = variation_jsons['variationsType']

			# take only product info
			variation_jsons = variation_jsons['variations']

			# take category
			_category = variation_jsons[0]['tracking'][0]['ecommerce']['add']['products'][0]['category']
		
			# take currency
			_currency = variation_jsons[0]['price']['currency']

			if variation_type == 'SIZE':
				_sku, _price, _instock, _sizes, _name, _color = self.parse_size(variation_jsons,
																				_sku,
																				_price,
																				_instock,
																				_sizes,
																				_name,
																				_color)
			elif variation_type == 'CAPACITY':
				_sku, _price, _instock, _sizes, _name, _color = self.parse_capaciry(variation_jsons,
																					_sku,
																					_price,
																					_instock,
																					_sizes,
																					_name,
																					_color)
			elif variation_type == 'SWATCH':
				_sku, _price, _instock, _sizes, _name, _color = self.parse_swatch(variation_jsons,
																					_sku,
																					_price,
																					_instock,
																					_sizes,
																					_name,
																					_color)
			else:
				_sku, _price, _instock, _sizes, _name, _color = self.parse_another(variation_jsons,
																						_sku,
																						_price,
																						_instock,
																						_sizes,
																						_name,
																						_color)

		items['product_name'] =  _name
		items['product_price'] = _price
		items['product_currency'] = _currency
		items['product_SKU'] = _sku
		items['product_instock'] = _instock
		items['crawl_time'] = _crawl_time
		items['product_color'] = _color
		items['product_category'] = _category
		items['product_size'] = _sizes
		items['region'] = _region
		items['product_description'] = _description
		return items

		


	def take_allproduct_liks(self, response):
		"""
		Take a navigation block and extract all links
		with 'all-' tag(like All Product, etc)
		and return it
		"""

		# take all links
		all_a = response.css('a')
		# list which will be contain new links
		link_list = []
		# for each link form navigation block
		for idx,a in enumerate(all_a):
			# if span text is like 'All ...'
			label = a.css('span::text').get()
			if 'All ' in label[:3] or 'Tou' in label[:3]:
				# append this link to list
				link_list.append(a.xpath('@href').get())

		return link_list


	def take_links_without_all(self, response):
		"""
		Not all sub-blocks in navigation block have a all-link
		So i take all links from block which have no all-link
		and return it
		"""

		# take all ul's from navigation block
		navigation_ul = response.xpath('//*[contains(concat( " ", @class, " " ),\
											 concat( " ", "navigation-item", " " ))]//ul')
		# list which will be contain new links
		needed_uls = []
		# for each ul in full list of ul's
		for ul in navigation_ul:
			# take a list of span-text which will check(has all-link or not)
			names = ul.css('span::text').getall()
			# if is_good value will not changing after check - that selector with ul
			# will append
			is_good = True
			# for each category name in categories
			for name in names:
				# if category like 'All shoes', 'All ready-to-wear', etc or 'New arrivals'
				if 'All ' in name[:3] or 'New ' in name[:3] or 'Tou' in name[:3] or 'collection' in name:
					# change value(if its change we should not append this link)
					is_good = False
					break
			if is_good:
				needed_uls.append(ul.css('a').xpath('@href').getall())
		return needed_uls
