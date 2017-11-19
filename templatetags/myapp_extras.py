from django import template

register = template.Library()


# 为了展现不懂data的变化量
@register.filter
def delta(data, data_type):
    if data:
        return data.delta(data_type)
    else:
        return ''