from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from apps.blog.models import Post, PostLike, Comment
from apps.blog.serializers import (
    PostSerializer,
    PostCreateUpdateSerializer,
    CommentSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления постами.
    - list: Список постов (публичные + свои приватные)
    - create: Создать пост
    - retrieve: Получить пост
    - update: Обновить пост
    - destroy: Удалить пост
    - like: Лайкнуть пост
    - unlike: Убрать лайк
    - comments: Комментарии к посту
    """
    queryset = Post.objects.all().select_related('author__profile')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['visibility']
    ordering_fields = ['created_at', 'likes']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostSerializer

    def get_queryset(self):
        """
        Возвращаем публичные посты + приватные посты текущего пользователя.
        """
        user = self.request.user
        queryset = Post.objects.filter(
            Q(visibility='public') | Q(author=user)
        ).select_related('author__profile').prefetch_related('user_likes')

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Лайкнуть пост."""
        post = self.get_object()
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)

        if created:
            post.likes += 1
            post.save()
            return Response({'status': 'liked', 'likes': post.likes})
        return Response({'status': 'already_liked', 'likes': post.likes})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlike(self, request, pk=None):
        """Убрать лайк с поста."""
        post = self.get_object()
        deleted, _ = PostLike.objects.filter(post=post, user=request.user).delete()

        if deleted:
            post.likes = max(0, post.likes - 1)
            post.save()
            return Response({'status': 'unliked', 'likes': post.likes})
        return Response({'status': 'not_liked', 'likes': post.likes})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        """Получить комментарии к посту."""
        post = self.get_object()
        comments = post.comments.select_related('author__profile').order_by('created_at')
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_comment(self, request, pk=None):
        """Добавить комментарий к посту."""
        post = self.get_object()
        serializer = CommentSerializer(data=request.data, context={'request': request, 'post': post})

        if serializer.is_valid():
            comment = serializer.save(post=post)
            return Response(CommentSerializer(comment, context={'request': request}).data,
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления комментариями.
    """
    queryset = Comment.objects.all().select_related('author__profile')
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
