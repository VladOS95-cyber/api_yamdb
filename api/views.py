import random

from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import models
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import (filters, generics, mixins, permissions,
                            serializers, status, viewsets)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import TitleFilter
from .models import Category, Comment, CustomUser, Genre, Review, Title
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrStaffOrReadOnly, IsOwnerOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetOTPSerializer,
                          MyTokenObtainPairSerializer, ReviewSerializer,
                          TitleSerializer, UserSerializer)


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
    permission_classes = [IsAuthenticated, IsAdmin]
    http_method_names = ('get', 'post', 'patch', 'delete',)
    lookup_field = 'username'


class UserViewMe(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        current_user = get_object_or_404(
            CustomUser, username=request.user.username
        )
        serializer = UserSerializer(current_user)
        return Response(serializer.data)

    def patch(self, request):
        current_user = get_object_or_404(
            CustomUser, username=request.user.username
        )
        serializer = UserSerializer(
            current_user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteViewSet(mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    pass


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsAdminOrReadOnly]
        else:
            self.permission_classes = [AllowAny]
        return [permission() for permission in self.permission_classes]


class GenreViewSet(DeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'slug')
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsAdminOrReadOnly]
        else:
            self.permission_classes = [AllowAny]
        return [permission() for permission in self.permission_classes]


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrReadOnly)
    filterset_class = TitleFilter

    def get_queryset(self):
        return Title.objects.select_related(
            'category'
        ).prefetch_related(
            'genre'
        ).all().annotate(
            rating=Avg('reviews__score', output_field=models.DecimalField())
        ).order_by('pk')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly
    )

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        if Review.objects.filter(title=title,
                                 author=self.request.user
                                 ).exists():
            raise serializers.ValidationError('Можно оставить только 1')
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(review=review, author=self.request.user)
