from django.contrib import admin

from abstractions import abstract_admin
from apps.care import models as care_models


@admin.register(care_models.Specialist)
class SpecialistAdmin(abstract_admin.AbstractAdmin):
    pass


@admin.register(care_models.SpecialistReview)
class SpecialistReviewAdmin(abstract_admin.AbstractAdmin):
    pass


@admin.register(care_models.SpecialistAchievement)
class SpecialistAchievementAdmin(abstract_admin.AbstractAdmin):
    pass


@admin.register(care_models.Category)
class CategoryAdmin(abstract_admin.AbstractAdmin):
    pass


@admin.register(care_models.Service)
class ServiceAdmin(abstract_admin.AbstractAdmin):
    pass


@admin.register(care_models.Appointment)
class AppointmentAdmin(abstract_admin.AbstractAdmin):
    pass
