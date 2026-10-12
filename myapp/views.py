from datetime import timedelta
from django.db.models import ( Count, Sum, Avg, Min, Max, Q, F, Value, IntegerField )
from django.utils import timezone
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

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

    
