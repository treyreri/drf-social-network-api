
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ( UserViewSet, ProfileViewSet, PostViewSet, LikeViewSet, FavoriteViewSet, post_likes, dashboard, )

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("profiles", ProfileViewSet, basename="profile")
router.register("posts", PostViewSet, basename="post")
router.register("likes", LikeViewSet, basename="like")
router.register("favorites", FavoriteViewSet, basename="favorite")

urlpatterns = [
    path("", include(router.urls)),
    path("posts/<int:pk>/likes/", post_likes, name="post-likes"),
    path("dashboard/", dashboard, name="dashboard"), ]
