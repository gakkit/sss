# 用于处理用户提交的内容 处理妥当后 再放入数据库
# 这部分其实发生在 view 但是因为是功能型，所以为了不让views太臃肿，独立出来

# 规则如下：
# 1、 禁止保存重复的 asin (value, country, user 三个同一)；
# 2、 禁止保存重复的 store (user, seller_id 同一)