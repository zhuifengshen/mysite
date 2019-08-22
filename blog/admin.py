from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.urls import reverse
from django.utils.html import format_html

from .models import Category, Tag, Post
from .adminforms import PostAdminForm
from mysite.custom_site import custom_site
from mysite.base_admin import BaseOwnerAdmin


# Register your models here.
class PostInline(admin.TabularInline):  # 其他样式 admin.StackedInline
    fields = ('title', 'desc')
    extra = 1  # 额外空白的个数
    model = Post


@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline]  # 在分类页面下直接编辑文章
    list_display = ('name', 'status', 'is_nav', 'owner', 'created_time', 'post_count')
    fields = ('name', 'status', 'is_nav')

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'owner', 'created_time')
    fields = ('name', 'status')


class CategoryOwnerFilter(admin.SimpleListFilter):
    """
    自定义过滤器，只展示当前用户自己的分类
    """
    title = '分类'
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=category_id)
        return queryset


@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm  # 文章描述字段更改为Textarea展示
    list_display = ('title', 'category', 'status', 'created_time', 'operator')  # operator为新增列
    list_display_links = []

    list_filter = [CategoryOwnerFilter]
    search_fields = ['title', 'category__name']

    actions_on_top = True
    actions_on_bottom = True

    save_on_top = True  # 控制是否在页面顶部展示保存按钮

    # fields = (  # 限定要展示的字段及其顺序
    #     ('category', 'title'),
    #     'desc',
    #     'status',
    #     'content',
    #     'tag',
    # )
    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (('title', 'category'), 'status',)
        }),
        ('内容', {
            'fields': ('desc', 'content'),
        }),
        ('额外信息', {
            'classes': ('wide',),  # 'wide' or 'collapse' 隐藏后样式无法显示???
            'fields': ('tag',),
        })
    )
    # 配置多对多字段的展示方式
    filter_horizontal = ('tag',)
    # filter_vertical = ('tag',)

    def operator(self, obj):
        return format_html('<a href="{}">编辑</a>', reverse('custom_admin:blog_post_change', args=(obj.id,)))

    operator.short_description = '操作'

    class Media:
        css = {
            'all': ('https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css',),
        }
        js = ('https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js',)


@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('object_repr', 'object_id', 'action_flag', 'user', 'change_message')