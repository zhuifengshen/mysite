from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


# Create your models here.
class Link(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    title = models.CharField(max_length=50, verbose_name='标题')
    href = models.URLField(verbose_name="链接")  # 默认长度为200
    status = models.PositiveIntegerField(choices=STATUS_ITEMS, default=STATUS_NORMAL, verbose_name='状态')
    weight = models.PositiveIntegerField(choices=zip(range(1, 6), range(1, 6)), default=1, verbose_name='权重', help_text='权重高展示顺序靠前')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '友链'
        ordering = ['-weight']

    def __str__(self):
        return '友链' + self.title


class SideBar(models.Model):
    STATUS_SHOW = 1
    STATUS_HIDE = 0
    STATUS_ITEMS = (
        (STATUS_SHOW, '展示'),
        (STATUS_HIDE, '隐藏'),
    )
    DISPLAY_HTML = 1
    DISPLAY_LATEST = 2
    DISPLAY_HOT = 3
    DISPLAY_COMMENT = 4
    DISPLAY_LINK = 5
    SIDE_TYPE = (
        (DISPLAY_HTML, 'HTML'),
        (DISPLAY_LATEST, '最新文章'),
        (DISPLAY_HOT, '最热文章'),
        (DISPLAY_COMMENT, '最近评论'),
        (DISPLAY_LINK, '友情链接'),
    )
    title = models.CharField(max_length=50, verbose_name='标题')
    display_type = models.PositiveIntegerField(choices=SIDE_TYPE, default=1, verbose_name='展示类型')
    content = models.TextField(blank=True, help_text='如果设置的不是HTML类型，可为空', verbose_name='内容')
    status = models.PositiveIntegerField(choices=STATUS_ITEMS, default=STATUS_SHOW, verbose_name='状态')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '侧边栏'

    def __str__(self):
        return '侧边栏' + self.title

    @classmethod
    def get_all(cls):
        return cls.objects.filter(status=cls.STATUS_SHOW)

    @property
    def content_html(self):
        """直接渲染模板"""
        from blog.models import Post
        from comment.models import Comment

        result = ''
        if self.display_type == self.DISPLAY_HTML:
            result = mark_safe(self.content)
        elif self.display_type == self.DISPLAY_LATEST:
            context = {
                'posts': Post.latest_posts()
            }
            result = render_to_string('config/blocks/sidebar_posts.html', context)
        elif self.display_type == self.DISPLAY_HOT:
            context = {
                'posts': Post.hot_posts()
            }
            result = render_to_string('config/blocks/sidebar_posts.html', context)
        elif self.display_type == self.DISPLAY_COMMENT:
            context = {
                'comments': Comment.objects.filter(status=Comment.STATUS_NORMAL)[:5]  # .select_related('target')
            }
            result = render_to_string('config/blocks/sidebar_comments.html', context)
        elif self.display_type == self.DISPLAY_LINK:
            context = {
                'links': Link.objects.filter(status=Link.STATUS_NORMAL)[:5]
            }
            result = render_to_string('config/blocks/sidebar_links.html', context)

        return result
