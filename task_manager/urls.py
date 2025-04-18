from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from tasks.views import RegisterView, VerifyCodeView, LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyCodeView.as_view(), name='verify_code'),

    path('', include('tasks.urls')),
]
