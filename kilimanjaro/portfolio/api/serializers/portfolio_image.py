from rest_framework import serializers

from portfolio.models import PortfolioImage


class PortfolioImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioImage
        fields = ["id", "picture"]

    def validate(self, attrs):

        """To check 'PortfolioImage' validity needs 'portfolio' instance but
        there is no 'portfolio' instance in attrs"""
        attrs["portfolio"] = self.context["request"].user.skilledworker.portfolio
        instance = self.instance

        if instance:
            full_attrs = {}  # 'instance' data will appends here

            if self.context["request"].method == "PATCH":

                """Updates data-dict with instance existing fields & field's value
                and previous value will update if new value inputs"""
                attrs = instance.__dict__ | attrs
                full_attrs = dict(attrs)

            elif self.context["request"].method == "PUT":
                fields = {"picture": None}

                """Updates data-dict and sets all the fields value as None, 
                and value will update if new value inputs"""
                full_attrs = fields | dict(attrs)

            instance.__dict__.update(**full_attrs)  # Updating instance value

        else:
            instance = PortfolioImage(**attrs)  # Checking model validation

        instance.full_clean()
        return attrs
