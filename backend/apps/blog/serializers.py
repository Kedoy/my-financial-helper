from rest_framework import serializers
from apps.blog.models import Post, PostLike, Comment
from apps.accounts.models import User


class UserMinimalSerializer(serializers.ModelSerializer):
    """Минимальная информация о пользователе для отображения в постах."""
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar_url']

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return request.build_absolute_uri(obj.profile.avatar.url) if request else obj.profile.avatar.url
        return None


class CommentSerializer(serializers.ModelSerializer):
    """Serializer для комментариев."""
    author = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'post', 'author', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Автор берется из контекста (request.user)
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    """Serializer для постов."""
    author = UserMinimalSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, source='author.id')
    image_url = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_id', 'title', 'content', 'visibility',
            'image', 'image_url', 'likes', 'comments_count', 'is_liked',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'likes', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return PostLike.objects.filter(post=obj, user=request.user).exists()
        return False


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer для создания и обновления постов."""

    class Meta:
        model = Post
        fields = ['title', 'content', 'visibility', 'image']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
