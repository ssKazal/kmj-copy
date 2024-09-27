from rest_framework import serializers

from certification.models import Certification
from portfolio.models import Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ["id", "education", "certification", "description"]

    def get_fields(self, *args, **kwargs):
        """While updating 'Portfolio' returns only that "skilled worker" Certification objects"""

        fields = super().get_fields(*args, **kwargs)  # Portfolio serializer fields
        request = self.context.get("request", None)
        view = self.context.get("view", None)
        if request and view:
            fields["certification"].queryset = Certification.objects.filter(
                skilled_worker=self.context["request"].user.skilledworker
            )
        return fields

    def validate(self, attrs):

        instance = self.instance
        if instance:
            full_attrs = {}  # 'instance' data will appends here

            if self.context["request"].method == "PATCH":

                """Updates data-dict with instance existing fields & field's value
                and previous value will update if new value inputs"""
                full_attrs = {
                    **self.to_internal_value(self.__class__(self.instance).data),
                    **attrs,
                }

            elif self.context["request"].method == "PUT":

                fields = {
                    "education": None,
                    "certification": None,
                    "description": None,
                }

                """Updates data-dict and sets all the fields value as None, 
                and value will update if new value inputs"""
                full_attrs = fields | dict(attrs)

            instance.__dict__.update(**full_attrs)
            instance.full_clean()  # Checking model validation

        return attrs
