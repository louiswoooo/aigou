from aigou3 import *
from info import *
import re

# ADDR_PAT = "([^省]+省|.+自治区|[^市]+市)([^自治州]+自治州|[^市]+市|[^盟]+盟|[^地区]+地区|.+区划)([^市]+市|[^县]+县|[^旗]+旗|.+区)"
# src = """李美丽。15907542741。
# 广东省汕头市金平区岐山街道兰田14巷13号寄车场006。
# 爱购定制一抹灵3支。3"""
#
#
# res = re.findall(ADDR_PAT, src)
# for line in res:
#     print(line)


yang = aigou(Price, Order)
prd_list = yang.GetProductList()[1]
form_list = yang.GetFormList()[1]
price_list = yang.GetPriceList(prd_list,form_list)[1]
print(price_list)
yang.GetPersonOrderList(price_list)
