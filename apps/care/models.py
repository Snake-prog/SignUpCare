from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

from abstractions import abstract_model
from apps.user import models as user_models


class Specialist(abstract_model.AbstractBaseModel):
    class Meta:
        verbose_name = "специалист"
        verbose_name_plural = "специалисты"
        default_related_name = "specialists"

    name = models.CharField(
        verbose_name=_("name"),
        help_text=_("name"),
        max_length=150,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class SpecialistReview(abstract_model.AbstractBaseModel):
    class Meta:
        verbose_name = "отзыв на специалиста"
        verbose_name_plural = "отзывы на специалистов"
        default_related_name = "reviews"

    name = models.CharField(
        verbose_name="автор оценки",
        help_text="автор оценки",
        max_length=150,
    )
    date = models.DateField(
        verbose_name=_("date"),
        help_text=_("date"),
        null=True,
        blank=True,
    )
    score = models.PositiveIntegerField(
        verbose_name="оценка",
        help_text="оценка",
        validators=[validators.MaxValueValidator(5)],
        default=0,
    )
    comment = models.TextField(
        verbose_name="комментарий",
        help_text="комментарий",
        null=True,
        blank=True,
    )
    specialist = models.ForeignKey(
        to=Specialist,
        related_name="reviews",
        verbose_name="специалист",
        help_text="специалист",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class SpecialistAchievement(abstract_model.AbstractBaseModel):
    class Meta:
        verbose_name = "достижение специалиста"
        verbose_name_plural = "достижения специалистов"
        default_related_name = "achievements"

    name = models.CharField(
        verbose_name="автор оценки",
        help_text="автор оценки",
        max_length=150,
    )
    date = models.DateField(
        verbose_name=_("date"),
        help_text=_("date"),
        null=True,
        blank=True,
    )
    score = models.PositiveIntegerField(
        verbose_name="оценка",
        help_text="оценка",
        validators=[validators.MaxValueValidator(5)],
        default=0,
    )
    comment = models.TextField(
        verbose_name="комментарий",
        help_text="комментарий",
        null=True,
        blank=True,
    )
    specialist = models.ForeignKey(
        to=Specialist,
        related_name="achievements",
        verbose_name="специалист",
        help_text="специалист",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Category(abstract_model.AbstractBaseModel):
    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        default_related_name = "categories"

    name = models.CharField(
        verbose_name="название",
        help_text="название",
        max_length=150,
    )
    icon = models.CharField(
        verbose_name="иконка",
        help_text="https://fontawesome.com/icons",
        max_length=150,
        null=True,
        blank=True,
    )
    background = models.CharField(
        verbose_name="фон",
        help_text="фон",
        max_length=9,
        null=True,
        blank=True,
    )
    color = models.CharField(
        verbose_name="цвет",
        help_text="цвет",
        max_length=9,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Service(abstract_model.AbstractBaseModel):
    class Meta:
        verbose_name = "сервис"
        verbose_name_plural = "сервисы"
        default_related_name = "services"

    name = models.CharField(
        verbose_name="название",
        help_text="название",
        max_length=150,
    )
    price = models.PositiveIntegerField(
        verbose_name="цена",
        help_text="цена",
        default=0,
    )
    is_documents_required = models.BooleanField(
        verbose_name="необходимость документов",
        help_text="необходимость документов",
        default=False,
    )
    specialists = models.ManyToManyField(
        verbose_name="специалисты",
        help_text="специалисты",
        to=Specialist,
        related_name="services",
    )
    category = models.ForeignKey(
        to=Category,
        related_name="services",
        verbose_name="категория",
        help_text="категория",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Appointment(abstract_model.AbstractBaseModel):
    class Meta:
        verbose_name = "прием"
        verbose_name_plural = "прием"
        default_related_name = "appointments"

    date = models.DateField(
        verbose_name=_("date"),
        help_text=_("date"),
    )
    time = models.TimeField(
        verbose_name=_("time"),
        help_text=_("time"),
    )
    specialist = models.ForeignKey(
        verbose_name="специалист",
        help_text="специалист",
        to=Specialist,
        related_name="appointments",
        on_delete=models.CASCADE,
    )
    service = models.ForeignKey(
        verbose_name="сервис",
        help_text="сервис",
        to=Service,
        related_name="appointments",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        to=user_models.User,
        related_name="appointments",
        on_delete=models.CASCADE,
        verbose_name="пользователь",
        help_text="пользователь",
    )

    def __str__(self):
        return f"{self.user} - {self.service}"

    def __repr__(self):
        return self.__str__()