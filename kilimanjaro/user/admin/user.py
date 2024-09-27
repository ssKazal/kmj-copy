from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats

from core.utils.general_func import admin_list_page_action
from country.models import Country
from customer.models import Customer
from occupation.models import Occupation
from skilled_worker.models import SkilledWorker
from user.models import AccountVerificationRequest, ResetPasswordRequest, User


class CustomUserCreationForm(UserCreationForm):
    """
    Represents user creation form.
    When create a user, also can manage skilled worker profile for this user
    ........

    Attributes
    ----------
    description : str
        description of skilled worker

    occupation : select
        occupation of skilled worker
    """

    # fields for skilled worker
    description = forms.CharField(required=False, widget=forms.Textarea)
    occupation = forms.ModelChoiceField(
        queryset=Occupation.objects.all(), required=False
    )

    class Meta(UserCreationForm):
        model = User
        fields = (
            "description",
            "occupation",
        )  # adding those fields with existing user fields

    def clean(self):
        occupation = self.cleaned_data.get("occupation")
        description = self.cleaned_data.get("description")

        errors_list = {}  # to contain error list

        # Either needs to insert both or needs to keep blank both since occupation and description are required for skilled worker profile
        if occupation and not description:
            errors_list.update({"description": "Add description"})
        elif description and not occupation:
            errors_list.update({"occupation": "Add occupation"})

        if errors_list:
            raise forms.ValidationError(errors_list)

        return self.cleaned_data  # since 'CustomUserCreation' form need cleaned data


class CustomUserChangeForm(UserChangeForm):
    """
    Represents user update form.
    When update a user, also can manage skilled worker profile for this user
    ........

    Attributes
    ----------
    description : str
        description of skilled worker

    occupation : select
        occupation of skilled worker
    """

    # fields for skilled worker
    description = forms.CharField(required=False, widget=forms.Textarea)
    occupation = forms.ModelChoiceField(
        queryset=Occupation.objects.all(), required=False
    )

    class Meta:
        model = User
        fields = ("description", "occupation")

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)

        # Initializing existing data to custom fields to show user update form
        user_obj = kwargs["instance"]
        skilled_worker_obj = SkilledWorker.objects.filter(user=user_obj).first()
        if skilled_worker_obj:
            self.fields["description"].initial = skilled_worker_obj.description
            self.fields["occupation"].initial = skilled_worker_obj.occupation

    def clean(self):
        occupation = self.cleaned_data.get("occupation")
        description = self.cleaned_data.get("description")

        errors_list = {}  # contains error list

        # Either needs to insert both or needs to keep blank both since occupation and description are required for skilled worker profile
        if occupation and not description:
            errors_list.update({"description": "Add description"})
        elif description and not occupation:
            errors_list.update({"occupation": "Add occupation"})

        if errors_list:
            raise forms.ValidationError(errors_list)

        return self.cleaned_data  # since 'CustomUserCreation' form need cleaned data


class UserResource(resources.ModelResource):
    """
    Represents of impoort-export resources.Like how resource can be imported or exported

    Adds description and occupation attribute for add new column to export file

    Methods
    ---------
    before_import(dataset, using_transactions, dry_run, **kwargs):
        Validates import data.

    before_save_instance(self, instance, using_transactions, dry_run):
        Modified imported instance before save it

    dehydrate_description(self, obj):
        Assigning value to export file's description column

    dehydrate_occupation(self, obj):
        Assigning value to export file's occupation column

    after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        After imported user data creates corresponding skilled worker and customer profile
    """

    description = fields.Field(column_name="description")
    occupation = fields.Field(column_name="occupation")
    set_unique_email = set()
    set_unique_phonenumber = set()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "password",
            "first_name",
            "last_name",
            "date_of_birth",
            "country",
            "city",
            "age_consent",
            "terms_and_condition",
            "is_email_verified",
            "is_phone_number_verified",
            "occupation",
            "description",
            "profile_picture",
        ]
        exclude = ("password",)
        export_order = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "country",
            "city",
            "age_consent",
            "terms_and_condition",
            "is_email_verified",
            "is_phone_number_verified",
            "occupation",
            "description",
        ]

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """Overriding from django-import-export for validate import data"""

        errors_list = []  # contains errors list
        line_number = 0  # row number of imported file

        self.set_unique_email = set()
        self.set_unique_phonenumber = set()

        # validation each row of data
        for row in dataset:

            # when not have profile picture, initializing default avatar for profile picture's
            profile_picture = row[15]
            if not profile_picture:
                profile_picture = "/profile-picture/common/avatar.png"

            country_obj = Country.objects.filter(id=row[6]).first()
            user = User(
                username=row[0],
                email=row[1],
                phone_number=row[2],
                first_name=row[3],
                last_name=row[4],
                date_of_birth=row[5],
                country=country_obj,
                city=row[7],
                age_consent=row[8],
                terms_and_condition=row[9],
                is_email_verified=row[10],
                is_phone_number_verified=row[11],
                password=row[14],
                profile_picture=profile_picture,
            )

            line_number += 1
            try:
                user.full_clean()  # checking user model validation
            except TypeError as e:
                errors_list.append(e)
            except ValidationError as e:

                # formating error messages for readable
                message_list = []
                for key, value in e.message_dict.items():
                    if key == "__all__":
                        message = value[0]
                    else:
                        message = {key: value}
                    message_list.append(message)
                errors_list.append(f"In line {line_number}: {message_list}")

            email = row[1]
            phone_number = row[2]
            is_email_verified = row[10]
            is_phone_number_verified = row[11]
            occupation = row[12]
            description = row[13]

            # when 'is_email_verified' is True but not provide any 'email'
            if int(is_email_verified) == 1 and not email:
                errors_list.append(
                    f"In line {line_number}: add 'email' before make it verified"
                )

            # when 'is_phone_number_verified' is True but not provide any 'phone_number'
            if int(is_phone_number_verified) == 1 and not phone_number:
                errors_list.append(
                    f"In line {line_number}: add 'phone_number' before make it verified"
                )

            # Checking 'email' address duplication in file
            if email:
                if email not in self.set_unique_email:
                    self.set_unique_email.add(email)
                else:
                    errors_list.append(
                        f"In line {line_number}: Email '{email}' has duplicated"
                    )

            # Checking 'phone_number' duplication in file
            if phone_number:
                if phone_number not in self.set_unique_phonenumber:
                    self.set_unique_phonenumber.add(phone_number)
                else:
                    errors_list.append(
                        f"In line {line_number}: Phone number'{phone_number}' has duplicated"
                    )

            # When provide occupation id doesn't exists
            if occupation and not Occupation.objects.filter(id=occupation).exists():
                errors_list.append(
                    f"In line {line_number}: 'Occupation' with this id does not exists."
                )

            # Either insert both or keep blank both of them
            if occupation and not description:
                errors_list.append(
                    f"In line {line_number}: 'description' field can not be blank"
                )
            if description and not occupation:
                errors_list.append(
                    f"In line {line_number}: 'occupation' field can not be blank"
                )

        if errors_list:
            raise Exception(errors_list)

        return ""

    def before_save_instance(self, instance, using_transactions, dry_run):
        """Modified imported instance before save it"""

        # when not have profile picture initialize default avatar for profile picture
        if not instance.profile_picture:
            instance.profile_picture = "/profile-picture/common/avatar.png"

        # convert plain-text password to hash
        instance.password = make_password(instance.password)

    def dehydrate_description(self, obj):
        """Assigning value to export file's description column"""

        skilled_worker_obj = SkilledWorker.objects.filter(user=obj).first()
        if skilled_worker_obj:
            return skilled_worker_obj.description
        return ""

    def dehydrate_occupation(self, obj):
        """Assigning value to export file's occupation column"""

        skilled_worker_obj = SkilledWorker.objects.filter(user=obj).first()
        if skilled_worker_obj and skilled_worker_obj.occupation:
            return skilled_worker_obj.occupation.name
        return ""

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        """After imported user data create corresponding skilled worker and customer profile"""

        if dry_run is False:

            # skill worker creation
            descriptions = dataset.__getitem__(
                "description"
            )  # initializing description from file data set
            occupations = dataset.__getitem__(
                "occupation"
            )  # initializing occupation from file data set
            occupation_qs = Occupation.objects.all()

            user_ids = [ids.object_id for ids in result]
            users = User.objects.filter(id__in=user_ids)

            customer_profile = []  # customer profile's list
            skilled_worker_profile = []  # skilled workder profile's list

            for i, user_obj in enumerate(users):

                # customer creation, since update is not applicable
                cs_obj = Customer(user=user_obj)
                customer_profile.append(cs_obj)

                description = descriptions[i]
                occupation = occupations[i]

                # skilled worker creation, since update is not applicable
                if occupation:
                    occupation_obj = occupation_qs.filter(id=occupation).first()

                    if (
                        description and occupation_obj
                    ):  # only those user has skilled worker profile which provide occupation and description
                        sk_obj = SkilledWorker(
                            user=user_obj,
                            description=description,
                            occupation=occupation_obj,
                        )  # creating skilled worker instance
                        skilled_worker_profile.append(sk_obj)

            # bulk creation 'customer' and 'skilled worker'
            SkilledWorker.objects.bulk_create(skilled_worker_profile)
            Customer.objects.bulk_create(customer_profile)


class UserActivityFilterWithCustomTemplate(admin.SimpleListFilter):
    """
    Filtering user list by user active status

    ...

    Methods
    --------
    lookups(self, request, model_admin):
        Returns filter params

    queryset(self, request, queryset):
        Return filtered queryset by params
    """

    title = "Active"  # label
    parameter_name = "is_active"  # param
    template = "admin/user_activity_custom_filter.html"

    def lookups(self, request, model_admin):
        """Returns filter params"""

        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        """Returns filtered queryset by params"""

        if self.value() == "yes":
            return queryset.filter(is_active=True)
        if self.value() == "no":
            return queryset.filter(is_active=False)
        if self.value() in ["yes,no", "no,yes"]:
            return queryset.all()


class UserStatusFilterWithCustomTemplate(admin.SimpleListFilter):
    """
    Filtering user list by user staff status, superuser status, basic user status

    ...

    Methods
    --------
    lookups(self, request, model_admin):
        Returns filter params

    queryset(self, request, queryset):
        Return filtered queryset by params
    """

    title = "Type of user"  # label
    parameter_name = "user_type"  # param
    template = "admin/user_type_custom_filter.html"

    def lookups(self, request, model_admin):
        """Returns filter params"""

        return (
            ("staff", "Staff"),
            ("super", "Super user"),
            ("basic", "Basic user"),
        )

    def queryset(self, request, queryset):
        """Returns filtered queryset by params"""

        if self.value() == "staff":
            return queryset.filter(is_staff=True)
        if self.value() == "super":
            return queryset.filter(is_superuser=True)
        if self.value() == "basic":
            return queryset.filter(is_staff=False, is_superuser=False)


class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    """
    Represents django admin

    ...

    Methods
    --------
    get_list_display(self, request):
        Overrides list display to Adding custom action button to user list item

    _customer_profile_link(self, instance):
        shows customer profile link inside user detail view

    _skilledworker_profile_link(self, instance):
        shows skilled worker profile link inside user detail view

    _customer_balance(self, instance):
        shows customer balance to user edit page

    _skilled_worker_balance(self, instance):
        shows skilled worker balance to user edit page

    _skilled_worker_experience(self, instance):
        shows skilled worker experience to user edit page

    get_export_formats(self):
        overriding export format

    get_import_formats(self):
        overriding import format

    save_model(self, request, obj, form, change)
        Overriding django admin default save method
    """

    model = User
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    readonly_fields = [
        "_customer_profile_link",
        "_skilledworker_profile_link",
        "_customer_balance",
        "_skilled_worker_balance",
        "_skilled_worker_experience",
    ]

    list_display = [
        "id",
        "uuid",
        "username",
        "email",
        "first_name",
        "last_name",
        "date_of_birth",
        "phone_number",
        "country",
        "city",
        "age_consent",
        "terms_and_condition",
        "is_email_verified",
        "is_phone_number_verified",
        "is_active",
        "email_subscription",
    ]
    search_fields = [
        "email",
        "date_of_birth",
        "phone_number",
        "city",
        "age_consent",
        "country__name",
        "first_name",
        "last_name",
    ]
    autocomplete_fields = [
        "country",
    ]
    list_filter = (
        "is_email_verified",
        "is_phone_number_verified",
        UserStatusFilterWithCustomTemplate,
        UserActivityFilterWithCustomTemplate,
    )
    list_display_links = ["id", "uuid"]

    resource_class = UserResource

    def get_list_display(self, request):
        """Adds custom action button to user list item"""

        default_list_display = super(CustomUserAdmin, self).get_list_display(request)

        # Custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm("user.change_user"),
                        "path": f"/user/user/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm("user.delete_user"),
                        "path": f"/user/user/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm("user.delete_user") or request.user.has_perm(
            "user.change_user"
        ):
            default_list_display = default_list_display + [action]

        return default_list_display

    def _customer_profile_link(self, instance):
        """shows customer profile link inside user detail view"""
        customer_obj = instance.customer if hasattr(instance, "customer") else None
        if customer_obj:
            return format_html(
                '<a href={} target="blank">Link</a>'.format(
                    reverse(
                        "admin:%s_%s_change" % ("customer", "customer"),
                        args=(customer_obj.id,),
                    )
                )
            )
        return "-"

    def _skilledworker_profile_link(self, instance):
        """shows skilled worker profile link inside user detail view"""

        skilled_worker_obj = (
            instance.skilledworker if hasattr(instance, "skilledworker") else None
        )
        if skilled_worker_obj:
            return format_html(
                '<a href={} target="blank">Link</a>'.format(
                    reverse(
                        "admin:%s_%s_change" % ("skilled_worker", "skilledworker"),
                        args=(skilled_worker_obj.id,),
                    )
                )
            )
        return "-"

    def _customer_balance(self, instance):
        """showing customer balance to user edit page"""

        customer_obj = instance.skilledworker if hasattr(instance, "customer") else None
        if customer_obj and customer_obj.balance:
            return f"{customer_obj.balance.amount} {customer_obj.balance.currency}"
        return "-"

    def _skilled_worker_balance(self, instance):
        """showing skilled worker balance to user edit page"""

        skilled_worker_obj = (
            instance.skilledworker if hasattr(instance, "skilledworker") else None
        )
        if skilled_worker_obj and skilled_worker_obj.balance:
            return f"{skilled_worker_obj.balance.amount} {skilled_worker_obj.balance.currency}"
        return "-"

    def _skilled_worker_experience(self, instance):
        """show skilled worker experience to user edit page"""

        skilled_worker_obj = (
            instance.skilledworker if hasattr(instance, "skilledworker") else None
        )
        if skilled_worker_obj and skilled_worker_obj.experience:
            return skilled_worker_obj.experience
        return "-"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "phone_number",
                    "password",
                )
            },
        ),
        (
            ("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "date_of_birth",
                    "country",
                    "city",
                    "profile_picture",
                    "age_consent",
                )
            },
        ),
        (
            ("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "user_permissions")},
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
        (("Groups"), {"fields": ("groups",)}),
        (
            ("Skilled Worker Profile"),
            {
                "fields": (
                    "description",
                    "occupation",
                    "_skilled_worker_balance",
                    "_skilled_worker_experience",
                    "_skilledworker_profile_link",
                )
            },
        ),
        (
            ("Customer Profile"),
            {"fields": ("_customer_balance", "_customer_profile_link")},
        ),
        (
            ("Others"),
            {
                "fields": (
                    "terms_and_condition",
                    "is_email_verified",
                    "is_phone_number_verified",
                )
            },
        ),
    )

    add_fieldsets = (
        (None, {"fields": ("email", "phone_number", "password1", "password2")}),
        (
            ("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "date_of_birth",
                    "country",
                    "city",
                    "profile_picture",
                    "age_consent",
                )
            },
        ),
        (
            ("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "user_permissions")},
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
        (("Groups"), {"fields": ("groups",)}),
        (("Skilled Worker Profile"), {"fields": ("description", "occupation")}),
        (
            ("Others"),
            {
                "fields": (
                    "terms_and_condition",
                    "is_email_verified",
                    "is_phone_number_verified",
                )
            },
        ),
    )

    def get_export_formats(self):
        """overriding export format"""

        # Format options that showing in django admin export page
        formats = (
            base_formats.CSV,
            base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]

    def get_import_formats(self):
        """overriding import format"""

        # Format options that showing in django admin import page
        formats = (
            base_formats.CSV,
            base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]

    def save_model(self, request, obj, form, change):
        """Overriding django admin default save method"""

        super().save_model(request, obj, form, change)

        description = request.POST.get("description")
        occupation = request.POST.get("occupation")

        Customer.objects.get_or_create(user=obj)  # customer profile creation

        # skilled worker creation and update
        if (
            description and occupation
        ):  # for creating or updating skilled worker 'description' and 'occupation' are required
            skilled_worker_obj = SkilledWorker.objects.filter(user=obj).first()
            occupation_obj = Occupation.objects.filter(id=occupation).first()

            # when skilled worker object already exists for this user have to update this object
            if skilled_worker_obj:
                skilled_worker_obj.description = description
                skilled_worker_obj.occupation = occupation_obj
                skilled_worker_obj.save()

            # when user not have skilled worker object have to create
            else:
                skilled_worker_obj = SkilledWorker.objects.create(
                    user=obj, description=description, occupation=occupation_obj
                )

        return obj


admin.site.register(User, CustomUserAdmin)


class AccountVerificationRequestAdmin(admin.ModelAdmin):
    """
    Represents AccountVerificationRequest admin

    Methods
    --------
    get_list_display(self, request):
        Adds custom action button to verification request list item
    """

    model = AccountVerificationRequest

    readonly_fields = ["uuid", "token"]
    list_display = ["id", "uuid", "verify_by", "user", "token", "is_used"]
    list_filter = [
        "is_used",
    ]
    search_fields = [
        "verify_by",
        "token",
        "user__first_name",
        "user__last_name",
    ]
    autocomplete_fields = [
        "user",
    ]

    def get_list_display(self, request):
        """Adding custom action button to verification request list item"""

        default_list_display = super(
            AccountVerificationRequestAdmin, self
        ).get_list_display(request)

        # Custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm(
                            "user.change_accountverificationrequest"
                        ),
                        "path": f"/user/accountverificationrequest/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "user.delete_accountverificationrequest"
                        ),
                        "path": f"/user/accountverificationrequest/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "user.delete_accountverificationrequest"
        ) or request.user.has_perm("user.change_accountverificationrequest"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(AccountVerificationRequest, AccountVerificationRequestAdmin)


class ResetPasswordRequestAdmin(admin.ModelAdmin):
    """
    Represents ResetPasswordRequest admin

    Methods
    --------
    get_list_display(self, request):
        Overrides list display to Adding custom action button to user list item
    """

    model = ResetPasswordRequest

    readonly_fields = [
        "uuid",
    ]
    list_display = ["id", "uuid", "requested_with", "token", "user", "is_used"]
    search_fields = ["requested_with", "token"]
    list_filter = ["is_used"]
    autocomplete_fields = [
        "user",
    ]

    def get_list_display(self, request):
        """Overrides list display to Adding custom action button to user list item"""

        default_list_display = super(ResetPasswordRequestAdmin, self).get_list_display(
            request
        )

        # Custom action button's for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm(
                            "user.change_resetpasswordrequest"
                        ),
                        "path": f"/user/resetpasswordrequest/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm(
                            "user.delete_resetpasswordrequest"
                        ),
                        "path": f"/user/resetpasswordrequest/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm(
            "user.delete_resetpasswordrequest"
        ) or request.user.has_perm("user.change_resetpasswordrequest"):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(ResetPasswordRequest, ResetPasswordRequestAdmin)
admin.autodiscover()
admin.site.login_template = "admin/login.html"
