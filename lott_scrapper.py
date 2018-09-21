# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 05:42:30 2018

@author: HuyNguyen
"""

request_payload = {"CompanyId":"NTLotteries","MaxDrawCountPerProduct":10,
                   "OptionalProductFilter":["TattsLotto","OzLotto","Powerball",
                                            "MonWedLotto","SetForLife",
                                            "LuckyLotteries2",
                                            "LuckyLotteries5","Super66"]}
            
import requests
import json

if __name__ == "__main__":
    r = requests.post("https://api.thelott.com/sales/vmax/web/data/lotto/latestresults",
                  data = json.dumps(request_payload))
    content = r.text
    with open('data.txt','w') as file:
        json.dump(content,file)
    print(content)