import pytest
from djmoney.money import Money
from mixer.backend.django import mixer

from customer.models import Customer
from user.models import User


@pytest.mark.django_db
class TestCustomer:
    def test_customer_string_representation(self, customer_obj):
        assert customer_obj.__str__() == customer_obj.user.__str__()

    def test_customer_string_representation_without_username(self):
        user_obj = User.objects.create(first_name="k", last_name="M")
        customer_obj = Customer.objects.create(user=user_obj)
        assert user_obj.__str__() in [user_obj.get_full_name(), user_obj.username, "GigUP User"]

    def test_customer_caching(self, customer_obj2):
        assert customer_obj2.balance.amount == 10

    def test_customer_cache_update(self, customer_obj):
        customer_obj.balance = Money(0, "USD")
        customer_obj.save()
        customer_obj.balance = Money(14, "USD")
        customer_obj.save()
        assert customer_obj.balance.amount == 14
