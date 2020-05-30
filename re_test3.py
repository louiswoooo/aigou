import re
from info import *

str = '朵朵神速大10盒。10'
res1 = re.findall('。 *(\d+) *$', str)  # 查找数量

print(res1)