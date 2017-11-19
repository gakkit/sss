# 用于管理代理服务器
from myapp.models import *
import os
import random

def parse():
    '''只有我在更新代理IP库的时候运行'''
    current_path = os.path.dirname(os.path.realpath(__file__))
    proxy_file = os.path.join(current_path, 'raw_proxy.txt')
    with open(proxy_file, 'r', encoding='utf-8') as f:
        ps = f.readlines()
    for p in ps:
        p = p.strip()
        if not Proxy.objects.filter(url=p): # 之前没有保存过的再保存
            Proxy(url=p).save()

def get(apply=True):
    '''获取单个proxy apply表示实际使用，如果支持查看的话，使用False以免use自动增加'''
    a_proxy = Proxy.objects.first() # 因为已经按照use排好序了 所以直接first就可以了
    if apply:
        a_proxy.use += 1 # 用一次加一次1
        a_proxy.save() 
    if random.choice(range(12)) == 0:
        print('.') # 不然不知道程序卡在哪里，和掷筛子出现同一面一样的概率
    return a_proxy