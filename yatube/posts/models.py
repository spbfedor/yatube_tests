from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models

User = get_user_model()


class Group(
    models.Model
):
    title = models.CharField(
        max_length=200
    )
    slug = models.SlugField(
        max_length=200,
        unique=True
    )
    description = models.TextField()

    def __str__(
        self
    ):
        return self.title


class Post(
    models.Model
):
    text = models.TextField(
        validators=[
            MinLengthValidator(
                limit_value=15,
                message="Длина этого поля должна быть не менее 15 символов"
            )
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts'
    )

    class Meta:
        ordering = [
            '-pub_date'
        ]

    def __str__(
        self
    ):
        return self.text
