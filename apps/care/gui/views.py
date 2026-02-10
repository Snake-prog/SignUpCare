from django import shortcuts
from django import views
from django.core import exceptions
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.http import HttpResponse

from apps.care import models as care_models
from apps.care.logic.facades import appointment as appointment_facades


class ServicesView(views.View):
    template_name = 'services.html'

    def get(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        category = request.GET.get("category", None)
        services = care_models.Service.objects.all()
        if category:
            services = services.filter(category_id=category)
        return shortcuts.render(
            request=request,
            template_name=self.template_name,
            context={
                "categories": care_models.Category.objects.all(),
                "services": services,
                "category_filtered": int(category) if category else None,
            }
        )


class ServiceView(views.View):
    template_name = 'service.html'

    def get(self, request: WSGIRequest, pk: int, *args: tuple, **kwargs: dict) -> HttpResponse:
        service = shortcuts.get_object_or_404(care_models.Service, pk=pk)

        specialists = (
            service.specialists
            .annotate(avg_score=models.Avg("reviews__score"))
        )
        return shortcuts.render(
            request=request,
            template_name=self.template_name,
            context={
                "service": service,
                "specialists": specialists,
            }
        )

    def post(self, request: WSGIRequest, pk: int, *args: tuple, **kwargs: dict) -> HttpResponse:
        service = shortcuts.get_object_or_404(care_models.Service, pk=pk)
        try:
            appointment_facades.create(
                user=request.user,
                service=service,
                date=request.POST["date"],
                time=request.POST["time"],
                specialist_id=request.POST["specialist_id"],
            )
        except exceptions.ValidationError as error:
            specialists = (
                service.specialists
                .annotate(avg_score=models.Avg("reviews__score"))
            )
            return shortcuts.render(
                request=request,
                template_name=self.template_name,
                context={
                    "error": error.message if hasattr(error, "message") else None,
                    "error_dict": error.error_dict if hasattr(error, "error_dict") else None,
                    "specialist_id": request.POST["specialist_id"],
                    "service": service,
                    "specialists": specialists,
                },
            )
        return shortcuts.redirect(to="user:user")


class AppointmentDeleteView(views.View):

    def post(self, request: WSGIRequest, pk: int, *args: tuple, **kwargs: dict) -> HttpResponse:
        appointment = shortcuts.get_object_or_404(care_models.Appointment, pk=pk)
        if appointment.user == request.user:
            appointment.delete()
        return shortcuts.redirect(to="user:user")
