from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    nickname = models.CharField(max_length=40, verbose_name="Никнейм")
    avatar = models.ImageField(
        upload_to="avatars/",
        verbose_name="Аватар",
        null=True,
        blank=True,
    )
    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.nickname
