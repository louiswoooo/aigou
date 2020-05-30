import re
from info import *

def SliceInfo(str, start, end):
    pat1 = r".*" + start + ".*"
    start_line = re.findall(pat1, Price)[0]

    pat2 = r".*" + end + ".*"
    end_line = re.findall(pat2, Price)[0]

    pat = start_line + "(.+)" + end_line
    info = re.findall(pat, Price, re.S | re.M)[0]
    return info

def GetProductList():                     #获取产品列表
    str = SliceInfo(Price, "报价", "下单格式")
    prd_info = str.split("\n")
    i=1
    prd_list=[]
    for line in prd_info:
        if len(line) > 4:
            #print("%d "%i, line)
            prd_list.append(line)
            i += 1
    return prd_list

def GetFormList():
    str = SliceInfo(Price, "下单格式", "返利")
    form_info = str.split("\n")
    i = 1
    form_list = []
    for line in form_info:
        if len(line) > 4:
            # print("%d "%i, line)
            form_list.append(line)
            i += 1
    return form_list

def GetOnlyName(name, name_list):
    i = 2
    while i <= len(name):
        count = 0
        for line in name_list:
            name_short = name[0:i]
            if re.findall(name_short, line):
                count += 1
        if count == 0:
            return("找不到这个名字")
        elif count > 1:
            i += 1
        elif count == 1:
            return name_short


def GetProductStandardNameList(form_list):          # 获得格式列表当中的每个产品订单的标准名称
    form_info = SliceInfo(Price, "下单格式", "返利")
    prd_std_name_list = []
    for prd_name in form_list:
        i = 2
        while i < len(prd_name):
            prd_name_short = prd_name[0:i]
            prd_find = re.findall(prd_name_short, form_info)
            if len(prd_find) == 1:
                prd_std_name_list.append(prd_find[0])
                break
            else:
                i += 1
        if (i > len(prd_name)):
            print("在订单格式当中找不到这个产品:%s" % prd_name)
    return prd_std_name_list

def GetOrderCount(prd_std_list):
    for line1 in prd_std_list:
        pat = ".*" + line1['name'] + ".*"
        record_list = re.findall(pat, Order)  # 查找订单内容当中的这个产品的订单信息
        order_count = 0
        pat = "\d+"
        for line2 in record_list:
            total = re.findall(pat, line2)[-1]       #查找订单信息当中的总数量
            if total:
                order_count += int(int(total) / int(line1['count']))    #总数量除以每份数量得到份数
        line1["order_count"] = order_count

def GetProductStandardList(prd_name_list, prd_list):
    print(prd_list)
    prd_std_list = []
    pat = '返利均为(\d*)'
    res = re.findall(pat, Price)
    if res:
        fanli_all = res[0]
    else:
        print("没有查到返利")
    for line in prd_name_list:
        prd_dict = {}
        prd_dict['name'] = line
        for line2 in prd_list:               #获取分销价格
            if re.findall(line, line2):
                #print(line2)
                pat = ".*分销(\d*)"
                res = re.findall(pat, line2)
                if res:
                    prd_dict['fenxiao'] = float(res[0])
                pat = ".*团购(\d*)"
                res = re.findall(pat, line2)
                if res:
                    prd_dict['tuangou'] = float(res[0])
                pat = r"\d+"
                prd_dict['count'] = int(re.findall(pat, line2.split('，')[0])[-1])
                break
        if  'count' not in prd_dict:
            name = GetOnlyName(line, prd_list)
            for line2 in prd_list:                  # 获取分销价格
                if re.findall(name, line2):
                    pat = ".*分销(\d*)"
                    res = re.findall(pat, line2)
                    if res:
                        prd_dict['fenxiao'] = float(res[0])
                    pat = ".*团购(\d*)"
                    res = re.findall(pat, line2)
                    if res:
                        prd_dict['tuangou'] = float(res[0])
                    pat = r"\d+"
                    prd_dict['count'] = int(re.findall(pat, line2.split('，')[0])[-1])
        prd_dict['fanli'] = float(fanli_all)
        #print(prd_dict)
        prd_std_list.append(prd_dict)
    return prd_std_list

def GetOrderList():
    pass

if __name__ == "__main__":
    prd_list = GetProductList()
    form_list = GetFormList()
    prd_name_list = GetProductStandardNameList(form_list)
    prd_std_list = GetProductStandardList(prd_name_list, prd_list)
    GetOrderCount(prd_std_list)
    print(prd_std_list)

    order_all = 0
    income_all = 0
    cost_all = 0
    profit_all = 0
    for line in prd_std_list:
        order_total = 0
        income = 0
        cost = 0
        profit = 0

        name = line['name']
        count = line['order_count']
        tuangou = line['tuangou']
        fenxiao = line['fenxiao']
        if  count> 0:
            order_total = count
            income = tuangou * count
            cost = fenxiao * count
            profit = income - cost
            print(name,"，数量：%d，成本：%.2f"     \
                %(order_total, cost))
            order_all += order_total
            income_all += income
            cost_all += cost
    profit_all = income_all - cost_all
    print("")
    print("总%d单"%order_all)
    print("总货款%d"%income_all)
    print("利润%d"%profit_all)
    print("应付%d"%cost_all)



