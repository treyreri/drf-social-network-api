from django.db import models
from django.db import models
from django.db.models import Q

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = "profile")
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    birth_date = models.DateField(null = True, blank = True)
    avatar = models.ImageField(upload_to="avatars/" , null = True, blank = True)
    def __str__(self):
        return f"Profile: {self.user.username}"


class Post(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name = "posts", )
    title = models.CharField(max_length=200)
    content = models.TextField()
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="likes" ,)
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name="likes") 
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [ models.UniqueConstraint(fields = ["user" , "post"] , name = "unique_user_post_like" ,) ]
        def __str__(self):
            return f"{self.user.username} likes {self.post.title}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "favorites")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="favorites")
    created_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.UniqueConstraint( fields=["user" , "post"] , name = "unique_user_post_favorite", )
            ]
    def __str__(self):
        return f"{self.user.username} : {self.post.title}"


#user - profile Один пользователь имеет один профиль
# user - post один пользователь может создать много постов
# user - like один пользователь может ставить лайки разным публикациям
# post - like одна публикация может получить много лайков
# user - favorite пользователь сохраняет публикации
# post - favorite публикация может быть в избранном у разных пользователей