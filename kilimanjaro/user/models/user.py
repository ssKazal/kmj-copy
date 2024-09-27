import datetime
import uuid
import random
from typing import NoReturn

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from core.utils import generate_uids
from country.models import Country

User = settings.AUTH_USER_MODEL  # As model has define after ModelManager


class UserManager(BaseUserManager):
    """A class to create "user".

    Methods
    -------
    create_user(email="", phone_number=int, password=""):
        Returns None
    -------
    create_superuser(email="", password=""):
        Returns "user"
    """

    use_in_migrations = True

    def create_user(self, email: str, phone_number: int, password: str) -> NoReturn:
        """
        Returns ValueError

        Parameters
        ----------
        email : str
        phone_number : int
        password : int
        """
        raise ValueError("Use '/admin/user' for creating new user.")

    def create_superuser(self, email: str, password: str) -> User:
        """
        Returns "superuser" object

        If the arguments "email" and "password" is passed, then it create a super user with that email and password

        Parameters
        ----------
        email : str
        password : str

        Return
        ----------
        User
        """

        if not email:
            raise ValueError("Enter an email address")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser, TimeStampedModel):
    def _upload_to_profile_picture(self, filename):
        """Using filename returns "profile_picture" field file saving path"""

        uid = generate_uids()  # Custom function to generate unique id
        now_time = datetime.datetime.now()
        return (
            "profile-picture/id-"
            + uid
            + "/"
            + str(now_time.strftime("%Y-%m-%d"))
            + "/"
            + filename
        )

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    username = models.CharField(max_length=225, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=225, null=True)
    last_name = models.CharField(max_length=225, null=True)
    date_of_birth = models.DateField(null=True)
    phone_number = PhoneNumberField(
        null=True, blank=True
    )  # Because of uniqueness of 'null' we can't use unique=True here
    email = models.EmailField(
        max_length=225, null=True, blank=True
    )  # Because of uniqueness of 'null' we can't use unique=True here
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, verbose_name="country"
    )
    city = models.CharField(max_length=225, null=True)
    profile_picture = models.ImageField(
        upload_to=_upload_to_profile_picture, max_length=1000, null=True
    )  # _upload_to_profile_picture() has called here
    age_consent = models.PositiveIntegerField(null=True)
    terms_and_condition = models.BooleanField(null=True)
    is_phone_number_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email_subscription = models.BooleanField(null=True, blank=True)
    __email = None
    __phone_number = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__email = self.email
        self.__phone_number = self.phone_number

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    """
        User object string representation first priority 
        username second full name last email
    """

    def __str__(self):
        if self.first_name and self.last_name:
            to_represent = self.get_full_name()
        elif self.username:
            to_represent = self.username
        else:
            to_represent = "GigUP User"

        return to_represent

    @property
    def profile_image(self) -> str:
        """Returns profile image with host"""
        return f"{settings.SITE_HOST}{self.profile_picture.url}" if self.profile_picture else ""

    def save(self, *args, **kwargs):
        """Overrides save method for generate a username if not exists"""
        
        self.username = self.username
        if not self.username:
            while True: # checking through loop username is exists or not
                username = f"{self.first_name}{self.last_name}{random.randint(1000, 100000)}"
                is_exists = User.objects.filter(username=username).exists()
                if not is_exists:
                    self.username = username
                    break
        return super().save(*args, **kwargs)

    def clean(self):
        """Extends this method to keep 'email' & 'phone_number' unique and to check 'age' validation"""

        email = self.email
        phone_number = self.phone_number
        date_of_birth = self.date_of_birth

        errors_list = {}

        if not (email or phone_number):
            errors_list.update({"email": "Either phone number or email is required"})
            errors_list.update({"phone_number": "Either phone number or email is required"})

        if email and User.objects.exclude(id=self.id).filter(email=email).exists():
            errors_list.update({"email": "User with this email already exists"})

        if (
            phone_number
            and User.objects.exclude(id=self.id)
            .filter(phone_number=phone_number)
            .exists()
        ):
            errors_list.update(
                {"phone_number": "User with this phone_number already exists"}
            )

        today = timezone.now().date()
        if (
            date_of_birth
            and (
                date_of_birth.year + 18,
                date_of_birth.month,
                date_of_birth.day,
            )
            > (today.year, today.month, today.day)
        ):
            errors_list.update({"date_of_birth": "Min age: 18 years"})

        if errors_list:
            raise ValidationError(errors_list)


    def can_chat_together(self, partner):
        """Two customers or two Skilled Workers can’t chat together, 
            but if a user is both Skilled workers and customers, 
            then he can chat with anyone.

            Parmeters
                partner (obj) : another room member

            Returns
                Boolean
        """

        # when user or partner is customer and skilled both
        if (hasattr(self, 'customer') and hasattr(self, 'skilledworker')) or (hasattr(partner, 'customer') and hasattr(partner, 'skilledworker')):
            return True

        # when user is cutomer and partner is skilled worker
        elif hasattr(self, 'customer') and hasattr(partner, 'skilledworker'):
            return True

        # when user is skilled worker and partner is customer
        elif hasattr(self, 'skilledworker') and hasattr(partner, 'customer'):
            return True

        return False
