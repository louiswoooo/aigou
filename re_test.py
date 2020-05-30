import re

language = ''''<tr><th>性別：</th><td>男</td></tr>'''
# 正则表达式获取<tr></tr>之间内容
res_tr = r'<tr>(.*?)</tr>'
m_tr = re.findall(res_tr, language, re.S | re.M)
for line in m_tr:
    print(line)
    # 获取表格第一列th 属性
    res_th = r'<th>(.*?)</th>'
    m_th = re.findall(res_th, line, re.S | re.M)
    for mm in m_th:
        print(mm)
    # 获取表格第二列td 属性值
    res_td = r'<td>(.*?)</td>'
    m_td = re.findall(res_td, line, re.S | re.M)
    for nn in m_td:
        print(nn)