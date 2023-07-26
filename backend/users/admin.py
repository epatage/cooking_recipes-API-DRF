from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "password",
    )
    search_fields = ("email", "username")
    list_filter = ("email", "username")
    empty_value_display = "-пусто-"


admin.site.register(Subscription)
