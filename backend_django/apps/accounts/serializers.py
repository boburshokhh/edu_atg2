from __future__ import annotations

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=1, max_length=50)
    password = serializers.CharField(min_length=1, max_length=128)


class RefreshSerializer(serializers.Serializer):
    refreshToken = serializers.CharField(min_length=10)


class LogoutSerializer(serializers.Serializer):
    refreshToken = serializers.CharField(min_length=10)


class ProfileUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    company = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    position = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    language = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email_notifications = serializers.BooleanField(required=False)
    push_notifications = serializers.BooleanField(required=False)
    weekly_report = serializers.BooleanField(required=False)
    avatar_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class RegisterProfileSerializer(serializers.Serializer):
    """Serializer for first-time user registration (required fields)"""
    full_name = serializers.CharField(min_length=2, max_length=255, required=True)
    phone = serializers.CharField(min_length=5, max_length=50, required=True)
    station_id = serializers.IntegerField(required=False, allow_null=True)  # Station ID from database (optional)
    position = serializers.CharField(min_length=2, max_length=255, required=True)  # Job title
    department = serializers.CharField(required=False, allow_blank=True, max_length=255)  # Department (stored in bio)






