from django.db import models
from user.models import User

# Create your models here.


class Space(models.Model):
    title = models.CharField(
        max_length=300, blank=False, null=False, unique=False, default=""
    )
    description = models.CharField(
        max_length=300, blank=True, null=True, unique=False, default=""
    )
    created_time = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User,
        related_name="own_spaces",
        null=True,
        unique=False,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title


class Label(models.Model):
    name = models.CharField(
        max_length=300, blank=False, null=False, unique=False, default=""
    )

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(
        max_length=300, blank=False, null=False, unique=False, default=""
    )
    description = models.CharField(
        max_length=300, blank=True, null=True, unique=False, default=""
    )
    platform = models.CharField(
        max_length=300, blank=False, null=False, unique=False, default=""
    )
    link = models.CharField(
        max_length=300, blank=False, null=False, unique=False, default=""
    )
    label = models.ManyToManyField(Label, blank=True, null=True)
    image = models.FileField(upload_to="posts", blank=True, null=True, unique=False)
    is_private = models.BooleanField(null=True, blank=True, default=False)
    created_time = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User,
        related_name="own_posts",
        null=True,
        unique=False,
        on_delete=models.CASCADE,
    )
    space = models.ForeignKey(
        Space,
        related_name="space_posts",
        null=True,
        unique=False,
        on_delete=models.CASCADE,
    )
    liked_by = models.ManyToManyField(
        User, blank=True, null=True, related_name="liked_posts"
    )

    def __str__(self):
        return self.title
