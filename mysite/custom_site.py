from django.contrib.admin import AdminSite


class CustomSite(AdminSite):
    site_header = 'The Zion'
    site_title = 'The Zion 管理后台'
    index_title = '首页'


custom_site = CustomSite(name='custom_admin')
