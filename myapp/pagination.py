from rest_framework.pagination import PageNumberPagination

class StandartResultSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

#пагинация разделяет большое список на страницы. Например ?page=2&page_size=5 вернет вторую страницу по пять объектов