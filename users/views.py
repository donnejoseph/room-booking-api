from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .serializers import (
    UserSerializer, 
    RegisterSerializer, 
    ChangePasswordSerializer,
)
from typing import Any, Dict

User = get_user_model()


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for authenticated users to view and update their profile.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self) -> User:
        """
        Return the authenticated user.
        """
        return self.request.user


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class ChangePasswordView(generics.UpdateAPIView):
    """
    API endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self) -> User:
        """
        Return the authenticated user.
        """
        return self.request.user
        
    def update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Update the user's password.
        """
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            old_password = serializer.validated_data.get('old_password')
            if not user.check_password(old_password):
                return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)
                
            # Set new password
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            
            return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
