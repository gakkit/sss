# 主程序，用于抓取listing网页，并调度解析器(resolver)，然后存到数据库。

from myapp.models import *
import requests
import os, re, time
import datetime
import sys
import glob
from bs4 import BeautifulSoup
import random
import multiprocessing
import psutil
from django.db import connection 
from django.utils import timezone

from myapp.utils import proxy, resolver

urls = {
    'JP':'https://www.amazon.co.jp/dp/{}',
    'UK':'https://www.amazon.co.uk/dp/{}',
    'ES':'https://www.amazon.es/dp/{}',
    'FR':'https://www.amazon.fr/dp/{}',
    'US':'https://www.amazon.com/dp/{}',
    'IT':'https://www.amazon.it/dp/{}',
    'DE':'https://www.amazon.de/dp/{}',
    'CA':'https://www.amazon.ca/dp/{}',
}

def clean_threads():
    PROCNAME = "Python"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            if proc.status() == 'stopped': # 杀掉停止的进程
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    pass

def status(asin, info):
    print(asin.country, asin.value, info)

def getAsin():
    '''
        只爬当天没有爬取的数据
    '''
    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day
    for asin in Asin.objects.all():
        if not asin.data_set.filter(datetime__year=year, datetime__month=month, datetime__day=day): #表示今天的数据还没有查过
            status(asin, '正在抓取中 ...')
            yield asin
        else:
            status(asin,'今日数据已经抓取')

def busted(content, country):
    '''差一个Japan'''
    verification = {
        "CA": "Enter the characters you see below",
        "US": "Enter the characters you see below",
        "UK": "Enter the characters you see below",
        "DE": "Sie kein Bot",
        "IT": "Inserisci i caratteri visualizzati nello spazio sottostante",
        "ES": "Introduce los caracteres que se muestran a continuación",
        "FR": "Saisissez les caractères que vous voyez ci-dessous",        
    }
    c = str(content)
    if verification[country] in c:
        return True # 被抓了

def getSoup(asin):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'content-type':'text/plain',
        'cache-control':'no-cache'
    }
    url = urls[asin.country].format(asin.value) # 不储存url，浪费数据库
    print(url)
    a_proxy = proxy.get()
    a_proxy.use += 1
    a_proxy.save()
    try:
        r = requests.get(url, proxies={'http':a_proxy.url}, headers=headers, timeout=3)
    #requests.exceptions.ConnectionError: HTTPSConnectionPool(host='***', port=443): Read timed out.
    except requests.exceptions.ConnectionError: 
        return 1 # 少显示点东西到控制台 
    except requests.exceptions.ReadTimeout:
        return 1 # 不懂为什么同一个timeout 居然会有两种不同的出错信息，不过都放这里就没问题了
    if r.status_code == 200:
        r.encoding='utf-8'
        if not busted(r.text, asin.country): # 成功抓取
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
        else: # 因为是按顺序使用数据库的代理，所以没有必要去掉，不行就下一个
            a_proxy.fail += 1 # 用于统计成功率，把失败率高的剔除掉
            a_proxy.save()
            with open('/Users/michael/tmp2.html', 'w', encoding='utf-8') as f:
                f.write(r.text) 
            print('busted.')
            return 1
    else:
        print(url)
        print(r.status_code)
        return 2

def getData(soup, asin):
    if soup != 2: # 正常返回 soup
        title = resolver.getTitle(soup)
        star, review = resolver.getStarAndReview(soup)        
        rank, bsr, bsr_link = resolver.getRanks(soup)
        price = resolver.getPrice(soup, asin)
        cart = resolver.getCart(soup, asin)
        sell_yours = resolver.getSellYours(soup)
    # soup == 2 意味着这个页面不存在 404 错误，所有值全部报缺省值
    # 为什么不处理跳转的情况？因为即使亚马逊变更了ASIN，原来的ASIN仍然能到达该页面，所以无需提示更换
    # 此外，这也算是对高级用户的特别照顾。
    else: 
        # 此时的 price是 0，这就是作为这个listing 已经消失的标记。 在views.py里面会靠这个分辨。
        title = 0
        bsr = 0
        rank = 0
        bsr_link = ''
        review = 0
        star = 0
        price = 0
        cart = True # 默认不警报，不然就成了“狼来了”的小孩了
        sell_yours = False # 默认没有人跟卖
    data = Data(
        asin=asin, 
        title=title, 
        rank=rank, 
        bsr=bsr, 
        bsr_link=bsr_link, 
        review=review, 
        star=star,
        price=price,
        cart=cart,
        sell_yours=sell_yours,
    )
    data.save()
    status(asin, '抓取成功！')

def task(asin):
    connection.close() # 每启动一个子进程，都要关闭之前的connection，使用api时，django会自动开启新的connection
    soup = getSoup(asin)
    while soup == 1: # 没有正确抓取则返回1
        try:
            soup = getSoup(asin) # 再试
        except TimeoutError:
            pass
    getData(soup, asin)
    
def main():
    # clean_threads() # 每次运行前把之前的线程杀干净
    if not Proxy.objects.all():
        print('Load proxies, this may take a while ...')
        proxy.parse() #没有代理则做一批    
    pool = multiprocessing.Pool(processes=10)
    pool.map(task, getAsin())
    pool.close()
    connection.connect() # 跑完之后运行一下这个，解除 connection.close()的封印，重新和数据库连接








