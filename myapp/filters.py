import django_filters
from .models import Post

class PostFilter(django_filters.FilterSet):
    min_views = django_filters.NumberFilter(field_name = "views" , lookup_expr="gte" ,)
    max_views = django_filters.NumberFilter( field_name="views", lookup_expr="lte", )
    user_id = django_filters.NumberFilter( field_name="user_id", )
    class Meta:
        model = Post
        fields = ["min_views", "max_views", "user_id"] 

#теперь можно будет передавать параметры в URL например : /api/posts/filter/?min_views=100&max_views=2000&user_id=1