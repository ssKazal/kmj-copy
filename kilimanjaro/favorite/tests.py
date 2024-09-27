import pytest

from core.utils.general_func import request_factory
from favorite.api.serializers import FavoriteSerializer
from favorite.models import Favorite


@pytest.mark.django_db
class TestFavorite:
    endpoint = "/favorites/"

    def test_favorite_update(
        self, api_client, auth_headers, favorite_obj, skilled_worker_obj2
    ):
        data = {"skilled_worker": skilled_worker_obj2.id}
        response = api_client.put(
            f"{self.endpoint}{favorite_obj.id}/", data, HTTP_AUTHORIZATION=auth_headers
        )
        assert response.status_code == 200

    def test_favorite_partial_update(
        self, api_client, auth_headers, favorite_obj, skilled_worker_obj2
    ):
        data = {"skilled_worker": skilled_worker_obj2.id}
        response = api_client.patch(
            f"{self.endpoint}{favorite_obj.id}/", data, HTTP_AUTHORIZATION=auth_headers
        )
        assert response.status_code == 200

    def test_favorite_representation_string(self, favorite_obj):
        assert favorite_obj.__str__() == str(favorite_obj.id)
