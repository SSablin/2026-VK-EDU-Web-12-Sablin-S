from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from core.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    can_delete = False
    max_num = 1


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "user")
    search_fields = ("nickname", "user__username")
    raw_id_fields = ("user",)
    list_select_related = ("user",)