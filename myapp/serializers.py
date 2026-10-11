from rest_framework import serializers
from .models import User, Profile, Post, Like, Favorite

class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "username", "full_name"]
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    posts_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = User
        fields = [ "id", "username", "full_name", "age", "posts_count", "likes_count", "favorites_count", ]
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()




class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "username", "full_name", "age", "profile", "statistics"]
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    def get_profile(self, obj):
        if not hasattr(obj, "profile"):
            return None
        return { "bio": obj.profile.bio, "city": obj.profile.city,}
    def get_statistics(self, obj):
        posts = obj.posts.all()
        return { "posts_count": posts.count(), "total_views": sum(post.views for post in posts),
            "likes_received": Like.objects.filter( post__user=obj ).count(),
            "favorites_received": Favorite.objects.filter( post__user=obj ).count(), }



class ProfileSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField( queryset=User.objects.all(), source="user", write_only=True,)
    posts_count = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = [ "id", "user", "user_id", "bio", "city", "birth_date", "avatar", "posts_count",]
    def get_posts_count(self, obj):
        return obj.user.posts.count()



class PostListSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(source="user", read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    is_popular = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = [ "id", "title", "content", "author", "views", "likes_count", "favorites_count", "is_popular", "created_at",]
    def get_is_popular(self, obj):
        return obj.likes_count >= 10




class PostDetailSerializer(PostListSerializer):
    liked_by = serializers.SerializerMethodField()
    favorited_by = serializers.SerializerMethodField()
    is_viral = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + [ "liked_by", "favorited_by", "is_viral", "status",]
    def get_liked_by(self, obj):
        users = User.objects.filter(likes__post=obj).distinct()
        return UserShortSerializer(users, many=True).data
    def get_favorited_by(self, obj):
        users = User.objects.filter(favorites__post=obj).distinct()
        return UserShortSerializer(users, many=True).data
    def get_is_viral(self, obj):
        return obj.likes_count >= 100
    def get_status(self, obj):
        if obj.likes_count:
            return "has_likes"
        return "no_likes"




class LikeSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField( queryset=Post.objects.all() )
    user_id = serializers.PrimaryKeyRelatedField( queryset=User.objects.all(),
        source="user", write_only=True, )
    class Meta:
        model = Like
        fields = ["id", "user", "user_id", "post", "created_at"]

    def validate(self, attrs):
        user = attrs.get("user", getattr(self.instance, "user", None))
        post = attrs.get("post", getattr(self.instance, "post", None))
        queryset = Like.objects.filter(user=user, post=post)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError( "Этот пользователь уже поставил лайк данной публикации " )
        return attrs




class FavoriteSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField( queryset=Post.objects.all() )
    user_id = serializers.PrimaryKeyRelatedField( queryset=User.objects.all(), source="user", write_only=True, )
    class Meta:
        model = Favorite
        fields = ["id", "user", "user_id", "post", "created_at"]

    def validate(self, attrs):
        user = attrs.get("user", getattr(self.instance, "user", None))
        post = attrs.get("post", getattr(self.instance, "post", None))
        queryset = Favorite.objects.filter(user=user, post=post)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(  "Эта публикация уже находится в избранном пользователя")
        return attrs
