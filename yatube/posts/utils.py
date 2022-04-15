from django.core.paginator import Paginator

from yatube.settings import AMT_POSTS


def paginator_mod(lists, request):
    paginator = Paginator(lists, AMT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
