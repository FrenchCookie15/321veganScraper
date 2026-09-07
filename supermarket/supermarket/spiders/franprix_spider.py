from pathlib import Path
import re
import json
import scrapy
from supermarket.items import SupermarketItem

class FranprixSpider(scrapy.Spider):
    name = "franprix"
    product = SupermarketItem()

    # We search for the EAN of the product
    async def start(self):
        yield scrapy.http.JsonRequest(
            url="https://api.rcdss.franprix.fr/rest/api/promotion?displayStartDate[before]=today&endDate[after]=today&search="+self.ean+"&itemsPerPage=16&page=1&return=light",
            headers= {
                "x-retailer-name": "franprix"
            },
            callback=self.parseProductURL
        )

    # From the response of the search, we get the URL of the product's page
    def parseProductURL(self, response):
        jsonResponse = json.loads(response.text)

        # Exit if there is no result
        if len(jsonResponse['items']) == 0:
            print(None)
            return None

        # We always take the first result, there should be only one result anyway
        next_page = jsonResponse['items'][0]['product']['metaTags']['seoUrl']
        if next_page is None:
            print(None)
            return None
        
        yield scrapy.Request(url="https://www.franprix.fr/promotion/"+next_page, callback=self.parseIngredients)

    # From the product's page, we scrape the ingredients list
    def parseIngredients(self, response):
        ingredients = response.xpath('//*[@id="__layout"]/div/div[2]/div/div[2]/div/div/div[6]/div/div[1]/div[2]/text()').get()
        cleanIngredients = ingredients

        # If the product does have some ingredients (a vaccum cleaner does not)
        if ingredients is not None:
            # There are usually some unnecessary HTML markings like <b> and <p>
            # we remove them with a regular expression
            ingredientsNoMarkings = re.sub(r"<.*?>", "", ingredients)
            cleanIngredients = re.sub(r"\n", "", ingredientsNoMarkings).strip()
 
        self.product.ingredients = cleanIngredients
        self.product.brand = response.xpath('//*[contains(@class, "product-page-brand")]/text()').get().strip()
        self.product.name = response.xpath('//*[contains(@class, "product-page-name")]/text()').get().strip()
        self.product.imageURL = response.xpath('//*[contains(@class, "product-medias-slider")]/div/picture/source/img/@src').get()
        # print(response.text)
        print(self.product)

