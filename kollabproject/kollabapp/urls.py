

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('chatui/', views.chatui, name='home'),
    path('', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
# from django.urls import path
# from .views import SignUpView, AuthLoginView
# from django.contrib.auth.views import LogoutView

# urlpatterns = [
#     path('signup/', SignUpView.as_view(), name='signup'),
#     path('login/', AuthLoginView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(), name='logout'),
# ]

