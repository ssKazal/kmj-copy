from rest_framework import serializers

from user.models import User


class UserSkilledWorkerProfileSerializer(serializers.ModelSerializer):
    country_name = serializers.SerializerMethodField()
    occupation_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    user_phone_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "occupation_name",
            "date_of_birth",
            "user_email",
            "user_phone_number",
            "country_name",
            "city",
            "profile_picture",
            "age_consent",
        )

    def get_country_name(self, obj):
        if obj.country_name:
            return obj.country_name
        return None

    def get_user_email(self, obj):
        if obj.email:
            return obj.email
        return None

    def get_user_phone_number(self, obj):
        if obj.phone_number:
            return obj.phone_number.raw_input
        return None

    def get_occupation_name(self, obj):
        if obj.occupation_name:
            return obj.occupation_name
        return None
