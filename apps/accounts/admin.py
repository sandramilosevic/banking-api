from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import UserChangeForm, UserCreationForm


@admin.register(User)
class CustomerUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    model = User
    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "role",
    ]
    list_filter = ["email", "is_staff", "is_active", "role"]
    fieldsets = (
        (
            _("Login credentials"),
            {
                "fields": (
                    "username",
                    "emails",
                    "password",
                )
            },
        ),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "id_no", "role")},
        ),
        (
            _("Account status"),
            {
                "fields": (
                    "account_status",
                    "failed_login_attempts",
                    "last_failed_login",
                )
            },
        ),
    )
