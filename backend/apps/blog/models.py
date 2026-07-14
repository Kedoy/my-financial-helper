from django.db import models
from apps.accounts.models import User


class Post(models.Model):
    """
    Модель поста (заметки) в мини-блоге.
    Пользователи могут публиковать заметки о финансовой грамотности.
    """
    VISIBILITY_CHOICES = [
        ('public', 'Публичный'),
        ('private', 'Приватный'),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержимое')
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='public',
        verbose_name='Видимость'
    )
    image = models.ImageField(
        upload_to='posts/images/',
        null=True,
        blank=True,
        verbose_name='Изображение'
    )
    likes = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]

    def __str__(self):
        return f'Пост {self.title} от {self.author.email}'


class PostLike(models.Model):
    """
    Модель лайка поста.
    Пользователь может лайкнуть пост только один раз.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='user_likes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='liked_posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_likes'
        verbose_name = 'Лайк поста'
        verbose_name_plural = 'Лайки постов'
        unique_together = ['post', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f'Лайк от {self.user.email} к посту {self.post.title}'


class Comment(models.Model):
    """
    Модель комментария к посту.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'post_comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий от {self.author.email} к посту {self.post.title}'
