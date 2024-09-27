from rest_framework import serializers

from favorite.models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ["id", "skilled_worker"]

    def validate(self, attrs):

        """To check 'favorite' validity needs 'customer' instance but
        there is no 'customer' instance in attrs"""
        attrs["customer"] = self.context["request"].user.customer
        instance = self.instance

        if instance:
            if self.context["request"].method == "PUT":
                instance.skilled_worker = attrs.get("skilled_worker", None)
            elif self.context["request"].method == "PATCH":
                instance.skilled_worker = attrs.get(
                    "skilled_worker", instance.skilled_worker
                )  # Keeps existing value unless new value inputted
        else:  # While creating
            instance = Favorite(**attrs)

        instance.full_clean()  # Checks model validation
        return attrs
