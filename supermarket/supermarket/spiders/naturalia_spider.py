from pathlib import Path
import re
import json
import scrapy
from supermarket.items import SupermarketItem

class NaturaliaSpider(scrapy.Spider):
    name = "naturalia"
    product = SupermarketItem()

    # We search for the EAN of the product
    async def start(self):
        yield scrapy.http.JsonRequest(
            url="https://www.naturalia.fr/search/ajax/suggest?q="+self.ean+"&_=1788338983783",
            callback=self.parseProductURL
        )

    # From the response of the search, we get the URL of the product's page
    def parseProductURL(self, response):
        jsonResponse = json.loads(response.text)

        # Exit if there is no result
        if len(jsonResponse) == 0:
            print(None)
            return None
        
        # We always take the first result, there should be only one result anyway
        next_page = jsonResponse[0]['url']
        if next_page is None:
            print(None)
            return None
        
        yield response.follow(next_page, callback=self.parseIngredients)

    # From the product's page, we scrape the ingredients list
    def parseIngredients(self, response):
        ingredients = response.xpath('//*[@id="ingredients_info"]/div[1]/p[1]').get()
        cleanIngredients = ingredients
        # If the product does have some ingredients (a vaccum cleaner does not)
        if ingredients is not None:
            # There are usually some unnecessary HTML markings like <b> and <p>
            # we remove them with a regular expression
            cleanIngredients = re.sub(r"<.*?>", "", ingredients)

        self.product.ingredients = cleanIngredients
        self.product.brand = response.xpath('//*[contains(@class, "brand")]/text()').get()
        self.product.name = response.xpath('//*[contains(@class, "typology")]/p/text()').get()
        if 'https://media.naturalia.fr/media/catalog/product/cache/' in response.text and '.jpg' in response.text:
            middleURL = response.text.split('https://media.naturalia.fr/media/catalog/product/cache/', 1)[1].split(self.ean+'.jpg', 1)[0]
            self.product.imageURL = ('https://media.naturalia.fr/media/catalog/product/cache/'+middleURL+self.ean+'.jpg')
        print(self.product)

