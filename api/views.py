from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets, generics, status, mixins
from .permissions import IsOwnerOrReadOnly, IsAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CommentSerializer, ReviewSerializer, CategorySerializer, GenreSerializer, TitleSerializer, MyTokenObtainPairSerializer, UserSerializer, GetOTPSerializer
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


class CategoryViewSet(DeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )


class GenreViewSet(DeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'slug')
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
    )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('title_id'))
        return review.comments.all()


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
