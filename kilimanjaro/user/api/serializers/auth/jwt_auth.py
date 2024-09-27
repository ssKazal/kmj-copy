from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customises JWT response"""

    def validate(self, attrs):
        data = super().validate(attrs)  # Data dict
        jwt_token = self.get_token(self.user)
        data["refresh"] = str(jwt_token)  # Adding refresh token
        data["access"] = str(jwt_token.access_token)  # Adding access token

        is_account_verified = False
        if self.user.is_email_verified or self.user.is_phone_number_verified:
            is_account_verified = True

        data[
            "is_account_verified"
        ] = is_account_verified  # Adding user verification status

        return data
