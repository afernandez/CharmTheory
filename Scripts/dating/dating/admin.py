__author__ = 'Alejandro'

from django.contrib import admin
from dating.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('nick', 'first_name', 'last_name', 'gender', 'email')
    search_fields = ('nick', 'first_name', 'last_name', 'email')
    list_filter = ('gender',)
    ordering = ('nick',)

# Allow the objects registered below to be editable view the Admin page.
# Specifying the "Admin" class is optional since it provides columns to display in the Admin page.
# Otherwise, it just displays the "__unicode__" method of the class.
admin.site.register(User, UserAdmin)