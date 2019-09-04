import json
import logging
from datetime import date
from json import JSONDecodeError

import requests
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from django.core.cache import cache

from .models import Post, Tag, Category
from config.models import SideBar, Link
from comment.models import Comment
from comment.forms import CommentForm


logging.basicConfig(level=logging.DEBUG)


class CommonViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # TODO(Devin): object -> super() ???
        context.update({
            'sidebars': SideBar.get_all(),
        })
        context.update(Category.get_navs())
        return context


# Create your views here.
class IndexView(CommonViewMixin, ListView):
    queryset = Post.all_posts()
    paginate_by = 20
    context_object_name = 'post_list'
    template_name = 'blog/list.html'


class AuthorView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author_id = self.kwargs.get('owner_id')
        author = get_object_or_404(User, pk=author_id)
        context.update({
            'author': author,
        })

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.kwargs.get('owner_id')

        return queryset.filter(owner_id=author_id)


class CategoryView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        context.update({
            'category': category,
        })

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')

        return queryset.filter(category_id=category_id)


class TagView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_id = self.kwargs.get('tag_id')
        tag = get_object_or_404(Tag, pk=tag_id)
        context.update({
            'tag': tag,
        })

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_id = self.kwargs.get('tag_id')

        return queryset.filter(tag__id=tag_id)


class SearchView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'keyword': self.request.GET.get('keyword', '')
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get('keyword', '')
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword) | Q(desc__icontains=keyword))


class PostDetailView(CommonViewMixin, DetailView):
    # queryset = Post.latest_posts()  # TODO(Devin): model ???
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    # 评论实现方式不符合"开闭原则"
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context.update({
    #         'comment_form': CommentForm,
    #         'comment_list': Comment.get_by_target(self.request.path),
    #     })
    #     return context

    # 每次访问都会写一次数据库，写操作的成本远大于读操作，而且还存在刷量问题
    # def get(self, request, *args, **kwargs):
    #     response = super().get(request, *args, **kwargs)
    #     Post.objects.filter(pk=self.object.id).update(pv=F('pv')+1, uv=F('uv')+1)
    #
    #     # 调试 - 查看SQL语句
    #     from django.db import connection
    #     print(connection.queries)
    #     return response

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.handle_visited()
        return response

    def handle_visited(self):
        """
        Django的缓存默认使用内存缓存（进程间独立），只适合单进程。
        在实际项目中推进使用memcached or redis，同时避免用户在请求数据过程中进行写操作，这时比较合理的方案就是：独立的统计服务
        """
        increase_pv = False
        increase_uv = False
        uid = self.request.uid
        pv_key = 'pv:%s:%s' % (uid, self.request.path)
        uv_key = 'uv:%s:%s:%s' % (uid, str(date.today()), self.request.path)

        if not cache.get(pv_key):
            increase_pv = True
            cache.set(pv_key, 1, 1*60)

        if not cache.get(uv_key):
            increase_uv = True
            cache.set(uv_key, 1, 24*60*60)

        if increase_pv and increase_uv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv')+1, uv=F('uv')+1)
        elif increase_pv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv')+1)
        elif increase_uv:
            Post.objects.filter(pk=self.object.id).update(uv=F('uv')+1)


class LinkListView(CommonViewMixin, ListView):
    queryset = Link.objects.filter(status=Link.STATUS_NORMAL)
    template_name = 'config/links.html'
    context_object_name = 'link_list'


# class CrawlingView(CommonViewMixin, ListView):
    # queryset = []
    # template_name = 'blog/crawling.html'

class CrawlingView(View):
    def get(self, request):
        context = {}
        context.update({
            'sidebars': SideBar.get_all(),
        })
        context.update(Category.get_navs())
        return render(request, 'blog/crawling.html', context=context)


def crawl(request):
    gank_api = 'http://gank.io/api/today'
    data = {'num': -1, 'msg': 'failed'}
    try:
        response = requests.get(gank_api)
    except requests.exceptions.RequestException:
        msg = '干货集中营文章获取失败，Request Exception!'
        logging.error(msg)
        data['msg'] = msg
    else:
        try:
            result = response.json()
            if result['error']:
                data['msg'] = '干货集中营API返回数据错误！'
            else:
                results = result.get('results', {})
                android_list = results.get('Android', [])
                android_num = gen_post_list(android_list, 'Android')
                ios_list = results.get('iOS', [])
                ios_num = gen_post_list(ios_list, 'iOS')

                front_end_list = results.get('前端', [])
                front_end_num = gen_post_list(front_end_list, '前端')
                post_num = android_num + ios_num + front_end_num

                data['num'] = post_num
                data['msg'] = 'Android文章 %d 篇， iOS文章 %d 篇， 前端文章 %d 篇' % (android_num, ios_num, front_end_num)
        except JSONDecodeError:
            msg = '服务器响应异常，状态码：%s, 响应内容：%s' % (response.status_code, response.text)
            logging.error(msg)
            data['msg'] = msg
        except Exception as e:
            logging.error(e)
            data['msg'] = '程序处理出现异常，请联系管理员查看错误日志，谢谢！'

    return HttpResponse(json.dumps(data), content_type='application/json')


def gen_post_list(data_list, data_type):
    if data_type == 'Android':
        category = Category.objects.get(name='Android')
    elif data_type == 'iOS':
        category = Category.objects.get(name='iOS')
    elif data_type == '前端':
        category = Category.objects.get(name='前端')
    username = '干货集中营'
    user = User.objects.get(username=username)
    third_party_tag = Tag.objects.get(name='第三方')
    num = 0
    for item in data_list:
        if not Post.objects.filter(title=item['desc']):
            title = item.get('desc', '我是个标题')
            url = item.get('url', reverse('index'))
            content = "原文地址：[%s](%s)" % (title, url)
            post = Post(title=title, desc=url, content=content, category=category, owner=user)
            post.save()
            post.tag.add(third_party_tag)
            num += 1
        else:
            logging.debug('平台：' + username + ' 分类：' + data_type + '文章：' + item['desc'] + ' 已存在')

    return num


def post_list(request, category_id=None, tag_id=None):
    tag = None
    category = None

    if tag_id:
        post_list, tag = Post.get_by_tag(tag_id)
    elif category_id:
        post_list, category = Post.get_by_category(category_id)
    else:
        post_list = Post.latest_posts()

    context = {
        'category': category,
        'tag': tag,
        'post_list': post_list,
        'sidebars': SideBar.get_all(),
    }
    context.update(Category.get_navs())

    return render(request, 'blog/list.html', context=context)


def post_detail(request, post_id=None):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        post = None

    context = {
        'post': post,
        'sidebars': SideBar.get_all(),
    }
    context.update(Category.get_navs())

    return render(request, 'blog/detail.html', context=context)

