from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    自定义分页类，支持前端指定page_size参数
    """
    # 默认每页显示的数据条数
    page_size = 10
    # 允许前端指定每页显示数据条数的参数名
    page_size_query_param = 'page_size'
    # 每页显示数据条数的最大值
    max_page_size = 1000

    def get_paginated_response(self, data):
        """
        自定义分页返回格式
        """
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })