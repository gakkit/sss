from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError # errors
import django.contrib.auth as auth
from myapp.models import *
import re

@login_required
def index(request):
    user = request.user
    return render(request, "myapp/index.html", {})

def login(request):
    next = request.META['QUERY_STRING'] # 根据next的参数来决定跳转到哪里
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            print('登录成功！')
            if next: # next 不为空跳转到 next 所指向的界面，否则到主页
                return redirect(next)
            else:
                return redirect("/")
        else:
            print('登录失败！')
            # Return an 'invalid login' error message.
            pass
    except MultiValueDictKeyError: # before submitting the form
        pass
    return render(request, "myapp/login.html", {})

def logout(request):
    auth.logout(request)
    return redirect("/login")

def signup(request):
    return render(request, "myapp/signup.html", {})

@login_required
def genrePage(request, pk):
    '''
        具体的分组页面，呈现一个组下面的所有国家。左侧栏继续显示所有的genre。
    '''
    genre = Genre.objects.get(pk=pk)
    user = request.user
    genres = user.genre_set.all()  
    page_name = genre.name  
    context = {
        "genre": genre,
        "genres": genres,
        "page_name": page_name,
    }
    return render(request, "myapp/genre.html", context)

@login_required
def asinPage(request, pk):
    '''
    '''
    asin = Asin.objects.get(pk=pk)
    user = request.user
    genres = user.genre_set.all() 
    return render(request, "myapp/asin.html", {"asin": asin, "genres": genres})

# /add-asin/<pk>
@login_required
def addAsin(request, pk):
    genre = Genre.objects.get(pk=pk)
    user = request.user
    genres = user.genre_set.all() 
    return render(request, "myapp/add_asin.html", {'genre': genre, "genres": genres})

@login_required
def addAsinAction(request):
    '''
        批量添加 asin。提交成功后，跳转一个介绍增加个数情况的页面。
    '''
    def _is_asin(asinlist):
        '''一串asin中 只有有一个不是 就返回False'''
        p = re.compile(r'[A-Z0-9]{10}')
        for asin in asinlist:
            if not p.search(asin):
                return False
        return True

    user = request.user
    genre_pk = request.POST['genre']
    genre = Genre.objects.get(pk=genre_pk)
    country = request.POST['country']
    asins = request.POST['asins'].split()

    # asin 是一个个独立存在的实体，我如果新增 asin，首先要保证之前没有这样的 asin 才会去创建
    # 确定一个 asin 对象的 id 那就是 asin 的值以及国家。

    for asin in asins: # 这里其实是字符串，不是 asin 对象
        existed_asin = Asin.objects.filter(value=asin, country=country) 
        if not existed_asin: # 表示这个 asin 不存在
            asin = Asin(value=asin, country=country)
            asin.save()
        else:
            asin = existed_asin[0] # 如果存在 则提取
        # 无论是否存在这个 asin, bound是一定要新建的
        Bound(asin=asin, genre=genre).save() # 并让这个 asin 和用户的 genre 绑定
    return redirect("/genre/" + genre_pk)

# /del-asin/<pk>
@login_required
def delAsin(request, pk):
    genre = Genre.objects.get(pk=pk)
    user = request.user
    genres = user.genre_set.all()
    return render(request, "myapp/del_asin.html", {'genre': genre, "genres": genres})

@login_required
def delAsinAction(request):
    '''批量删除 asin'''
    p = re.compile(r'pk_(\d+)')
    for i in request.POST:
        try:
            pk = p.findall(i)[0]
            Bound.objects.get(pk=pk).delete()
        except IndexError:
            pass
    return redirect('/del-asin/{}'.format(request.POST['genre']))

@login_required
def export(request, pk):
    '''导出数据'''
    genre = Genre.objects.get(pk=pk)
    user = request.user
    genres = user.genre_set.all()
    return render(request, "myapp/export.html", {'genre': genre, "genres": genres})

@login_required
def addGenreAction(request):
    '''添加 genre 的动作，返回0表示创建成功'''
    try:
        name = request.POST['name']
        user = request.user
        genre = Genre(user=user, name=name)
        genre.save()
        return HttpResponse(genre.pk)
    except:
        return HttpResponse(0)

@login_required
def renGenreAction(request):
    '''重命名 genre'''
    try:
        name = request.POST['name']
        pk = request.POST['pk']
        genre = Genre.objects.get(pk=pk)
        genre.name = name
        genre.save()
        return HttpResponse(0)
    except:
        return HttpResponse(1)

@login_required
def delGenreAction(request):
    '''删除 genre'''
    try:
        pk = request.POST['pk']
        genre = Genre.objects.get(pk=pk)
        genre.delete()
        return redirect("/") # 删了回到首页
    except:
        return HttpResponse("/genre/" + pk) # 原地不动

























