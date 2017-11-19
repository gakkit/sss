#! /usr/local/bin/python3
# 用于解析抓到的页面
import re
import copy
from bs4 import BeautifulSoup

def getTitle(soup):
    try:
        title = soup.find('span', id='productTitle').text.strip()
        return title
    except AttributeError:
        print('Resolving failed.')
        return ''

# compile regex first hand to make it faster
star_review_pattr = re.compile(r'[\n\r]+')
star_pattr = re.compile(r'([\d\.]+).*([\d\.]+)')
review_pattr = re.compile(r'(\d+)')

def getStarAndReview(soup):
    soup = soup.find(id="averageCustomerReviews")
    while soup.script: # 只要还有这恶心人的script 就继续删 直到删光 而且保证不会死循环
        soup.script.decompose()
    try:
        _star, _review = star_review_pattr.split(soup.text.strip())
    except ValueError: # not enough values to unpack (expected 2, got 1)
        return (0, 0) # 没有评分 或者没有抓到
    _pure_star = star_pattr.findall(_star)[0]
    star = min(_pure_star, key=lambda x:float(x))
    review = review_pattr.findall(_review)[0]
    return (float(star), int(review))

def getRanks(soup):
    ''' return rank(int), bsr(int), bsr_link(str)'''
    target = soup.find(id="SalesRank")
    if not target: # 如果找到的是空的，也就是老版的美国站，它是没有id=SalesRank 的
        try:
            target_0 = re.findall(r'Best Sellers Rank.*?</td>\W+</tr>', str(soup), re.S)[0] # re.S 匹配一切符号，就是我理解的多行匹配
            target_1 = re.findall(r'<td>.*?</td>', target_0, re.S)[0]
            target = BeautifulSoup(target_1, 'html.parser')
            bsr_link = target.td.span
        except IndexError: # 没有找到 Best Sellers Rank 
            return (0, 0, '')
    else:
        # 从这里开始处理新版的美国站（应该是和所有欧洲站+日本站同一的。）
        while target.style: # 去除自带的style tag
            target.style.decompose()
        bsr_link = target

    # 接下来从 bsr_link 获取纯的排名，只要最大值和最小值，毕竟字符串难以用于排序和直观的观察

    # 确保去除所有的 <a>，其实这里正则也可以实现.去掉了一切a，这样就不怕排名100里面的100，或者产品名里面的数字了，比如mp4
    mid_bsr_link = copy.copy(bsr_link) # 复制一份？以免在删除a tag时候触及真身
    while mid_bsr_link.a:
        mid_bsr_link.a.decompose()
    target = mid_bsr_link.text
    target = re.sub(r'\{.*?\}', '', target) # 去掉该死的css样式
    target = target.replace(',', '').replace('.', '') # 只要纯粹的数字

    nums = re.findall(r'([\d]+)', target) # 找个这个<tr>，然后把里面数字都扒出来
    nums = [int(num) for num in nums]

    try:
        rank = min(nums) # 小类目
        bsr = max(nums) # 大类目
        if len(nums) == 1: # 如果只有一个数字，那最大类目就是空的。
            return (rank, 0, str(bsr_link))
        else:
            return (rank, bsr, str(bsr_link))
    except ValueError:
        return (0, 0, '')

def getPrice(soup, asin):
    '''
    返回的有三种情况，一个数字，两个数字（价格区间，一般是尺码变体），空（currently available）
    为了方便数据库储存，全部改成一个数字，两个数字的取最小值（可以商榷），空为0.
    '''
    country = asin.country
    ourprice = soup.find(id="priceblock_ourprice")
    if ourprice:
        price = ourprice
    else:
        dealprice = soup.find(id="priceblock_dealprice")
        if dealprice:
            price = dealprice
        else:
            saleprice = soup.find(id="priceblock_saleprice")
            if saleprice:
                price = saleprice 
            else: # 兜底条款
                uk_price = soup.find(class_="a-color-price") # 第一个出现的是价格，有一定的不稳定性
                if uk_price:
                    price = uk_price

    # 处理不同风格的数字写法
    if country in ['JP', 'UK', 'US', 'CA']:
        price = price.text.replace(',', '')
    elif country in ['DE', 'IT', 'FR', 'ES']:
        price = price.text.replace('.', '').replace(',', '.')
    try:                    
        return float(min(re.findall(r'\d+[.,]*\d+', price)))
    except ValueError: # empty
        return 0

def getCart(soup, asin):
    '''
        返回商家名，在主程序中，根据用户自身的商家名来判断是否被抢购物车，这个函数不分析；
        没有购物车返回None，购物车是自己是返回True,不是则返回False
    '''
    stores = asin.user.store_set.all() # 顺藤摸瓜找到用户管理的所有店铺用来判断是否是本家的购物车
    seller_ids = [store.seller_id for store in stores]

    if not soup.find(id="add-to-cart-button"):
        return None # 没有购物车！？好的，那没有必要继续往下判断了。
    else:
        merchantID = soup.find("input", id="merchantID")['value']
        sellingCustomerID = soup.find("input", id="sellingCustomerID")['value']
        if merchantID == sellingCustomerID and merchantID in seller_ids:
            return True
        else:
            return False

def getSellYours(soup):
    mbc = soup.find(id="mbc")
    if mbc:
        return True # 被跟卖了
    else:
        return False # 没有被跟卖

# 以下为测试代码

def main():
    def get_soup(rat):
        with open('/Users/michael/{}.html'.format(rat), 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        return soup

    white_rats = [
        'aus1', 'aus2', 'aus3', 'auk1', 'auk2',  'aca1', 'aca2', 'ajp1', 'ajp2', 'ajp3',
        'ade1', 'ade2', 'afr1', 'afr2', 'ait1',  'ait2', 'aes1', 'aes2',
    ]

    for rat in white_rats:
        soup = get_soup(rat)

        print('***' + rat + '***')
        country = rat[1:3]
        print(getSellYours(soup))

if __name__ == '__main__':
    main()
























