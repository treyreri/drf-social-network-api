from datetime import timedelta
from django.db.models import ( Count, Sum, Avg, Min, Max, Q, F, Value, IntegerField )
from django.utils import timezone
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models.functions import Coalesce
from .models import *
from .serializers import *
from .filters import PostFilter
from rest_framework import viewsets, status

def post_queryset():
    return Post.objects.annotate( likes_count=Count("likes", distinct=True), favorites_count=Count("favorites", distinct=True), )

def user_queryset():
    return User.objects.annotate( posts_count=Count("posts", distinct=True), likes_count=Count("likes", distinct=True), favorites_count=Count("favorites", distinct=True), )


class UserViewSet(viewsets.ModelViewSet):
    queryset = user_queryset()
    serializer_class = UserListSerializer

    def get_queryset(self):
        return user_queryset()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        if self.action == "list":
            return UserListSerializer
        return UserListSerializer

    @action(detail=False, methods=["get"], url_path="most-active")
    def most_active(self, request):
        users = user_queryset().order_by("-posts_count", "id")[:10]
        data = [ {"id": user.id, "username": user.username, "posts_count": user.posts_count,} for user in users]
        return Response(data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        stats = User.objects.aggregate(
            total_users=Count("id"),
            average_age=Avg("age"),
            min_age=Min("age"),
            max_age=Max("age"),  )

        return Response({
            "total_users": stats["total_users"] or 0,
            "average_age": round(stats["average_age"], 1)
            if stats["average_age"] is not None else None,
                         "min_age": stats["min_age"],
                         "max_age": stats["max_age"], })

    @action(detail=True, methods=["get"], url_path="posts")
    def user_posts(self, request, pk=None):
        user = self.get_object()
        posts = post_queryset().filter(user=user).order_by("-created_at")
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(posts, request)

        results = [ { "id": post.id, "title": post.title,  "likes_count": post.likes_count,  "views": post.views, } for post in page]
        return Response({
            "user": {  "id": user.id,  "username": user.username, },
            "posts_count": posts.count(),
            "results": results, })
    @action(detail=True, methods=["get"])
    def favorites(self, request, pk=None):
        user = self.get_object()
        favorites = Favorite.objects.filter(user=user).select_related("post")
        return Response({
            "user": user.username,
            "favorites_count": favorites.count(),
            "results": [ { "post_id": fav.post.id, "title": fav.post.title,
                    "likes_count": fav.post.likes.count(), "views": fav.post.views,  } for fav in favorites ], })
    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        user = self.get_object()
        posts = user.posts.all()
        posts_stats = posts.aggregate(
            posts_count=Count("id"), total_views=Coalesce(Sum("views"), 0),  average_views=Avg("views"), )
        likes_received = Like.objects.filter(post__user=user).count()
        favorites_received = Favorite.objects.filter( post__user=user ).count()
        week_ago = timezone.now() - timedelta(days=7)
        posts_last_7_days = posts.filter(created_at__gte=week_ago).count()
        return Response({  "user": {  "id": user.id, "username": user.username,"full_name": f"{user.first_name} {user.last_name}".strip(), },
            "posts": {
                "posts_count": posts_stats["posts_count"],
                "total_views": posts_stats["total_views"],
                "average_views": posts_stats["average_views"],  },
            "engagement": {
                "likes_received": likes_received,
                "favorites_received": favorites_received,
                "likes_given": user.likes.count(),
                "favorites_given": user.favorites.count(), },
            "activity": {
                "posts_last_7_days": posts_last_7_days,
                "is_active_user": posts_last_7_days > 0, }, })

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    @action(detail=False, methods=["get"], url_path="city-statistics")
    def city_statistics(self, request):
        data = ( Profile.objects.values("city") .annotate(users_count=Count("user", distinct=True)) .order_by("-users_count", "city"))
        return Response(list(data))


class PostViewSet(viewsets.ModelViewSet):
    queryset = post_queryset().select_related("user")
    serializer_class = PostListSerializer
    def get_queryset(self):
        return post_queryset().select_related("user").order_by("-created_at")
    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"])
    def popular(self, request):
        posts = post_queryset().filter( likes_count__gte=10 ).order_by("-likes_count", "-created_at")
        return Response([ {
                "id": post.id,
                "title": post.title,
                "likes_count": post.likes_count,
                "favorites_count": post.favorites_count,
                "is_popular": True,  } for post in posts ])

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        posts = self.get_queryset().filter( Q(title__icontains=query) | Q(content__icontains=query))
        return Response(PostListSerializer(posts, many=True).data)

    @action(detail=False, methods=["get"])
    def filter(self, request):
        filtered = PostFilter( request.query_params, queryset=self.get_queryset(), ).qs
        return Response(PostListSerializer(filtered, many=True).data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        stats = post_queryset().aggregate(
            total_posts=Count("id", distinct=True),
            total_views=Coalesce(Sum("views"), 0),
            average_views=Avg("views"),
            max_views=Max("views"),
            min_views=Min("views"),)

        return Response({**stats,
            "total_likes": Like.objects.count(),
            "total_favorites": Favorite.objects.count(), })

    @action(detail=False, methods=["get"], url_path="author-statistics")
    def author_statistics(self, request):
        data = user_queryset().annotate(
            total_views=Coalesce(Sum("posts__views"), 0),
            average_views=Avg("posts__views"),
            likes_received=Count("posts__likes", distinct=True), ).order_by("id")

        return Response([ {
                "user_id": user.id,
                "username": user.username,
                "posts_count": user.posts_count,
                "total_views": user.total_views,
                "average_views": user.average_views,
                "likes_received": user.likes_received,  } for user in data ])