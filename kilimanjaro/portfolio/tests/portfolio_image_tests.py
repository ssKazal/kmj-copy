import pytest
from django.core.exceptions import ValidationError

from core.utils.general_data import MAX_PORTFOLIO_IMAGE_NUMBER
from core.utils.general_func import file_object, request_factory
from portfolio.api.serializers import PortfolioImageSerializer
from portfolio.models import PortfolioImage


@pytest.mark.django_db
class TestPortfolioImage:
    endpoint = "/portfolios/portfolio-image/"

    def test_Portfolio_image_model_clean_method(
        self, skilled_worker_obj, certification_obj, portfolio_obj
    ):

        for i in range(MAX_PORTFOLIO_IMAGE_NUMBER):
            PortfolioImage.objects.create(
                picture=file_object(name="abcdg.png"), portfolio=portfolio_obj
            )

        portfolio_img_data = {
            "portfolio": portfolio_obj,
            "picture": file_object(name="abcdg.png"),
        }
        portfolio_img_obj = PortfolioImage(**portfolio_img_data)

        try:
            portfolio_img_obj.full_clean()
            portfolio_img_obj.save()
        except ValidationError as e:
            assert (
                e.messages[0]
                == f"Up to {MAX_PORTFOLIO_IMAGE_NUMBER} pictures can be added to one portfolio."
            )

    def test_portfolio_image_update(
        self, api_client, auth_headers, portfolio_image_obj
    ):
        data = {"picture": file_object(name="abcfde.png")}
        response = api_client.put(
            f"{self.endpoint}{portfolio_image_obj.id}/",
            data=data,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_portfolio_image_partial_update(
        self, api_client, auth_headers, portfolio_image_obj
    ):
        data = {}
        response = api_client.patch(
            f"{self.endpoint}{portfolio_image_obj.id}/",
            data=data,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_portfolio_image_string_representation(self, portfolio_image_obj):
        assert portfolio_image_obj.__str__() == str(portfolio_image_obj.id)
