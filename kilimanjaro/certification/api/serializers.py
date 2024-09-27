from rest_framework import serializers

from certification.models import Certification


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = [
            "id",
            "certification_name",
            "description",
            "date_earned",
            "certification_issued",
        ]

    def validate(self, attrs):

        """To check 'certification' validity needs 'skilled worker' instance but
        there is no 'skilled worker' instance in attrs"""
        attrs["skilled_worker"] = self.context["request"].user.skilledworker

        if self.context["request"].method == "PATCH":
            instance = self.instance
            instance_oreder_dict = (
                instance.__dict__
            )  # 'certification' instance OrderDict(user's data as dict)
            attrs = instance_oreder_dict | attrs  # Updating 'instance' OrderDict value

            certification_object_fields = (
                "certification_name",
                "description",
                "date_earned",
                "certification_issued",
                "skilled_worker",
            )

            for key in dict(attrs):
                # Removes unnecessary fields
                if key not in certification_object_fields:
                    attrs.pop(key, None)

        instance = Certification(**attrs)
        instance.full_clean()  # Checks model validation

        return attrs
