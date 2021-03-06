from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property

import mistune


# Create your models here.
class Category(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(max_length=50, verbose_name='名称')
    status = models.PositiveIntegerField(choices=STATUS_ITEMS, default=STATUS_NORMAL, verbose_name='状态')
    is_nav = models.BooleanField(default=False, verbose_name='是否为导航')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '分类'

    def __str__(self):
        return self.name

    # @classmethod
    # def get_navs(cls):  # 需要两次I/O查询操作
    #     categories = cls.objects.filter(status=cls.STATUS_NORMAL)
    #     nav_categories = categories.filter(is_nav=True)
    #     normal_categories = categories.filter(is_nav=False)
    #     return {
    #         'navs': nav_categories,
    #         'categories': normal_categories,
    #     }

    @classmethod
    def get_navs(cls):
        categories = cls.objects.filter(status=cls.STATUS_NORMAL)
        nav_categories = []
        normal_categories = []
        for cate in categories:
            if cate.is_nav:
                nav_categories.append(cate)
            else:
                normal_categories.append(cate)

        return {
            'navs': nav_categories,
            'categories': normal_categories,
        }


class Tag(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(max_length=50, verbose_name='名称')
    status = models.PositiveIntegerField(choices=STATUS_ITEMS, default=STATUS_NORMAL, verbose_name='状态')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '标签'

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_DRAFT, '草稿'),
    )

    title = models.CharField(max_length=255, verbose_name='标题')
    desc = models.CharField(max_length=1024, blank=True, verbose_name='摘要')
    content = models.TextField(verbose_name='正文', help_text='正文必须为MarkDown格式')
    content_html = models.TextField(verbose_name='正文html代码', blank=True, editable=False)
    is_md = models.BooleanField(default=True, verbose_name='Markdown语法')
    status = models.PositiveIntegerField(choices=STATUS_ITEMS, default=STATUS_NORMAL, verbose_name='状态')
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag, verbose_name='标签')  # 可选 or 必须 ???
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    pv = models.PositiveIntegerField(default=1)
    uv = models.PositiveIntegerField(default=1)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '文章'
        ordering = ['-id']  # 跟进id进行降序排列

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_md:
            self.content_html = mistune.markdown(self.content)  # 因为博文需要修改更新，所以生成markdown格式需要另外保存
        else:
            self.content_html = self.content
        super().save(*args, **kwargs)

    @cached_property  # 作用是帮我们把返回的数据绑到实例上，不要每次访问时都去执行tags函数  TODO(Devin):与内在property的异同
    def tags(self):
        return ','.join(self.tag.values_list('name', flat=True))  # TODO(Devin): 多对多关联的获取

    @staticmethod
    def get_by_tag(tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            tag = None
            post_list = []
        else:
            post_list = tag.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')

        return post_list, tag

    @staticmethod
    def get_by_category(category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            category = None
            post_list = []
        else:
            post_list = category.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')

        return post_list, category

    @classmethod
    def all_posts(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL)

    @classmethod
    def latest_posts(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL)[:5]

    @classmethod
    def hot_posts(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-pv').only('id', 'title')[:5]



