from django.contrib import admin
from .models import User, ResetPassword

# Register your models here.
admin.site.register(User)
admin.site.register(ResetPassword)
