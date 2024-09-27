import pytest
from mixer.backend.django import mixer

from certification.api.serializers import CertificationSerializer
from certification.models import Certification
from core.utils.general_func import request_factory


@pytest.mark.django_db
class TestCertification:

    endpoint = "/certifications/"

    def test_certification_partial_update(
        self, certification_obj, api_client, auth_headers
    ):
        endpoint = f"{self.endpoint}{certification_obj.id}/"
        data = {
            "description": "more update related certification",
            "date_earned": "2020-03-15",
        }
        response = api_client.patch(
            endpoint, data=data, format="json", HTTP_AUTHORIZATION=auth_headers
        )

        assert response.status_code == 200

    def test_certification_representation_string(self, certification_obj):
        assert certification_obj.__str__() == "New Certificate"
