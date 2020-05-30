import re

key = r"<h1>hello world<h1>"#源文本
p1 = r"<h1>(.+)<h1>"#我们写的正则表达式，下面会将为什么
pattern1 = re.compile(p1)
print (pattern1.findall(key)[0])#发没发现，我怎么写成findall了？咋变了呢？