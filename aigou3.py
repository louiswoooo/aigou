# 版本3.0
#需要加上对于小数的处理
#需要加上对订单空格的兼容
import re
#微信信息的过滤器定义，只保留指定的编码字符，
# 包括中文、英文大小写、数字等，
WX_CONTENT_PAT = "[^\u4e00-\u9fa5^a-z^A-Z^0-9^\n^ ^(^)^+^-^.^:^/^ ^（^）^，^。^：^、^＋^-]"
#订单信息的分割器
ORDER_SPLIT = '[。，., \n]'
#订单信息的过滤器定义
ORDER_SPLIT_PAT = "\w"

ADDR_PAT = "([^省]+省|.+自治区|[^市]+市)([^自治州]+自治州|[^市]+市|[^盟]+盟|[^地区]+地区|.+区划)"
PHONE_PAT = ".*(1[35678]\d{9}).*"
ALL_COUNT_PAT = ' *(\d+) *$'


class aigou:
    def __init__(self, price='', order=''):
        self.price = price
        self.order = order

    def filter_emoji(self, desstr, restr=''):
        # 过滤除中英文及数字以外的其他字符
        # 原生字符串加 r，\符号不转义；转义字符串
        res = re.compile(WX_CONTENT_PAT)
        return res.sub(restr, desstr)

    # 获取以包含 start 关键字的行开头,包含 end 关键字结尾的行的中间信息
    def SliceInfo(self, info, start, end):
        pat1 = r".*" + start + ".*"
        find_list1 = re.findall(pat1, info)
        if len(find_list1) == 0:
            return ''
        else:
            start_line = find_list1[0]

        pat2 = r".*" + end + ".*"
        find_list2 = re.findall(pat2, info)
        if len(find_list2) == 0:
            return ''
        else:
            end_line = find_list2[0]

        pat = start_line + "(.+)" + end_line
        info = re.findall(pat, self.price, re.S | re.M)[0]
        return info

    # 获取产品列表，获取不到返回 error 列表
    def GetProductList(self):
        res = re.findall('.*返利.*', self.price)
        if len(res)>0:
            fanli_info = res[-1]
        else:
            return 0, '报价信息当中没有找到返利关键字！'
        fan_list = fanli_info.split('，')
        fanli_list = []
        for line in fan_list:
            fanli_dict = {}
            res_name = re.findall('(.+)返利', line)
            res_fanli = re.findall('\d+', line)
            if len(res_name)>0 and len(res_fanli)>0:
                fanli_dict['name'] = res_name[0]
                fanli_dict['fanli'] = float(res_fanli[-1])
                fanli_list.append(fanli_dict)
                res = re.findall('其他',fanli_dict['name'])
                if len(res)>0:
                    other_fanli = fanli_dict['fanli']
                else:
                    other_fanli = 0
            else:
                return 0, '在返利信息%s当中没有找到商品返利信息！'%line

        info_temp = self.SliceInfo(self.price, "报价", "下单格式")
        info = self.filter_emoji(info_temp)
        if len(info) == 0:
            return 0, '报价信息当中找不到报价或下单格式关键字！'
        prd_info = info.split("\n")
        temp_list=[]
        for line in prd_info:
            if len(line) > 4:
                pat = '\d*[.，、。]*(.*)'      #过滤产品列表当中的前缀字符
                res = re.findall(pat, line)
                temp_list.append(res[0])
        prd_list = []
        for prd_line in temp_list:
            prd_dict = {}
            name = prd_line.split('，')[0]
            pat = ".*分销(\d*)"
            res = re.findall(pat, prd_line)
            if res:
                fenxiao = float(res[0])
            else:
                return 0, '找不到产品%s的分销价格'%prd_line
            pat = ".*团购(\d*)"
            res = re.findall(pat, prd_line)
            if res:
                tuangou = float(res[0])
            else:
                return 0, '找不到产品%s的团购价格'%prd_line
            prd_dict['name'] = name
            prd_dict['fenxiao'] = fenxiao
            prd_dict['tuangou'] = tuangou
            for fanli_dict in fanli_list:
                res = re.findall(fanli_dict['name'], prd_dict['name'])
                if len(res)>0:
                    prd_dict['fanli'] = fanli_dict['fanli']
                    break;
            if fanli_dict == fanli_list[-1]:
                prd_dict['fanli'] = other_fanli;
            prd_list.append(prd_dict)
        return 1, prd_list

    # 获取订单格式列表，获取不到返回 0 和原因
    def GetFormList(self):
        info_temp = self.SliceInfo(self.price, "下单格式", "返利")
        info = self.filter_emoji(info_temp)
        if len(info) == 0:
            return 0, '团购报价当中找不到下单格式或返利关键字！'
        form_info = info.split("\n")
        form_list = []
        for line in form_info:
            form_dict = {}
            if len(line) > 4:
                temp = line.split('。')
                name = temp[0]
                count = temp[1]
                if name and count:
                    form_dict['name'] = name
                    form_dict['count'] = int(count)
                else:
                    return 0, '订单格式当中“%s”找不到商品或单份数量！'%line
                form_list.append(form_dict)
        return 1, form_list

    #从列表 name_list 当中获取唯一的简称 name, 长度从2开始，
    # 保证返回的 name 尽可能短而且在name_list 当中唯一的
    def GetOnlyName(self, name, name_list):
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

    # 合并产品列表和格式列表得到价格列表，由于产品列表和格式列表名称不一致，需要做产品名称匹配
    # 匹配的方式是先取 form_list name 中头两个字 对prd_list name 进行匹配，如果只有唯一结果，就算成功
    # 如果>2 就取 3 个字，如此直到匹配成功为止
    #如果有 =0 的情况，就取 prd_list name 取匹配 form_list name 方法类似
    def GetPriceList(self, prd_list, form_list):
        Price_list = []
        for form_line in form_list:         #取form_list 每一行进行匹配
            Price_dict = {}
            i = 2                                   #从两个字开始
            while i<len(form_line['name']):         #直到名字结束
                count = 0                           #匹配计数器
                form_name_short = form_line['name'][0:i]
                for prd_line in prd_list:               #到 prd_list 当中去匹配name
                    if len(re.findall(form_name_short, prd_line['name']))>0:
                        prd_pt = prd_line               #指针指向匹配的那个
                        count += 1
                if count == 1:                          #匹配完毕如果总数 =1，则合并
                    Price_dict['name'] =  form_name_short
                    Price_dict['count'] = form_line['count']
                    Price_dict['fenxiao'] = prd_pt['fenxiao']
                    Price_dict['tuangou'] = prd_pt['tuangou']
                    Price_dict['fanli'] = prd_pt['fanli']
                    Price_list.append(Price_dict)
                    break
                elif count > 1:             #如果匹配到多个，说明有多个重名，加字数
                    i += 1
                else:                       #如果匹配不到，转到取prd_list 当中去取 name 匹配 form_list
                    for temp_line in prd_list:
                        prd_name_short = temp_line['name'][0:2]
                        if len(re.findall(prd_name_short, form_line['name'])) >0:
                            Price_dict['name'] = prd_name_short
                            Price_dict['count'] = form_line['count']
                            Price_dict['fenxiao'] = temp_line['fenxiao']
                            Price_dict['tuangou'] = temp_line['tuangou']
                            Price_dict['fanli'] = temp_line['fanli']
                            Price_list.append(Price_dict)
                            break;
                        if temp_line == prd_list[-1]:
                            return 0, '报价表中找不到这个产品：%s'%form_line
                    break
            if i>= len(form_line['name']):
                return 0, '报价表中找不到这个产品：%s'%form_line
        return 1, Price_list

    #查找订单列表当中的信息，形成订单列表，其中商品通过 price_list 获取
    def GetPersonOrderList(self, price_list):
        Order_list = []
        prd_list = []
        for line in price_list:             #获取商品名称的列表
            prd_list.append(line['name'])
        info = self.order
        temp_list = []
        temp0_list = info.split('\n')
        order_info_list = []
        order_info_list_copy = []
        for line in temp0_list:             #简化订单有用信息
            if len(line)>4:
                temp_list = line.split('。')
                for info_line in temp_list:
                    if re.findall(ORDER_SPLIT_PAT, info_line):
                        order_info_list.append(info_line)
        waste_list = []
        i = len(order_info_list)        #获取订单的分割行数长度
        while  i > 0:                   #循环每一行
            order_dict = {}
            all_count_info = order_info_list.pop()          #先匹配 all_count,从最后一行开始匹配
            i -= 1
            res = re.findall(ALL_COUNT_PAT, all_count_info)
            if res == []:
                waste_list.insert(0, all_count_info)        #如果没有匹配到，放到 waste ,重新开始找
                continue
            elif len(res[0]) > 3:
                waste_list.insert(0, all_count_info)        #如果没有匹配到，放到 waste ,重新开始找
                continue
            else:
                order_dict['all_count'] = res[0]            #如果找到了，赋值
                prd_info = order_info_list.pop()
                i -= 1
                order_dict['name'] = ''
                for prd in prd_list:                        #循环产品列表，匹配产品名称
                    res = re.findall(prd, prd_info)
                    if res:
                        order_dict['name'] = res[0]         #如果找到，赋值，并退出循环
                        break
                if order_dict['name'] == '':      #如果循环结束都没有找到，放到 waste
                    waste_list.insert(0, all_count_info)
                    waste_list.insert(0,prd_info)
                    continue
                else:
                    i -= 1
                    addr_info = order_info_list.pop()
                    res = re.findall(ADDR_PAT, addr_info)
                    if res == []:
                        waste_list.insert(0, addr_info)
                        waste_list.insert(0, all_count_info)
                        waste_list.insert(0, prd_info)
                        continue
                    else:
                        order_dict['addr'] = res[0]
                        phone_info = order_info_list.pop()


            print(order_dict)
        # for line in waste_list:
        #     print(line)


    def cal(self):
        prd_ret = self.GetProductList()
        if prd_ret[0] == 0:
            return prd_ret[1]
        else:
            prd_list = prd_ret[1]
        form_ret = self.GetFormList()
        if form_ret[0] == 0:
            return form_ret[1]
        else:
            form_list = form_ret[1]
        price_ret = self.GetPriceList(prd_list, form_list)
        if price_ret[0] == 0:
            return price_ret[1]
        else:
            price_list = price_ret[1]
        order_ret = self.GetOrderList(price_list)
        if order_ret[0] == 0:
            return order_ret[1]
        else:
            order_list = order_ret[1]

        all_list = []
        ret_str = ''
        for order_line in order_list:
            all_dict = {}
            for price_line in price_list:
                # print(price_line)
                # print(order_line)
                if price_line['name'] == order_line['name']:
                    all_dict['name'] = order_line['name']
                    all_dict['num'] = order_line['all_count'] / price_line['count']
                    all_dict['fenxiao'] = price_line['fenxiao'] * all_dict['num']
                    all_dict['tuangou'] = price_line['tuangou']*all_dict['num']
                    all_list.append(all_dict)
                    ret_str += "%s，数量：%d，成本：%d\n" % (all_dict['name'],all_dict['num'],all_dict['fenxiao'] )
                    break
        total_num = 0
        total_fenxiao = 0
        total_tuangou = 0
        for line in all_list:
            total_num += line['num']
            total_fenxiao += line['fenxiao']
            total_tuangou += line['tuangou']
        ret_str += "总%d单\n总货款%d\n利润%d\n应付%d" % (total_num, total_tuangou,total_tuangou - total_fenxiao,total_fenxiao)
        return ret_str









