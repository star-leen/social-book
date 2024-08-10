from django.db import models
from django.contrib.auth import get_user_model
import uuid


User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(upload_to='profile_images', default="blank-profile-picture.png")
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.user.username)

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user.username)

class LikePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.username)

class FollowersCount(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed', null=True, blank=True)

    def __str__(self):
         return str(self.followed.username)