from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    # new fields for profile form
    display_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=225, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.username




class Workspace(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=225, blank=True, null=True)
    image = models.ImageField(upload_to="workspace_pics/", blank=True, null=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_workspaces"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("title", "admin")  

    def __str__(self):
        return self.title  
    

class WorkspaceMembership(models.Model):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("member", "Member"),
    )

    workspace = models.ForeignKey("Workspace", on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspace_memberships")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("workspace", "user")  # prevents duplicate memberships

    def __str__(self):
        return f"{self.user.username} in {self.workspace.title} ({self.role})"
    

