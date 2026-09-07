# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class SupermarketItem:
    brand: str | None = None
    name: str | None = None
    imageURL: str | None = None
    ingredients: str | None = None
