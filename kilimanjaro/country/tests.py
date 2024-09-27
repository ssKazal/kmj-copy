import pytest
from mixer.backend.django import mixer

from country.models import Country


@pytest.mark.django_db
class TestCountry:
    def test_country_string_representation(self, country_obj):
        assert country_obj.__str__() == "Germany"
