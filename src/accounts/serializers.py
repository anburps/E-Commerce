from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from app.models import Vendor, UserVendorRole

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        exclude = ['user']


class RegisterSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(write_only=True)
    role = serializers.ChoiceField(
        choices=[choice[0] for choice in UserVendorRole.ROLE_CHOICES],
        write_only=True
    )
    vendors = VendorSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'vendor',
            'vendors',
            'role',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        vendor_data = validated_data.pop('vendor')
        role = validated_data.pop('role')

        user = User.objects.create_user(**validated_data)

        vendor = Vendor.objects.create(user=user, **vendor_data)

        UserVendorRole.objects.create(user=user, vendor=vendor, role=role)

        return user





class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'email', 'date_joined']
