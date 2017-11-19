# check if grank or other scripts work correctly
# 运行本程序进行测试 请直接 python check.py 没有太大必要用 shell_plus
from bs4 import BeautifulSoup
import os, re


current_path = os.path.dirname(os.path.realpath(__file__))
raw_html = os.path.join(current_path, 'check.html')
with open(raw_html) as f:
    raw_html = f.read()
soup = BeautifulSoup(raw_html, 'html.parser')

star_review_pattr = re.compile(r'[\n\r]+')
star_pattr = re.compile(r'([\d\.]+).*([\d\.]+)')
review_pattr = re.compile(r'(\d+)')
remove_script_tag = re.compile(r'<script.*?</script>')

def getStarAndReview(soup):
    soup = soup.find(id="averageCustomerReviews")
    while soup.script:
        soup.script.decompose()
    try:
        _star, _review = star_review_pattr.split(soup.text.strip())
    except ValueError: # not enough values to unpack (expected 2, got 1)
        return (0, 0) # 没有评分 或者没有抓到
    _pure_star = star_pattr.findall(_star)[0]
    star = min(_pure_star, key=lambda x:float(x))
    review = review_pattr.findall(_review)[0]
    return (float(star), int(review))

getStarAndReview(soup)