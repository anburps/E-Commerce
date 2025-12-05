from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import User
from accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            content_text = {
                "message": "Only superusers can register new users."
            }
            return Response(content_text, status=status.HTTP_403_FORBIDDEN)
        else:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Registration successful",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
            }
        }, status=status.HTTP_200_OK)


# GET – Profile
class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)

        return Response({
            "message": "Profile retrieved successfully",
            "user": serializer.data,
        },
        status=status.HTTP_200_OK
        )
# PATCH – Update Profile
class ProfileUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# LIST – (superuser only) list all users
class UserListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        serializer = ProfileSerializer(self.get_queryset(), many=True)

        if serializer.is_valid():
            return Response({
                "message": "Users retrieved successfully",
                "users": serializer.data,
            },
            status=status.HTTP_200_OK
            )
        
        else:
            return Response({
                "message": "Users could not be retrieved",
            },
            status=status.HTTP_400_BAD_REQUEST
            )