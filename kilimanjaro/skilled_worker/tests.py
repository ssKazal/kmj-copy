import json

import pytest
from djmoney.money import Money

from skilled_worker.api.serializers import UserSkilledWorkerProfileSerializer
from skilled_worker.models import SkilledWorker
from user.models import User


@pytest.mark.django_db
class TestSkilledWorker:

    endpoint = "/skilledworkers/"

    def test_skilled_worker_with_country(
        self, api_client, user_obj, skilled_worker_obj
    ):
        endpoint = f"{self.endpoint}{user_obj.id}/"
        response = api_client.get(endpoint)
        assert response.data["country_name"] == "Germany"

    def test_specific_skilled_worker_without_country(
        self, api_client, user_obj1, skilled_worker_obj1
    ):
        endpoint = f"{self.endpoint}{user_obj1.id}/"
        response = api_client.get(endpoint)
        assert response.data["country_name"] == None

    def test_skilled_worker_with_email(self, api_client, user_obj, skilled_worker_obj):
        endpoint = f"{self.endpoint}{user_obj.id}/"
        response = api_client.get(endpoint)
        assert response.data["user_email"] == "josephgreene@example.net"

    def test_specific_skilled_worker_without_email(
        self, api_client, user_obj4, skilled_worker_obj4
    ):
        endpoint = f"{self.endpoint}{user_obj4.id}/"
        response = api_client.get(endpoint)
        assert response.data["user_email"] == None

    def test_skilled_worker_with_phone_number(
        self, api_client, user_obj, skilled_worker_obj
    ):
        endpoint = f"{self.endpoint}{user_obj.id}/"
        response = api_client.get(endpoint)
        assert response.data["user_phone_number"] == "+8801789929182"

    def test_specific_skilled_worker_without_phone_number(
        self, api_client, user_obj1, skilled_worker_obj1
    ):
        endpoint = f"{self.endpoint}{user_obj1.id}/"
        response = api_client.get(endpoint)
        assert response.data["user_phone_number"] == None

    def test_skilled_worker_with_occupation(
        self, api_client, user_obj, skilled_worker_obj
    ):
        endpoint = f"{self.endpoint}{user_obj.id}/"
        response = api_client.get(endpoint)
        assert response.data["occupation_name"] == "Cleaner2"

    def test_specific_skilled_worker_without_occupation(
        self, api_client, user_obj4, skilled_worker_obj4
    ):
        endpoint = f"{self.endpoint}{user_obj4.id}/"
        response = api_client.get(endpoint)
        assert response.data["occupation_name"] == None

    def test_skilledworker_bulk_create(self, occupation_obj):
        skilled_worker_profile = []
        user_obj = User.objects.create(
            email="teste@gmail.com",
            username="user123",
            first_name="k",
            last_name="M",
            is_email_verified=True,
        )

        sk_obj = SkilledWorker(
            user=user_obj,
            description="description",
            occupation=occupation_obj,
        )
        skilled_worker_profile.append(sk_obj)

        skilled_worker_obj_list = SkilledWorker.objects.bulk_create(
            skilled_worker_profile
        )

        for sk in skilled_worker_obj_list:
            assert sk.user.username == "user123"

    def test_skilledworker_filter(self, api_client, skilled_worker_obj, occupation_obj):
        endpoint = f"{self.endpoint}?country=&city__icontains=&occupation=Cleaner"
        response = api_client.get(endpoint)
        assert response.status_code == 200

    def test_skilledworker_portfolio_for_non_loggedin_user(
        self,
        api_client,
        user_obj5,
        skilled_worker_obj3,
        portfolio_obj2,
        portfolio_image_obj2,
    ):
        endpoint = f"{self.endpoint}{user_obj5.id}/portfolio/"
        response = api_client.get(endpoint)
        assert response.status_code == 200

    def test_skilledworker_certification_for_non_loggedin_user(
        self, api_client, user_obj5, skilled_worker_obj3, certification_obj2
    ):
        endpoint = f"{self.endpoint}{user_obj5.id}/certifications/"
        response = api_client.get(endpoint)
        assert response.status_code == 200

    def test_customer_caching(self, skilled_worker_obj4):
        assert skilled_worker_obj4.balance.amount == 10

    def test_skilledworker_cache_update(self, skilled_worker_obj):
        skilled_worker_obj.balance = Money(0, "USD")
        skilled_worker_obj.save()
        skilled_worker_obj.balance = Money(20, "USD")
        skilled_worker_obj.save()
        assert skilled_worker_obj.balance.amount == 20

    def test_skilledworker_string_representation(self, skilled_worker_obj):
        assert skilled_worker_obj.__str__() in [
            skilled_worker_obj.user.get_full_name(), 
            skilled_worker_obj.user.username, "GigUP User"]
