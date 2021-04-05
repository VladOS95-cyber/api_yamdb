from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    GetOTPApiView, MyTokenObtainPairView, ReviewViewSet,
                    TitleViewSet, UserViewSet)

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='Users')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')

urlpatterns = [
    path(
        'v1/auth/token/',
        MyTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'v1/auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('v1/api-token-auth/', views.obtain_auth_token),
    path('auth/email/', GetOTPApiView.as_view()),
    path('v1/', include(router_v1.urls)),
]
