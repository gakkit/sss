from django.db import models
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone

User = get_user_model()

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

class Profile(models.Model):
    '''
        user对象的扩展。OneToOneField。用于保存用户的余额、认证资料等信息。
        换言之，对于“单个的属性“，放profile，对于“多个的属性”，新建一个model，如Store。
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vip = models.IntegerField(default=0) # 用户类型：0 免费用户，1 会员，2 超级会员
    balance = models.FloatField(default=0) # 账户余额
    phone_number = models.CharField(default='', max_length=20) # 电话号码

class Store(models.Model):
    '''店铺：用于储存用户店铺的id'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    seller_id = models.CharField(max_length=20, default="")
    def __str__(self):
        return self.user.username + ' ' + self.seller_id        

class Tag(models.Model):
    '''
        用户自行给ASIN归类。
        用户在初次提交asin时，如果没有分类，则归入一个tag叫“未分类”。
        如果删除asin，则放入一个叫“回收站”的tag，从此不再爬取该asin，但之前的数据不删除。
        这样改asin也会停止计费，但是该月的钱还是要扣的。（如果是按月计费的话）
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="") # 应该不可能超过50了
    datetime = models.DateTimeField(auto_now_add=True) # 创建日期
    reserved = models.BooleanField(default=False) # 是否为保留tag，保留tag有特殊用途，如 __dummy__ 和回收站 __recycle__
    def __str__(self):
        return self.name

class Asin(models.Model):
    '''警告：注意之后用户提交的时候，不能由 user, value, country 全部一样的重复 Asin'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    alias = models.CharField(max_length=50, default="") # 别名
    value = models.CharField(max_length=10)
    country = models.CharField(max_length=2)
    def __str__(self):
        return "{}-{}".format(self.country, self.value)
    def get_link(self):
        return urls[self.country].format(self.value) # 不储存url，浪费数据库

class Data(models.Model):
    '''
        用于储存被抓到的数据。
    '''
    asin = models.ForeignKey(Asin, on_delete=models.CASCADE) # 表示这个Data属于哪个asin
    datetime = models.DateTimeField(auto_now_add=True)  # 抓取数据的具体时间
    title = models.CharField(max_length=250, default="") # amazon 目前规则是250个，我留250个字符够了
    bsr = models.IntegerField(default=0) # 大类目 没抓到就返回0
    rank = models.IntegerField(default=0) # 小类目 没抓到就返回0
    bsr_link = models.TextField(default="") # 把排名部分整个抓取下来，方便用户点击类目的链接
    review = models.IntegerField(default=0) # review 个数
    star = models.FloatField(default=0) # 星星 0-5
    price = models.FloatField(default=0) # 价格
    cart = models.NullBooleanField(default=True) # True表示一切正常， False表示购物车被抢，None表示没有购物车
    sell_yours = models.BooleanField(default=False) # 只判断有没有人跟卖不计算有几个人跟卖
    def __str__(self):
        return str(self.datetime)
    class Meta:
        ordering = ['-datetime'] # 降序 这样才能直接显示当天的数据

class Log(models.Model):
    '''
        由用户自定义添加，然后每个日志完全用户自定义。但是提供一个筛选功能，
        可以让用户只查看某一操作下的Data。例如，筛查“价格”，可以看到所有产品价格调整的日志对应的data
    '''
    data = models.ForeignKey(Data, on_delete=models.CASCADE) # 和每天的data绑定
    content = models.TextField(default="") # 玩
    def __str__(self):
        return self.content

class Critical(models.Model):
    '''差评的抓取频率有多种,而data的设计是每天一次'''
    asin = models.ForeignKey(Asin, on_delete=models.CASCADE) # 表示这个差评属于哪个asin
    number = models.IntegerField(default=0) # 差评的个数 （1、2、3星都是差评）
    datetime = models.DateTimeField(auto_now_add=True)  # 抓取的时间
    def __str__(self):
        return '{}:{}'.format(self.asin, self.number)
    def get_last_one(self): # 返回上一次抓取结果，从而便于比较, 检索关系有点复杂，不知道会不会。。。
        try:
            return self.asin.critical_set.order_by('-datetime')[1] # 返回第二新的critical对象
        except IndexError:
            return self # 如果只有一个critical，那么表示是新数据，那么上面的[1]就报错，直接返回本身

class Review(models.Model):
    '''把具体的差评存下来,和每日的critical绑定'''
    critical = models.ForeignKey(Critical, on_delete=models.CASCADE)
    asin = models.ForeignKey(Asin, on_delete=models.CASCADE)
    link = models.URLField(default="")
    title = models.CharField(max_length=200, default="") # 评论的标题
    content = models.TextField(default="") # 评论的具体内容
    star = models.IntegerField(default=0) # 值只能为1-3,0表示没有抓到
    def __str__(self):
        return self.link

class Proxy(models.Model):
    '''
        所有的代理都放到这里。感觉从数据库读取代理会比从文本读取快。
    '''
    url = models.URLField()
    use = models.IntegerField(default=0) # 使用次数
    fail = models.IntegerField(default=0) # 失败次数 合起来计算成功率
    def __str__(self):
        return self.url
    def get_rate(self): # 成功率
        if self.use: # 不为0
            return (self.use - self.fail)/self.use
        else:
            return 0
    class Meta:
        ordering = ['use'] # 升序 这样使用次数少的在前面，objects.first 可以直接取出









