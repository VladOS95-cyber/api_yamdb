from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Category, Genre, Title, CustomUser, Review, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'year', 'genre', 'category', 'description')
        model = Title


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'first_name', 'last_name', 'username', 'bio', 'email', 'role',
        ]
        model = CustomUser


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )
    title = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='id'
    )
    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'author', 'title', 'text', 'created')
        model = Comment
        read_only_fields = ('title', )
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = CustomUser.objects.create(**validated_data)
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = CustomUser.USERNAME_FIELD 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False

    def validate(self, attrs):
        attrs['password'] = self.context['request'].data.get('confirmation_code')
        return super().validate(attrs)


class GetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
