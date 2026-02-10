from django.contrib.auth.decorators import login_required
from django.urls import path

from apps.user.gui import views as user_views

app_name = 'user'
urlpatterns = [
    path('', user_views.WellcomeView.as_view(), name='wellcome'),
    path('login/', user_views.LoginView.as_view(), name='login'),
    path('register/', user_views.RegisterView.as_view(), name='register'),
    path('user/', login_required(user_views.UserView.as_view()), name='user'),
    path('logout/', login_required(user_views.LogoutView.as_view()), name='logout'),
]
