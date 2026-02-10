from django import shortcuts
from django import views
from django.contrib.auth import logout
from django.core import exceptions
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.db.models import functions
from django.http import HttpResponse

from apps.user.logic.facades import user as user_facades


class WellcomeView(views.View):
    template_name = 'wellcome.html'

    def get(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        return shortcuts.render(
            request=request,
            template_name=self.template_name,
        )

    def post(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        if request.user.is_authenticated:
            return shortcuts.redirect(to="care:services")
        return shortcuts.redirect(to="user:login")


class LoginView(views.View):
    template_name = 'login.html'

    def get(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        if request.user.is_authenticated:
            return shortcuts.redirect(to="care:services")
        return shortcuts.render(
            request=request,
            template_name=self.template_name,
        )

    def post(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        if request.user.is_authenticated:
            return shortcuts.redirect(to="care:services")
        try:
            user_facades.login(request=request, email=request.POST["email"], password=request.POST["password"])
        except exceptions.ValidationError as error:
            return shortcuts.render(
                request=request,
                template_name=self.template_name,
                context={
                    "error": error.message if hasattr(error, "message") else None,
                    "error_dict": error.error_dict if hasattr(error, "error_dict") else None,
                },
            )

        return shortcuts.redirect(to="care:services")


class RegisterView(views.View):
    template_name = 'register.html'

    def get(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        if request.user.is_authenticated:
            return shortcuts.redirect(to="care:services")
        return shortcuts.render(
            request=request,
            template_name=self.template_name,
        )

    def post(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        if request.user.is_authenticated:
            return shortcuts.redirect(to="care:services")
        try:
            user_facades.register(
                request=request,
                email=request.POST["email"],
                password=request.POST["password"],
                password_repeat=request.POST["password_repeat"],
                phone=request.POST["phone"],
                name=request.POST["name"],
            )
        except exceptions.ValidationError as error:
            print(error.__dict__)
            return shortcuts.render(
                request=request,
                template_name=self.template_name,
                context={
                    "error": error.message if hasattr(error, "message") else None,
                    "error_dict": error.error_dict if hasattr(error, "error_dict") else None,
                },
            )

        return shortcuts.redirect(to="care:services")


class UserView(views.View):
    template_name = 'user.html'

    def get(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        appointments = (
            request.user.appointments
            .annotate(
                appointment_datetime=models.ExpressionWrapper(
                    functions.Cast(
                        functions.Concat(
                            models.F("date"),
                            models.Value(" "),
                            models.F("time"),
                        ),
                        output_field=models.DateTimeField(),
                    ),
                    output_field=models.DateTimeField(),
                )
            )
            .annotate(
                is_past=models.Case(
                    models.When(appointment_datetime__lt=functions.Now(), then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                )
            )
        ).order_by("-appointment_datetime")
        return shortcuts.render(
            request=request,
            template_name=self.template_name,
            context={
                "user": request.user,
                "appointments": appointments,
            }
        )

    def post(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        appointments = (
            request.user.appointments
            .annotate(
                appointment_datetime=models.ExpressionWrapper(
                    functions.Cast(
                        functions.Concat(
                            models.F("date"),
                            models.Value(" "),
                            models.F("time"),
                        ),
                        output_field=models.DateTimeField(),
                    ),
                    output_field=models.DateTimeField(),
                )
            )
            .annotate(
                is_past=models.Case(
                    models.When(appointment_datetime__lt=functions.Now(), then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                )
            )
        ).order_by("-appointment_datetime")
        try:
            user = user_facades.update(
                user=request.user,
                email=request.POST["email"],
                phone=request.POST["phone"],
                name=request.POST["name"],
                passport=request.POST["passport"],
                policy=request.POST["policy"],
            )
        except exceptions.ValidationError as error:
            print(repr(request.user.policy), type(request.user.policy))
            return shortcuts.render(
                request=request,
                template_name=self.template_name,
                context={
                    "error": error.message if hasattr(error, "message") else None,
                    "error_dict": error.error_dict if hasattr(error, "error_dict") else None,
                    "user": request.user,
                    "appointments": appointments,
                },
            )
        return shortcuts.render(
            request=request,
            template_name=self.template_name,
            context={
                "user": user,
                "appointments": appointments,
            }
        )


class LogoutView(views.View):

    def post(self, request: WSGIRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        logout(request)
        return shortcuts.redirect("user:login")
