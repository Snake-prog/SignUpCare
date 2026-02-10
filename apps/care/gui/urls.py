from django.contrib.auth.decorators import login_required
from django.urls import path

from apps.care.gui import views as care_views

app_name = 'care'
urlpatterns = [
    path('services/', login_required(care_views.ServicesView.as_view()), name='services'),
    path('services/<int:pk>/', login_required(care_views.ServiceView.as_view()), name='service'),
    path('appointment/delete/<int:pk>/', login_required(care_views.AppointmentDeleteView.as_view()), name='appointment-delete'),
]
