from rest_framework.pagination import PageNumberPagination

from api_foodgram import settings


class LimitPageNumberPagination(PageNumberPagination):
    """Пагинатор переопределенный по ТЗ"""
    page_size_query_param = 'limit'
    page_size = settings.NUM_PAG_IN_PAGE
