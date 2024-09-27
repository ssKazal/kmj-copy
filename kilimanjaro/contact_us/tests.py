import pytest
from django.core.exceptions import ValidationError

from contact_us.models import ContactUs
from core.utils.general_func import base64_to_file
from chat.tests.test_gn_data import GREATHER_THAN_5_MB_FILE


@pytest.mark.django_db
class TestContactUs:
    def test_contact_us_model_clean_method(self, user_obj):
        data = {
            "title": "Title",
            "message": "New message",
            "attachment": base64_to_file(GREATHER_THAN_5_MB_FILE),
            "user": user_obj,
        }

        contact_us_obj = ContactUs(**data)

        try:
            contact_us_obj.full_clean()
            contact_us_obj.save()
        except ValidationError as e:
            assert e.messages[0] == "File size should not exceed 5MB."

    def test_contact_us_string_representation(self, contact_us_obj):
        assert contact_us_obj.__str__() == "Contact us title"
