import re
from info import *

pat1=r".*报价.*"
baojia_line = re.findall(pat1, Price)[0]

pat2=r".*下单格式.*"
xiadangeshi_line = re.findall(pat2, Price)[0]

pat = baojia_line + "(.+)" + xiadangeshi_line
product_info = re.findall(pat, Price, re.S | re.M)[0]

prd_info = product_info.split("\n")
i=1
prd_list=[]
for line in prd_info:
    if len(line) > 4:
        #print("%d "%i, line)
        prd_list.append(line)
        i += 1


#################################################################
pat3 = r".*返利.*"
fanli_line = re.findall(pat3, Price)[0]

pat = xiadangeshi_line + "(.+)" + fanli_line
order_form_info = re.findall(pat, Price, re.S | re.M)[0]

form_info = order_form_info.split("\n")
i=1
form_list=[]
for line in form_info:
    if len(line) > 4:
        #print("%d "%i, line)
        form_list.append(line)
        i += 1

prd_std_name_list = []
for prd_name in form_list:
    i = 2
    while i<len(prd_name):
        prd_name_short = prd_name[0:i]  # 获得格式列表当中的每个产品订单的标准名称
        prd_find = re.findall(prd_name_short, order_form_info)
        if len(prd_find) == 1:
            prd_std_name_list.append(prd_find[0])
            break
        else:
            i += 1
    if(i>len(prd_name)):
        print("在订单格式当中找不到这个产品:%s"%prd_name)
print(prd_std_name_list)
#################################################################
money_total = 0
money_cost = 0
money_profit = 0
order_sum = 0


for prd_name in form_list:
    pat = r"\d+"                        #在格式列表当中查找每个产品每份的数量
    res = re.findall(pat, prd_name)
    prd_singal_num = int(res[-1])

    pat = prd_name_short
    for line in prd_list:                          #在产品列表当中查找这个格式列表的产品对应的内容，形成prd_select
        res = re.findall(pat, line)
        if res:
            prd_select = line
            #print(prd_select)
            break


    prd_sel_info = prd_select.split("，")        #分割产品列表的选中记录
    prd_name = prd_sel_info[0]

    #for line in prd_sel_info:
        #print(line)

    for line in prd_sel_info:               #获取分销价格
        pat = ".*分销(\d*)"
        res = re.findall(pat, line)
        if res:
            price_fenxiao = float(res[0])
            #print("%f"%price_fenxiao)

    for line in prd_sel_info:               #获取团购价格
        pat = r"团购(\d*)"
        res = re.findall(pat, line)
        if res:
            price_tuangou = float(res[0])
            #print("%f"%price_tuangou)

    pat = ".*" + prd_name_short +".*"
    #print(pat)
    res = re.findall(pat, Order)            #查找订单内容当中的这个产品的订单信息
    #print(res)

    ord_prd_num = 0
    pat = "\d+"
    for line in res:
        #print(line)
        total = re.findall(pat, line)[-1]       #查找订单信息当中的总数量
        if total:
            ord_prd_num += int(total)/prd_singal_num    #总数量除以每份数量得到份数

    order_sum += ord_prd_num
    money_tuangou = ord_prd_num * price_tuangou
    money_fenxiao = ord_prd_num * price_fenxiao
    money_lirun = money_tuangou - money_fenxiao

    money_total += money_tuangou
    money_cost += money_fenxiao
    money_profit += money_lirun

    #if(ord_prd_num>0):
        #print(prd_name,"，数量：%d，总价：%.2f，成本：%.2f，利润：%.2f"     \
          #%(ord_prd_num, money_tuangou, money_fenxiao, money_lirun))

#print(prd_name,"，数量：%d，总价：%.2f，成本：%.2f，利润：%.2f"     \
          #%(ord_prd_num, money_tuangou, money_fenxiao, money_lirun))


