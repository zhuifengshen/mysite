from django import template

from comment.forms import CommentForm
from comment.models import Comment


register = template.Library()


@register.inclusion_tag('comment/block.html')
def comment_block(target):
    """
    使用方式：
    1、模板最上面增加（extends下面）
    {% load comment_block %}
    2、在需要展示评论的地方增加
    {% comment_block request.path %}

    """
    return {
        'target': target,
        'comment_form': CommentForm(),
        'comment_list': Comment.get_by_target(target)
    }
