from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserCreateSerializer, LoginSerializer
from .models import User
from rest_framework.permissions import AllowAny


class RegisterView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        content_text ={
            "message": "User created successfully",
            "status": status.HTTP_201_CREATED,
            "data": serializer.data
        }
        return Response(content_text)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        content_text = {
            "message": "Login successful",
            "data": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "token": str(refresh.access_token),
            "status": status.HTTP_200_OK
        }

        return Response(content_text)
            


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  
        except Exception:
            return Response({"error": "Invalid token"}, status=400)

        return Response({"message": "Logout successful"}, status=200)
