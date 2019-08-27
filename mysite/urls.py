"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.sitemaps import views as sitemap_views

from blog.views import (IndexView, CategoryView, TagView, PostDetailView, SearchView, AuthorView, LinkListView)
from blog.rss import LatestPostFeed
from blog.sitemap import PostSitemap
from comment.views import CommentView
from .custom_site import custom_site

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    re_path(r'^category/(?P<category_id>\d+)/$', CategoryView.as_view(), name='category-list'),
    re_path(r'^tag/(?P<tag_id>\d+)/$', TagView.as_view(), name='tag-list'),
    re_path(r'^post/(?P<post_id>\d+).html$', PostDetailView.as_view(), name='post-detail'),
    re_path(r'author/(?P<owner_id>\d+)/$', AuthorView.as_view(), name='author'),
    path('search/', SearchView.as_view(), name='search'),
    path('comment/', CommentView.as_view(), name='comment'),
    path('links/', LinkListView.as_view(), name='links'),  # TODO(Devin): 添加友情链接
    re_path(r'^rss/|feed/', LatestPostFeed(), name='rss'),
    path('sitemap.xml', sitemap_views.sitemap, {'sitemaps': {'posts': PostSitemap}}),

    path('polls/', include('polls.urls')),
    path('student/', include('student.urls')),
    path('myapp/', include('myapp.urls')),
    path('super_admin/', admin.site.urls, name='super-admin'),
    path('admin/', custom_site.urls, name='admin'),
]
