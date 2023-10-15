import scrapy
import json
import math
from datetime import datetime

class CromaSpider(scrapy.Spider):
    name = 'croma'

    url = "https://api.croma.com/cmstemplate/allchannels/v1/page?pageType=ContentPage&pageLabelOrId=pwaHomePage1&fields=FULL"

    headers = {
    'authority': 'api.croma.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://www.croma.com',
    'referer': 'https://www.croma.com/',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }
    def start_requests(self):
        
        yield scrapy.Request(
                                url=self.url,
                                headers=self.headers,
                                method="GET",
                                callback=self.parse
                            )

    def parse(self, response):
        data = json.loads(response.text)

        for i in data["contentSlots"][ "contentSlot"][0]["components"]["component"][1]["bannerList"]:
            link = i["urlLink"]
            categ = link.split("/")[1]
            u_split = link.split("/c/")[-1]

            url2 = f"https://api.croma.com/searchservices/v1/category/{u_split}?currentPage=1&query=:relevance&fields=FULL&channel=WEB&channelCode=400049"

            yield scrapy.Request(
                                    url=url2,
                                    headers=self.headers,
                                    method="GET",
                                    meta={"url": url2, "currnt_page": 1, "count": 0,"u_split":u_split,"categ":categ},
                                    callback=self.parse2
                                    )
    def parse2(self, response):
        data2 = json.loads(response.text)
        total_result = math.ceil(int(data2["pagination"]["totalResults"]) /20)
        
        for j in data2["products"]:
            
            name = j["name"]

            img = j["plpImage"]

            orignal_price = j["mrp"]["value"]
            
            discount_price = j["price"]["value"]

            productLiveDate = j["productLiveDate"]

            date_obj = datetime.strptime(productLiveDate, '%Y-%m-%dT%H:%M:%S')
            given_date_obj = datetime.fromisoformat(productLiveDate)
            date_formatted = date_obj.strftime('%d-%m-%Y %H:%M:%S')
            
            date = "2023-02-01T00:00:00"
            com_date_obj = datetime.fromisoformat(date)

            if given_date_obj >= com_date_obj:
                new = 'yes'
            else:
                new = 'no' 

            standardWarranty = j["standardWarranty"][0]
            a = (int(standardWarranty)/12)
           
            try:
                productMessage1 = j["productMessage1"]  
            except:
                productMessage1 = None
            try:
                if productMessage1 in "Exchange Available":
                    Exchange = 'Yes'
            except:
                    Exchange = 'No'  
                
            item = {
                "pro_details":{"name":name,
                "img_url":img,
                "orignal_price":orignal_price,
                "price":discount_price,
                "standardWarranty":standardWarranty,
                "standardWarranty_in_year":a,
                "productMessage1":productMessage1,
                "Exchange Available":Exchange
                },
                "date":{
                    "productLiveDate":date_formatted,
                    "productnew":new
                },
                "categ":response.meta["categ"]
            }
            yield item

        if response.meta['currnt_page'] < total_result:
            response.meta['currnt_page'] += 1     
            url2 = f"https://api.croma.com/searchservices/v1/category/{response.meta['u_split']}?currentPage={response.meta['currnt_page']}&query=:relevance&fields=FULL&channel=WEB&channelCode=400049"
            
            yield scrapy.Request(
                                    url=url2,
                                    headers=self.headers,
                                    method="GET",
                                    meta={
                                        "url": url2,
                                        "currnt_page": response.meta['currnt_page'],
                                        "count": 0,
                                        "categ":response.meta["categ"],
                                        "u_split":response.meta['u_split'],
                                        },
                                    callback=self.parse2
                                )