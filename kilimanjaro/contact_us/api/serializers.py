from rest_framework import serializers

from contact_us.models import ContactUs


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ["id", "title", "message", "attachment"]

    def validate(self, attrs):

        """To check 'contact us' validity needs 'user' instance but
        there is no 'user' instance in attrs"""
        attrs["user"] = self.context["request"].user
        instance = ContactUs(**attrs)
        instance.full_clean()  # Checks model validation
        return attrs
