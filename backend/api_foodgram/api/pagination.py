from api_foodgram.settings import NUM_PAG_IN_PAGE
from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Пагинатор переопределенный по ТЗ"""
    page_size_query_param = 'limit'
    page_size = NUM_PAG_IN_PAGE
