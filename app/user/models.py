from django.db import models
from django.contrib.auth.models import User
from django_resized import ResizedImageField
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class User(User):
    photo = ResizedImageField(size=[200, 200],quality=100,force_format='PNG', upload_to='user_photo', blank=True, null= True, unique = False, default = '')
    phone_number = models.BigIntegerField('phone number', blank=True, unique=True, null=True,
                                          validators=[MinValueValidator(1000000), MaxValueValidator(10000000000 - 1)])