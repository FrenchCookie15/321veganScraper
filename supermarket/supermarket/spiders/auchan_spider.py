from pathlib import Path

import re
import scrapy
from supermarket.items import SupermarketItem

class AuchanSpider(scrapy.Spider):
    name = "auchan"
    product = SupermarketItem()

    # We search for the EAN of the product
    async def start(self):
        yield scrapy.Request(url="https://www.auchan.fr/recherche?text="+self.ean, callback=self.parseProductURL)

    # From the response of the search, we get the URL of the product's page
    def parseProductURL(self, response):
        next_page = response.xpath('//*[@id="wrapper"]/div[5]/article/div[2]/a/@href').get()
        
        # Exit if there is no result
        if next_page is None:
            print(None)
            return None

        yield response.follow(next_page, callback=self.parseIngredients)


    def parseIngredients(self, response):
        ingredients = response.xpath('//*[@id="product-features"]/div/div//text()[contains(.,"Ingrédients")]/../../div/span').get()
        cleanIngredients = ingredients

        # If the product does have some ingredients (a vaccum cleaner does not)
        if ingredients is not None:
            # There are usually some unnecessary HTML markings like <b> and <p>
            # we remove them with a regular expression
            cleanIngredients = re.sub(r"<.*?>", "", ingredients)
        
        self.product.ingredients = cleanIngredients
        self.product.brand = response.xpath('//*[contains(@class, "offer-selector__brand")]/text()').get()
        self.product.name = response.xpath('//*[contains(@class, "offer-selector__name--large")]/h1/text()').get()
        self.product.imageURL = response.xpath('//*[contains(@class, "galleryItem")]/img/@src').get()
        
        print(self.product)

