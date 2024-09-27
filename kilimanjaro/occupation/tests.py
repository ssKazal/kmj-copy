import pytest
from django.core.exceptions import ValidationError

from occupation.models import Occupation


@pytest.mark.django_db
class TestOccupation:
    def test_occupation_model_clean_method(self, occupation_obj):
        data = {
            "name": "Cleaner2",
        }
        occupation_obj = Occupation(**data)
        try:
            occupation_obj.full_clean()
            occupation_obj.save()
        except ValidationError as e:
            assert e.messages[0] == "Occupation with this Name already exists."

    def test_occupation_representation_string(self, occupation_obj):
        assert occupation_obj.__str__() == "Cleaner2"
