from django.conf.urls import url

from . import views

app_name = 'myapp' # 这个的作用就是增加一个 namespace

urlpatterns = [
    # project目录下的url必须是开放式的r'^',而app目录下的，必须是封闭式的，否则会url错乱，全部都匹配到r'^'这里
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login, name='login'), # 不加$，免得/next后面的匹配不到
    url(r'^logout$', views.logout, name='logout'),
    url(r'^signup', views.signup, name='signup'),

    # ajax
    url(r'^ajax-send-verify$', views.ajaxSendVerify, name='ajaxSendVerify'),
    url(r'^ajax-check-verify$', views.ajaxCheckVerify, name='ajaxCheckVerify'),
]
