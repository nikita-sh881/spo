from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from .serializers import UserSerializer, RegisterSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = authenticate(username=request.data.get('username'), 
                               password=request.data.get('password'))
            if user:
                response.data['user'] = UserSerializer(user).data
        return response