from typing import Any

from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from apps.common.models import TimeStampModel

User = get_user_model()


class Profile(TimeStampModel):
    """Profile model that extends the User model with additional fields.

    Several fields on this model (identification means, employment
    status, marital status, etc.) exist to support AML/KYC (Anti-Money
    Laundering / Know Your Customer) requirements. These fields are
    typically subject to legal retention periods that outlive the
    user's active account - in most jurisdictions such records must be
    kept for several years even after an account is closed.
    """

    class Salutation(models.TextChoices):
        """Salutation choices for the Profile model."""

        MR = "Mr", _("Mr")
        MRS = "Mrs", _("Mrs")
        MS = "Ms", _("Ms")
        DR = "Dr", _("Dr")
        PROF = "Prof", _("Prof")

    class Gender(models.TextChoices):
        """Gender choices for the Profile model."""

        MALE = ("male", _("Male"))
        FEMALE = ("female", _("Female"))
        NON_BINARY = ("non-binary", _("Non-binary"))
        OTHER = ("other", _("Other"))

    class MaritalStatus(models.TextChoices):
        """Marital status choices for the Profile model."""

        SINGLE = ("single", _("Single"))
        MARRIED = ("married", _("Married"))
        DIVORCED = ("divorced", _("Divorced"))
        WIDOWED = ("widowed", _("Widowed"))
        SEPARATED = ("separated", _("Separated"))
        UNKNOWN = ("unknown", _("Unknown"))

    class IdentificationMeans(models.TextChoices):
        """Accepted forms of identification for KYC verification."""

        DRIVERS_LICENSE = ("driver_license", _("Drivers License"))
        NATIONAL_ID = ("national_id", _("National ID"))
        PASSPORT = ("passport", _("Passport"))

    class EmploymentStatus(models.TextChoices):
        """Employment status choices, used for KYC/AML risk assessment."""

        SELF_EMPLOYED = ("self_employed", _("Self Employed"))
        EMPLOYED = ("employed", _("Employed"))
        UNEMPLOYED = ("unemployed", _("Unemployed"))
        RETIRED = ("retired", _("Retired"))
        STUDENT = ("student", _("Student"))

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    title = models.CharField(
        _("Salutation"), max_length=5, choices=Salutation.choices, default=Salutation.MR
    )
    gender = models.CharField(
        _("Gender"), max_length=8, choices=Gender.choices, default=Gender.MALE
    )
    date_of_birth = models.DateField(
        _("Date of Birth"), default=settings.DEFAULT_BIRTH_DATE
    )
    country_of_birth = CountryField(
        _("Country of Birth"), default=settings.DEFAULT_COUNTRY
    )
    place_of_birth = models.CharField(
        _("Place of Birth"), max_length=50, default="Unknown"
    )
    marital_status = models.CharField(
        _("Marital Status"),
        max_length=20,
        choices=MaritalStatus.choices,
        default=MaritalStatus.SINGLE,
    )
    means_of_identification = models.CharField(
        _("Means of Identification"),
        max_length=20,
        choices=IdentificationMeans.choices,
        default=IdentificationMeans.DRIVERS_LICENSE,
    )
    id_issue_date = models.DateField(
        _("ID or Passport Issue Date"), default=settings.DEFAULT_DATE
    )
    id_expiry_date = models.DateField(
        _("ID or Passport Expiry Date"), default=settings.DEFAULT_EXPIRY_DATE
    )
    passport_number = models.CharField(
        _("Passport"), max_length=20, blank=True, null=True
    )
    nationality = models.CharField(_("Nationality"), max_length=30, default="Unknown")
    phone_number = PhoneNumberField(
        _("Phone Number"), max_length=30, default=settings.DEFAULT_PHONE_NUMBER
    )
    address = models.CharField(_("Address"), max_length=100, default="Unknown")
    city = models.CharField(_("City", max_length=100, default="Unknown"))
    country = CountryField(_("Country"), default=settings.DEFAULT_COUNTRY)
    employment_status = models.CharField(
        _("Employment Status"),
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.EMPLOYED,
    )
    empoyer_name = models.CharField(
        _("Employer Name"), max_length=50, blank=True, null=True
    )
    annual_income = models.DecimalField(
        _("Annual Income"), max_digits=12, decimal_places=2, default=0.0
    )
    date_of_employment = models.DateField(
        _("Date of Employment"), blank=True, null=True
    )
    employer_address = models.CharField(
        _("Emloyer Address"), max_length=100, blank=True, null=True
    )
    employer_city = models.CharField(
        _("Employer City"), max_length=50, blank=True, null=True
    )
    employer_state = models.CharField(
        _("Employer State", max_length=50, blank=True, null=True)
    )
    photo = CloudinaryField(
        _("Photo"),
        blank=True,
        null=True,
    )
    photo_url = models.URLField(_("Photo URL"), blank=True, null=True)
    id_photo = CloudinaryField(_("ID Photo"), blank=True, null=True)
    id_photo_url = models.URLField(_("ID Photo URL"), blank=True, null=True)
    signature_photo = CloudinaryField(_("Signature Photo"), blank=True, null=True)
    signature_photo_url = models.URLField(
        _("Signature Photo URL"), blank=True, null=True
    )

    def clean(self) -> None:
        super().clean()
        if self.id_issue_date and self.id_expiry_date:
            if self.id_expiry_date <= self.id_issue_date:
                raise ValueError(_("ID exipry date must come after issue date."))

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def is_complete_with_next_of_kin(self):
        required_fields = [
            self.title,
            self.gender,
            self.date_of_birth,
            self.country_of_birth,
            self.place_of_birth,
            self.marital_status,
            self.means_of_identification,
            self.id_issue_date,
            self.id_expiry_date,
            self.nationality,
            self.phone_number,
            self.address,
            self.city,
            self.country,
            self.employment_status,
            self.photo,
            self.id_photo,
            self.signature_photo,
        ]

        return all(required_fields) and self.next_of_kin.exits()

    def __str__(self) -> str:
        return f"{self.title} {self.user.first_name}'s Profile"


class NextOfKin(TimeStampModel):
    """Emergency/contact person designated by a user's Profile, used to
    reach a family member or other trusted contact when the bank
    cannot reach the account holder directly. A profile may have
    multiple next of kin, but only one may be marked as primary
    (enforced via the unique constraint in Meta below).
    """

    class Salutation(models.TextChoices):
        """Salutation choices for the NextOfKin model."""

        MR = "Mr", _("Mr")
        MRS = "Mrs", _("Mrs")
        MS = "Ms", _("Ms")
        DR = "Dr", _("Dr")
        PROF = "Prof", _("Prof")

    class Gender(models.TextChoices):
        """Gender choices for the NextOfKin model."""

        MALE = ("male", _("Male"))
        FEMALE = ("female", _("Female"))
        NON_BINARY = ("non-binary", _("Non-binary"))
        OTHER = ("other", _("Other"))

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="next_of_kin"
    )
    title = models.CharField(
        _("Salutation"), max_length=5, choices=Salutation.choices, default=Salutation.MR
    )
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    other_names = models.CharField(
        _("Other Names"), max_length=50, blank=True, null=True
    )
    date_of_birth = models.DateField(_("Date of Birth"))
    gender = models.CharField(_("Gender"), max_length=8, choices=Gender.choices)
    relationship = models.CharField(_("Relationship"), max_length=50)
    email_address = models.EmailField(_("Email Address"), db_index=True)
    phone_number = PhoneNumberField(_("Phone Number"))
    address = models.CharField(_("Address"), max_length=100)
    city = models.CharField(
        _("City"),
        max_length=50,
    )
    country = CountryField(_("Country"))
    is_primary = models.BooleanField(_("Is primary next of kin"), default=False)

    def clean(self) -> None:
        super().clean()
        if self.is_primary:
            primary_kin = NextOfKin.objects.filter(
                profile=self.profile, is_primary=True
            ).exclude(pk=self.pk)
            if self.primary_kin.exists():
                raise ValidationError(_("There can be only one primary next of kin."))

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} - Next of Kin for {self.profile.user.full_name}"

    class Meta:
        constrains = [
            models.UniqueConstraint(
                fields=["profile", "is_primary"],
                condition=models.Q(is_primary=True),
                name="unique_primary_next_of_kin",
            )
        ]
