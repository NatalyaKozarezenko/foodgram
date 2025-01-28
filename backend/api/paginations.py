"""Настройки построничного ывода."""

from rest_framework.pagination import PageNumberPagination

from api.constants import PAGE_SIZE_PAGINATOR


class Pagination(PageNumberPagination):
    """Построничный вывод."""

    page_size = PAGE_SIZE_PAGINATOR
    page_size_query_param = "limit"
