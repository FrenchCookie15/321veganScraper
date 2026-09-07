from pathlib import Path
import re
import json
import scrapy
from supermarket.items import SupermarketItem

class CarrefourSpider(scrapy.Spider):
    name = "carrefour"
    product = SupermarketItem()

    # We search for the EAN of the product
    async def start(self):
        yield scrapy.http.JsonRequest(
            url="https://www.carrefour.fr/autocomplete?q="+self.ean+"&maxResults=1&productCard=true",
            headers= {
                "x-requested-with": "XMLHttpRequest"
            },
            callback=self.parseProductURL
        )

    # From the response of the search, we get the URL of the product's page
    def parseProductURL(self, response):
        jsonResponse = json.loads(response.text)
        # Exit if there is no result
        if 'products' not in jsonResponse['data']:
            print(None)
            return None

        # We always take the first result, there should be only one result anyway
        next_page = jsonResponse['data']['products'][0]['links']['self']
        if next_page is None:
            print(None)
            return None
        
        yield response.follow(next_page, callback=self.parseIngredients)

    # From the product's page, we scrape the ingredients list
    def parseIngredients(self, response):
        ingredients = response.xpath('//*[@id="product-ingredients"]/div[2]/div/div').get()
        cleanIngredients = ingredients

        # If the product does have some ingredients (a vaccum cleaner does not)
        if ingredients is not None:
            # There are usually some unnecessary HTML markings like <b> and <p>
            # we remove them with a regular expression
            cleanIngredients = re.sub(r"<.*?>", " ", ingredients)

        self.product.ingredients = cleanIngredients
        self.product.imageURL = response.xpath('//*[@id="data-produit-image"]/div[2]/div/ul/li/img/@src').get()
        self.product.name = response.xpath('//*[@id="product-title-desktop"]/div[1]/h1/text()').get()
        if '"brand":["' in response.text and '"]},"facets":[]' in response.text:
            self.product.brand = response.text.split('"brand":["', 1)[1].split('"]},"facets":[]', 1)[0]

        print(self.product)

