from django.conf import settings
from django.contrib import admin
from django.db.models import F

from core.utils.general_func import admin_list_page_action
from customer.models import Customer


class CustomerAdmin(admin.ModelAdmin):
    """
    Represents Customer admin

    Methods
    --------
    get_list_display(self, request):
        Overriding list display

    get_queryset(self, request):
        Overrides get_queryset method for showing customer's user data to list display

    """

    model = Customer

    readonly_fields = [
        "uuid",
    ]
    list_display = [
        "id",
        "uuid",
        "get_username",
        "get_email",
        "get_first_name",
        "get_last_name",
        "get_date_of_birth",
        "get_phone_number",
        "get_country",
        "get_city",
        "get_age_consent",
        "_balance",
        "get_terms_and_condition",
        "get_is_email_verified",
        "get_is_phone_number_verified",
        "get_is_active",
        "get_email_subscription",
    ]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__phone_number",
        "user__email",
        "balance",
    ]
    autocomplete_fields = [
        "user",
    ]

    class Media:
        js = [
            settings.STATIC_URL + "js/customer_currency.js",
        ]

    def get_queryset(self, request):
        """
        Overrides get_queryset method for showing customer's user data to list display

        Return
        -------
        Customer queryset with some annotated value
        """
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            username=F("user__username"),
            email=F("user__email"),
            first_name=F("user__first_name"),
            last_name=F("user__last_name"),
            date_of_birth=F("user__date_of_birth"),
            phone_number=F("user__phone_number"),
            country=F("user__country__name"),
            city=F("user__city"),
            age_consent=F("user__age_consent"),
            terms_and_condition=F("user__terms_and_condition"),
            is_email_verified=F("user__is_email_verified"),
            is_phone_number_verified=F("user__is_phone_number_verified"),
            is_active=F("user__is_active"),
            email_subscription=F("user__email_subscription"),
        )
        return queryset

    @admin.display(description="Balance", ordering="balance_currency")
    def _balance(self, obj):
        """For better balance representation in list display"""

        if obj.balance:
            return f"{obj.balance.amount} {obj.balance.currency}"
        return "-"

    @admin.display(description="Username", ordering="username")
    def get_username(self, obj):
        """showing user's username to list display"""
        return obj.username

    @admin.display(description="Email Address", ordering="email")
    def get_email(self, obj):
        """
        showing user's email to list display
        """
        return obj.email

    @admin.display(description="First Name", ordering="first_name")
    def get_first_name(self, obj):
        """showing user's first name to list display"""
        return obj.first_name

    @admin.display(description="Last Name", ordering="last_name")
    def get_last_name(self, obj):
        """showing user's last_name to list display"""
        return obj.last_name

    @admin.display(description="Date of birth", ordering="date_of_birth")
    def get_date_of_birth(self, obj):
        """showing user's date_of_birth to list display"""

        return obj.date_of_birth

    @admin.display(description="Phone Number", ordering="phone_number")
    def get_phone_number(self, obj):
        """showing user's phone_number to list display"""
        return obj.phone_number

    @admin.display(description="Country", ordering="country")
    def get_country(self, obj):
        """showing user's country to list display"""
        return obj.country

    @admin.display(description="City", ordering="city")
    def get_city(self, obj):
        """showing user's city to list display"""
        return obj.city

    @admin.display(description="Age Consent", ordering="age_consent")
    def get_age_consent(self, obj):
        """showing user's age_consent to list display"""
        return obj.age_consent

    @admin.display(description="Terms And Condition", ordering="terms_and_condition")
    def get_terms_and_condition(self, obj):
        """showing user's terms_and_condition to list display"""
        return obj.terms_and_condition

    @admin.display(description="Is Email Verified", ordering="is_email_verified")
    def get_is_email_verified(self, obj):
        """showing user's is_email_verified to list display"""
        return obj.is_email_verified

    @admin.display(
        description="Is Phone Number Verified", ordering="is_phone_number_verified"
    )
    def get_is_phone_number_verified(self, obj):
        """showing user's is_phone_number_verified to list display"""
        return obj.is_phone_number_verified

    @admin.display(description="Is Active", ordering="is_active")
    def get_is_active(self, obj):
        """showing user's is_active to list display"""
        return obj.is_active

    @admin.display(description="Email Subscription", ordering="email_subscription")
    def get_email_subscription(self, obj):
        """showing user's email_subscription to list display"""
        return obj.email_subscription

    def get_list_display(self, request):
        """Overriding list display"""

        default_list_display = super(CustomerAdmin, self).get_list_display(request)

        # custom action buttons for list page
        def action(obj):
            return admin_list_page_action(
                [
                    {
                        "button_name": "Edit",
                        "has_perm": request.user.has_perm("customer.change_customer"),
                        "path": f"/customer/customer/{obj.id}/change",
                        "background_color": "#040cf9b8",
                    },
                    {
                        "button_name": "Delete",
                        "has_perm": request.user.has_perm("customer.delete_customer"),
                        "path": f"/customer/customer/{obj.id}/delete",
                        "background_color": "#ff3737bf",
                    },
                ]
            )

        # user's permission check for button access
        if request.user.has_perm("customer.delete_customer") or request.user.has_perm(
            "customer.change_customer"
        ):
            default_list_display = default_list_display + [action]

        return default_list_display


admin.site.register(Customer, CustomerAdmin)
