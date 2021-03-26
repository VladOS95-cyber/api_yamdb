from .serializers import MyTokenObtainPairSerializer, UserSerializer, GetOTPSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import random
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import CustomUser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.core.mail import send_mail
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password


PERMISSION_CLASSES = [IsAuthenticatedOrReadOnly, ]


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = PERMISSION_CLASSES
    lookup_field = 'username'


class GetOTPApiView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = random.randint(1111, 9999)
        email = serializer.validated_data['email']
        send_mail(
            'Регистрация на Yamdb!',
            f'Ваш код регистрации - {code}',
            'from@example.com',
            [email]
        )
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'password': make_password(str(code))
            }
        )
        if not created:
            user.password = make_password(str(code))
            user.save()
        return Response({'message': 'Check your email for verification code!'})
