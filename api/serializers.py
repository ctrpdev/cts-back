from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'email']

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        user = CustomUser(**validated_data)
        user.set_unusable_password()
        user.save()
        return user
