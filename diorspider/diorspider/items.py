# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DiorspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_name = scrapy.Field()
    product_price = scrapy.Field()
    product_currency = scrapy.Field()
    product_SKU = scrapy.Field()
    product_instock = scrapy.Field()
    crawl_time = scrapy.Field()
    product_color = scrapy.Field()
    product_category = scrapy.Field()
    product_size = scrapy.Field()
    region = scrapy.Field()
    product_description = scrapy.Field()
