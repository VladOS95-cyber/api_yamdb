from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, filters, generics
from .permissions import IsOwnerOrReadOnly
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CommentSerializer, ReviewSerializer, CategorySerializer, GenreSerializer, TitleViewSerializer, MyTokenObtainPairSerializer, UserSerializer, GetOTPSerializer
from .models import Category, Genre, Title, Review, CustomUser
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework.views import APIView
import random
from rest_framework_simplejwt.views import TokenObtainPairView


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


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'


class UserViewMe(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, )

    def retrieve(self, request, *args, **kwargs):
        return Response(UserSerializer(instance=request.user).data)

    def update(self, request, *args, **kwargs):
        if request.data.get('role'):
            request.data.pop('role')
        serializer = UserSerializer(request.user, data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleViewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()
