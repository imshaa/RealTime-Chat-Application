
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    # path('chatui/', views.chatui, name='chatui'),
    path("chatui/<int:workspace_id>/", views.chatui, name="chatui"),
    path('', views.home, name='home'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('signup/', views.signup_view, name='signup'),
    path('workspace/', views.workspace, name='workspace'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('workspace/join/', views.join_workspace_manual, name='join_workspace_manual'),
    path('workspace/<int:workspace_id>/add-member/', views.add_member_manual, name='add_member_manual'),
    path("workspace/<int:workspace_id>/remove-member/", views.remove_member, name="remove_member"),
    path("workspace/<int:workspace_id>/delete/", views.delete_workspace, name="delete_workspace"),
] 
