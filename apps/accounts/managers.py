import random
import string
from os import getenv
from typing import Any, Optional

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


def generate_username() -> str:
    """
    Generates a username in the format "<PREFIX>-<RANDOM>", e.g. "NLB-7F3K9A2Q1X".
    The prefix is derived from the initials of each word in BANK_NAME
    """
    bank_name = getenv("BANK_NAME")
    words = bank_name.split()
    prefix = "".join([word[0] for word in words]).upper()
    remaining_length = 12 - len(prefix) - 1
    random_chars = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=remaining_length)
    )
    username = f"{prefix}-{random_chars}"
    return username


def validate_email_address(email: str) -> None:
    """
    Validates the email format using Django's built-in validator.

    Returns nothing if the email is valid; otherwise raises a
    ValidationError with a user-friendly, translatable message.
    """
    try:
        validate_email(email)

    except ValidationError:
        raise ValidationError(_("Enter a valid email address."))


class UserManager(DjangoUserManager):
    """
    Custom manager for the User model.

    Extends Django's default UserManager to:
    - require both email and password when creating a user
    - auto-generate the username (users don't enter one themselves)
    - validate and normalize the email before saving
    """

    def _create_user(self, email: str, password: str, **extra_fields: Any):
        if not email:
            raise ValueError(_("An email address must be provided."))

        if not password:
            raise ValueError(_("A password must be provided."))

        username = generate_username()
        email = self.normalize_email(email)
        validate_email_address(email)

        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email: str, password: Optional[str] = None, **extra_fields: Any
    ):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: Optional[str] = None, **extra_fields: Any
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True"))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))

        return self._create_user(email, password, **extra_fields)
