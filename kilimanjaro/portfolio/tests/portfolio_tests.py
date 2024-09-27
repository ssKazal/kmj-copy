from django.core.cache import cache
from django.core.exceptions import ValidationError

from core.utils.general_func import request_factory
from portfolio.api.serializers import PortfolioSerializer
from portfolio.models import Portfolio


class TestPortfolio:
    endpoint = "/portfolios/"

    def test_portfolio_model_clean_method(self, skilled_worker_obj, certification_obj1):
        data = {
            "skilled_worker": skilled_worker_obj,
            "education": "HSC",
            "certification": certification_obj1,
            "description": "dummy Desc",
        }

        portfolio_obj = Portfolio(**data)

        try:
            portfolio_obj.full_clean()
            portfolio_obj.save()
        except ValidationError as e:
            assert (
                e.messages[0] == "This Certification obj doesn't belong to this user."
            )

    def test_portfolio_list_from_cache(self, api_client, auth_headers):
        response = api_client.get(self.endpoint, HTTP_AUTHORIZATION=auth_headers)
        assert response.status_code == 200

    def test_portfolio_list_from_db(self, api_client, auth_headers):
        cache.clear()
        response = api_client.get(self.endpoint, HTTP_AUTHORIZATION=auth_headers)
        assert response.status_code == 200

    def test_portfolio_update(
        self, api_client, auth_headers, skilled_worker_obj, certification_obj
    ):
        endpoint = f"{self.endpoint}{skilled_worker_obj.portfolio.id}/"

        data = {
            "skilled_worker": skilled_worker_obj.id,
            "education": "HSC",
            "certification": certification_obj.id,
            "description": "dummy Desc",
        }

        response = api_client.put(
            endpoint, data=data, format="json", HTTP_AUTHORIZATION=auth_headers
        )
        assert response.status_code == 200

    def test_portfolio_partial_update(
        self, api_client, auth_headers, skilled_worker_obj
    ):
        endpoint = f"{self.endpoint}{skilled_worker_obj.portfolio.id}/"

        data = {"education": "SSC", "description": "dummy Desc"}

        response = api_client.patch(
            endpoint, data=data, format="json", HTTP_AUTHORIZATION=auth_headers
        )
        assert response.status_code == 200

    def test_portfolio_representation_string(self, skilled_worker_obj):
        assert skilled_worker_obj.__str__() in [
            skilled_worker_obj.user.get_full_name(), 
            skilled_worker_obj.user.username, "GigUP User"
            ]
