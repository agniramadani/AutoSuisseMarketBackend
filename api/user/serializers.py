from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Normalize the username to lowercase
        validated_data['username'] = validated_data['username'].lower()
        
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Check if the username is being updated, make it lowercase
        if 'username' in validated_data:
            validated_data['username'] = validated_data['username'].lower()
        # Check if the password is being updated, hash the password
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return super().update(instance, validated_data)

    def validate_username(self, value):
        if len(value) < 3:  # Minimum length requirement for username
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        return value

    def validate_password(self, value):
        if len(value) < 8:  # Minimum length requirement for password
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
