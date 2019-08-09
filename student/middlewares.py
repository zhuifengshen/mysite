import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimeItMiddleware(MiddlewareMixin):
    """
    process_request - 一个请求来到middelware层，进入的第一个方法。一般情况我们可以在这里做一些校验，比如用户登录，或者HTTP中是否有认证头之类的验证。这个方法需要两种返回值，HttpResponse或者None，如果返回HttpResponse，那么接下来的处理方法只会执行process_response，其他的方法将不会被执行。这里需要注意的是，如果你的middleware在settings配置的MIDDLEWARE_CLASS的第一个的话，那么剩下的middleware也不会被执行。另外一个返回值是None，如果返回None，那么Django会继续执行其他的方法。

    process_view - 这个方法是在process_request之后执行的，参数如上面代码所示，其中的func就是我们将要执行的view方法，因此我们要统计一个view的执行时间，可以在这里来做。它的返回值跟process_request一样，HttpResponse/None，逻辑也是一样。如果返回None，那么Django会帮你执行view函数，从而得到最终的Response。

    process_template_response - 执行完上面的方法，并且Django帮忙我们执行完view之后，拿到最终的response，如果是使用了模板的Response(是指通过return render(request, 'index.html', context={})的方式返回Response，就会来到这个方法中。这个方法中我们可以对response做一下操作，比如Content-Type设置，或者其他HEADER的修改/增加。

    process_response - 当所有流程都处理完毕，就来到了这个方法，这个方法的逻辑跟process_template_response是完全一样的。只是process_template_response是针对带有模板的response的处理。

    process_exception - 上面的所有处理方法是按顺序介绍的，而这个不太一样。只有在发生异常时，才会进入到这个方法。哪个阶段发生的异常呢？可以简单的理解为在将要调用的view中出现异常（就是在process_view的func函数中）或者返回的模板Response在render时发生的异常，会进入到这个方法中。但是需要注意的是，如果你在process_view中手动调用了func，就像我们上面做的那样，那就不会触发process_exception了。这个方法接收到异常之后，可以选择处理异常，然后返回一个含有异常信息的HttpResponse，或者直接返回None，不处理，这种情况Django会使用自己的异常模板。
    """
    def process_request(self, request):
        return

    def process_view(self, request, func, *args, **kwargs):
        if request.path != reverse('student:index'):
            return None

        start = time.time()
        response = func(request)
        costed = time.time() - start
        print('**** {:.2f}s ****'.format(costed))
        logger.info('**** {:.2f}s ****'.format(costed))
        return response

    def process_template_response(self, request, response):
        return response

    def process_response(self, request, response):
        return response

    def process_exception(self, request, exception):
        pass