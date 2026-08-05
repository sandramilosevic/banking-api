from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer

# Get the active User model configured for this project (could be a custom model)
User = get_user_model()


class CreateUserSerializer(UserCreateSerializer):
    """Serializer used to handle new user registration, extending Djoser's
    default create serializer with extra custom fields."""

    class Meta(UserCreateSerializer.Meta):
        # Inherit default Meta settings from Djoser (e.g. password write-only, validators)
        model = User  # Model this serializer is based on
        fields = [
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "id_no",
            "security_question",
            "security_answer",
        ]  # Fields exposed/accepted through the API

    def create(self, validated_data):
        # Create a new user instance; create_user() properly hashes the password
        user = User.objects.create_user(**validated_data)
        return user
