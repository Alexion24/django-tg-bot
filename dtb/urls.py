"""dtb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('tgadmin/', admin.site.urls),
    path('broadcast/', views.BroadcastMessageView.as_view(), name='broadcast'),
    path('__debug__/', include(debug_toolbar.urls)),

    path('', views.IndexView.as_view(), name='index'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('create/', views.CreateUserView.as_view(), name='create'),

    path('profile/webhook/', csrf_exempt(views.TelegramBotWebhookView.as_view())),
    path('webhooklist/', views.WebhookListView.as_view())
]
