from django.contrib import admin

from .models import *
# class AsinInline(admin.TabularInline):
#     model = Asin

critical_urls = {
    'JP':'https://www.amazon.co.jp/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'UK':'https://www.amazon.co.uk/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'ES':'https://www.amazon.es/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'FR':'https://www.amazon.fr/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'US':'https://www.amazon.com/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'IT':'https://www.amazon.it/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'DE':'https://www.amazon.de/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
    'CA':'https://www.amazon.ca/product-reviews/{}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&reviewerType=all_reviews&filterByStar=critical&pageNumber=1&pageSize=50&sortBy=recent',
}


def getURL(obj): # 从critical/data 引出 url
    asin = obj.asin
    url = critical_urls[asin.country].format(asin.value)
    return url

getURL.short_description = 'URL'

class AsinAdmin(admin.ModelAdmin):
    list_display = ('country', 'value')

class CriticalAdmin(admin.ModelAdmin):
    list_display = ('asin', 'number', 'datetime', getURL)

def getDate(obj):
    critical = obj.critical
    return critical.datetime
getDate.short_description = '抓取时间'
def getCriticalPk(obj):
    critical = obj.critical
    return critical.pk
getCriticalPk.short_description = "差评数ID"
def getCriticalNumber(obj):
    critical = obj.critical
    return critical.number
getCriticalNumber.short_description = "差评数"    
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('critical', 'asin', getCriticalPk, getCriticalNumber, getDate, 'star', 'title', 'content')
    list_display_links = ('critical',)

def getAlias(obj):
    return obj.asin.alias

class DataAdmin(admin.ModelAdmin):
    list_display = ('asin', getAlias,'datetime', 'price', 'bsr', 'rank', 'star', 'review', 'cart', 'sell_yours')
    
class ProxyAdmin(admin.ModelAdmin):
    list_display = ('pk', 'url', 'use', 'get_rate')

def getAsin(obj):
    asins = obj.asin_set.all()
    return str(asins)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', getAsin)



admin.site.register(Asin, AsinAdmin)
admin.site.register(Critical, CriticalAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(Proxy, ProxyAdmin)
admin.site.register(Tag, TagAdmin)









