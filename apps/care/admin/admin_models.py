from django.contrib import admin
from django.utils import safestring

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
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "name",
                    "icon_preview",
                    "icon",
                    "background",
                    "color",
                )
            }
        ),
    )
    readonly_fields = (
        "icon_preview",
    )

    @admin.display(description="предпросмотр")
    def icon_preview(self, obj: care_models.Category):
        return safestring.mark_safe(f"""
        <div 
        class="d-flex justify-content-center align-items-center align-content-center"
        style="width: 48px;height: 48px;color: {obj.color or '#ced4da'};background: {obj.background or '#6c757d'};padding: 4px;border-radius: 6px;">
        <i class="{obj.icon}" style="font-size: 32px;"></i>
        </div>        
        """)

    icon_preview.allow_tags = True


@admin.register(care_models.Service)
class ServiceAdmin(abstract_admin.AbstractAdmin):
    pass


@admin.register(care_models.Appointment)
class AppointmentAdmin(abstract_admin.AbstractAdmin):
    pass
