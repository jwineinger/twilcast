from django.contrib import admin
from models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','phone_number')
admin.site.register(UserProfile, UserProfileAdmin)
