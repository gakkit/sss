# 这个专门用于抓取 listing 页面
# 而对于

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

from myapp.utils import proxy

urls = {
    'JP':'https://www.amazon.co.jp/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'UK':'https://www.amazon.co.uk/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'ES':'https://www.amazon.es/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'FR':'https://www.amazon.fr/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'US':'https://www.amazon.com/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'IT':'https://www.amazon.it/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'DE':'https://www.amazon.de/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'CA':'https://www.amazon.ca/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
}

host_urls = {
    'JP':'https://www.amazon.co.jp',
    'UK':'https://www.amazon.co.uk',
    'US':'https://www.amazon.com',
    'ES':'https://www.amazon.es',
    'FR':'https://www.amazon.fr',
    'IT':'https://www.amazon.it',
    'DE':'https://www.amazon.de',
    'CA':'https://www.amazon.ca',
}

def clean_threads(): # 待定，不知道两个爬虫同时运行会有什么结果
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

    users = User.objects.filter(profile__vip__gte=1) # 只给高级vip抓取 greater than or equals to 0
    print(users)
    for user in users:
        for asin in user.asin_set.all():
            # 表示某个时间段的数据还没抓
            # if not asin.critical_set.filter(datetime__year=year, datetime__month=month, datetime__day=day):
            if True:
                status(asin, '正在抓取「差评」中 ...')
                yield asin
            else:
                status(asin,'该时间「差评」已经抓取')

# # for testing
# def getAsin():
#     asin1 = Asin.objects.get(value='B01H6GQJHS', country='US')
#     asin2 = Asin.objects.get(value='B01H6G3B0Q', country='US')
#     for asin in [asin1, asin2]:
#         yield asin

def getCaughtOrNot(content):
    '''差一个Japan'''
    eg = "Enter the characters you see below"
    de = "Sie kein Bot"
    it = "Inserisci i caratteri visualizzati nello spazio sottostante"
    es = "Introduce los caracteres que se muestran a continuación"
    fr = "Saisissez les caractères que vous voyez ci-dessous"
    c = str(content)
    for i in [eg, de, es, it, fr]:
        if i in c:
            return True # 被抓了

def getCritical(soup):
    try:
        criticals = soup.find(class_="review-views").find(class_="a-size-base").text
    except AttributeError: #'NoneType' object has no attribute 'find' 一个差评也没有
        return 0
    pure = re.sub(r"1.*?-.*?\d+", "", criticals).replace(',', '').replace('.', '')
    try:
        critical = re.findall(r'\d+', pure)[0]
        return int(critical)
    except IndexError:
        return 0

# 从这里开始，到saveReviews结束，这里的函数都是为saveReviews服务的小函数
def get_bad_star(s): # 这个函数专门为 getReviews 服务
    '''从字符串中获取整数的star，因为是单个用户，所以只能是整数, 输入参数只能是 ‘2.0 out of 5 stars’ 这样的'''
    if '1' in s:
        return 1
    elif '2' in s:
        return 2
    elif '3' in s:
        return 3

def get_host_url(review):
    '''根据review获取对应host'''
    country = review.critical.asin.country
    return host_urls[country]

pattr_asin = re.compile(r'/([A-Z\d]{10})/')
def parse_asin(url):
    '''从链接中抽取干净的ASIN'''
    return pattr_asin.findall(url)[0]

def save_dummy_asin(user, value, country):

    dummy_asin = Asin(user=user, value=value, country=country)
    dummy_asin.save() # 必须先save 才能加tag
    dummy_tag = user.tag_set.filter(name='__dummy__')
    if not dummy_tag: # _dummy 是内部保留tag，用于存放dummy asin,用户无法看到
        dummy_tag = Tag(user=user, name='__dummy__', reserved=True)
        dummy_tag.save()

    dummy_asin.tags.add(dummy_tag)
    dummy_asin.save()
    print('由于变体未被用户收录，以dummy_asin处理')
    return dummy_asin

def saveReviews(original_asin, critical, soup, n):
    ''' 
        直接将新增的差评存入数据库, n表示来的新差评个数 
        为什么叫 original asin，因为如果有变体，那么保存的差评可能不是针对这个asin的
    '''
    review_blocks = soup.find_all("div", id=re.compile("^customer_review-[\dA-Z]{10,20}"))[:n]
    for review_block in review_blocks:
        review = Review(critical=critical)
        # 如果有变体，这里会返回该变体的差评页的链接，我只提取里面的ASIN既可以了
        # 这样再访问下个变体的时候，即使读取的差评页是一样的，也不会去重复保存差评。因为对应的ASIN不同了。
        try:
            value = parse_asin(review_block.find("a", class_="a-size-mini")['href']) # 差评针对的具体变体的asin
            try:
                asin = Asin.objects.get(user=original_asin.user, value=value, country=original_asin.country)
            # myapp.models.DoesNotExist 这个是表示，如果我有两个变体，但是我只上传了其中一个asin，另一个我不care
            # 那么抓取同一个差评列表页的时候，可能会遇到，那么我就做一个dummy asin，仍然保存这个差评
            except: 
                asin = save_dummy_asin(original_asin.user, value, original_asin.country) # 这是一个dummy asin，用户不可见
        except TypeError: # 'NoneType' object is not subscriptable, 表示没有变体
            asin = original_asin # 没有变体的，直接把review保存到该 original_asin 即可

        # 差评对应的asin
        review.asin = asin
        # 差评的星级
        raw_star = review_block.find("div", class_="a-row").find("a", class_="a-link-normal")['title']
        review.star = get_bad_star(raw_star)
        # 差评的标题
        review.title = review_block.find("a", class_="review-title").text
        # 差评的具体链接
        review.link = get_host_url(review) + review_block.find("a", class_="review-title")['href']
        # 差评的内容
        review.content = review_block.find("span", class_="review-text").text

        # 有变体的listing，它们的差评是放在一起的。如果，抓了其中一个差评，识别了它的asin，它们如果这段差评的内容出现过，
        # 那么不再保存。两个变体下的差评都是针对同一个变体，那么这个review对象必然 asin，title, content相同，就不重复保存。
        if not Review.objects.filter(asin=asin, title=review.title, content=review.content): 
            review.save()

def getSoup(url):
    '''
        返回 soup 对象，表示成功抓取正常的页面
        返回 1，表示被反爬虫机制识别，需要更换一个代理继续重试
        返回 -1，表示发生了302页面跳转，意味着亚马逊自动修改了用户的ASIN，需要提示用户更换新的ASIN，此时也无法获取差评
        返回 -2，表示发生了404错误，意味着该产品已经不存在，需要提示用户检查ASIN输入是否正确或者该产品是否已经下降
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'content-type':'text/plain',
        'cache-control':'no-cache'
    }
    a_proxy = proxy.get()
    a_proxy.use += 1
    a_proxy.save()    
    try:
        r = requests.get(url, proxies={'http': a_proxy}, headers=headers, timeout=3)
        try: # 检测是否发生过跳转
            # 跳转到了类似 https://www.amazon.co.uk/ss/customer-reviews/B01NAPYGUF 的页面
            # 以为着亚马逊自动将欧洲产品的ASIN合并了，这会带来流量的衰减。        
            if r.history[0].status_code == 302:
                print('有跳转！')
                return -1
        except IndexError:
            pass        
    except requests.exceptions.ConnectionError: #requests.exceptions.ConnectionError: HTTPSConnectionPool(host='***', port=443): Read timed out.
        return 1 # 少显示点东西到控制台 
    except requests.exceptions.ReadTimeout:
        return 1 # 不懂为什么同一个timeout 居然会有两种不同的出错信息，不过都放这里就没问题了

    if r.status_code == 200:
        r.encoding='utf-8'
        if not getCaughtOrNot(r.text): # 成功抓取
            return BeautifulSoup(r.text, 'html5lib') # 用html.parser不行，会丢失信息，但是html5lib有点点慢
        else: # 因为是按顺序使用数据库的代理，所以没有必要去掉，不行就下一个
            print('busted.')
            a_proxy.fail += 1 # 用于统计成功率，把失败率高的剔除掉
            a_proxy.save()
            return 1
    else:
        print(url)
        print(r.status_code)
        return -2 # 404 页面被移除

def getData(soup, asin):
    if type(soup)!= int: # 只要返回的不是数字，那就是正常返回 soup
        number = getCritical(soup)
    elif soup == -1: # asin 变动，无法抓取差评，需要提示用户更改ASIN。
        print(asin, '有ASIN变化！')
        number = -1
    elif soup == -2:
        print(asin, '404错误！') # 404, 提示用户检查asin是否输入正确，或者该产品可能已经下架或被封
        number = -2 
    critical = Critical(asin=asin, number=number) # number是当天的number，然后日期时间是自动生成
    critical.save()
    status(asin, '抓取成功！')
    last_number = critical.get_last_one().number
    if last_number > number: # 本次抓取的数目比上次少->差评减少->是好事
        pass # 暂不处理
    elif last_number == number: 
        pass # 没有新增，也没有减少，不处理
    else: # 来差评！
        saveReviews(asin, critical, soup, number-last_number)
        # with open('/Users/michael/review-{}.html'.format(str(critical).split(':')[0]), 'w', encoding='utf-8') as f:
        #     f.write(str(soup))
        print('新差评已保存！')

def task(asin):
    connection.close() # 每启动一个子进程，都要关闭之前的connection，使用api时，django会自动开启新的connection
    # 如果不关就会 DatabaseError: error with status PGRES_TUPLES_OK and no message from the libpq
    url = urls[asin.country].format(asin.value)
    soup = getSoup(url)
    while soup == 1: # 没有正确抓取则返回1
        try:
            soup = getSoup(url) # 再试
        except TimeoutError:
            pass
    getData(soup, asin)
    
def main():
    clean_threads() # 每次运行前把之前的线程杀干净
    if not Proxy.objects.all():
        print('Load proxies, this may take a while ...')
        proxy.parse() #没有代理则做一批    
    pool = multiprocessing.Pool(processes=10)
    pool.map(task, getAsin())
    pool.close()
    connection.connect()










