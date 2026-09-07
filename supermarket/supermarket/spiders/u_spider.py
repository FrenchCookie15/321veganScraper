from pathlib import Path

import re
import scrapy
from supermarket.items import SupermarketItem

class USpider(scrapy.Spider):
    name = "u"
    product = SupermarketItem()

    # We search for the EAN of the product
    async def start(self):
        yield scrapy.Request(url="https://www.coursesu.com/on/demandware.store/Sites-DigitalU-Site/fr_FR/Search-GetSuggestions?q="+self.ean, callback=self.parseProductURL)

    # From the response of the search, we get the URL of the product's page
    def parseProductURL(self, response):
        next_page = response.xpath('//*[@class="product-tile-link"]/@href').get()
        # print(next_page)
        # Exit if there is no result
        if next_page is None:
            print(None)
            return None

        yield response.follow(next_page, callback=self.parseIngredients)


    def parseIngredients(self, response):
        ingredients = response.xpath('//*[@id="product-details"]/div[1]/div/div/ul/li[2]/p/text()').get()
        cleanIngredients = ingredients

        # If the product does have some ingredients (a vaccum cleaner does not)
        if ingredients is not None:
            # There are usually some unnecessary HTML markings like <b> and <p>
            # we remove them with a regular expression
            cleanIngredients = re.sub(r"<.*?>", "", ingredients)
        
        self.product.ingredients = cleanIngredients
        self.product.name = response.xpath('//*[contains(@class, "pdp-product-name ")]/text()').get().split('\n\n\n    ')[1].split(' \n\n\n')[0]
        self.product.imageURL = response.xpath('//*[contains(@class, "main-image")]/picture/img/@src').get()

        print(self.product)

