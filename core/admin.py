from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from core.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "user")
    list_filter = ("user",)
    search_fields = ("nickname", "user__username")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')