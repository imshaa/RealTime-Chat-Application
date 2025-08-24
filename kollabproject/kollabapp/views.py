
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .models import Workspace
from .models import WorkspaceMembership
from django.db import models
User = get_user_model()  # This gets CustomUser


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        if CustomUser.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already exists"})

        if CustomUser.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email already exists"})

        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect("login")

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("profile")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


# Logout view
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile(request):
    user = request.user  

    # Check if profile is already created
    profile_created = bool(user.display_name and user.description and user.profile_picture)

    # Handle profile creation form
    if not profile_created and request.method == "POST":
        display_name = request.POST.get("displayName", "").strip()
        description = request.POST.get("description", "").strip()
        profile_picture = request.FILES.get("fileUpload")

        if not display_name or not description or not profile_picture:
            messages.error(request, "All fields are required.")
            return render(request, "profile.html", {
                "user": user,
                "profile_saved": False,
                "workspaces": [],
            })

        # Save user profile
        user.display_name = display_name
        user.description = description
        user.profile_picture = profile_picture
        user.save()

        messages.success(request, "Profile successfully saved. Now you can Create/Join Workspaces")
        profile_created = True

    # Fetch all workspaces the user is part of
    memberships = WorkspaceMembership.objects.filter(user=user).select_related("workspace")
    workspaces = [m.workspace for m in memberships]

    return render(request, "profile.html", {
        "user": user,
        "profile_saved": profile_created,
        "workspaces": workspaces,   # 👈 pass workspaces to template
    })



@login_required
def update_profile(request):
    user = request.user  

    if request.method == "POST":
        display_name = request.POST.get("displayName", "").strip()
        description = request.POST.get("description", "").strip()
        profile_picture = request.FILES.get("fileUpload")

        if not display_name or not description:
            messages.error(request, "Display name and description are required.")
            return redirect("profile")  # fallback

        # Update user profile
        user.display_name = display_name
        user.description = description
        if profile_picture:
            user.profile_picture = profile_picture
        user.save()

        #  redirect to a workspace (like join_workspace_manual does)
        workspace = Workspace.objects.filter(memberships__user=user).first()
        if workspace:
            return redirect("chatui", workspace_id=workspace.id)
        else:
            return redirect("profile")  # if user has no workspace, go to profile

    return redirect("profile")


def home(request):
    return render(request, 'home.html')



# To check Workspace Admin.
def is_workspace_admin(user, workspace):
    return WorkspaceMembership.objects.filter(workspace=workspace, user=user, role="admin").exists()


@login_required
def chatui(request, workspace_id):
    # Get workspace by ID (only if the user is a member)
    membership = WorkspaceMembership.objects.filter(
        user=request.user, workspace_id=workspace_id
    ).first()

    if not membership:
        messages.error(request, "You are not part of this workspace.")
        return redirect("profile")

    workspace = membership.workspace
    members = WorkspaceMembership.objects.filter(workspace=workspace).select_related("user")

    return render(request, "chatui.html", {
        "workspace": workspace,
        "members": members,
    })

@login_required
def workspace(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        image = request.FILES.get("fileUpload")

        #  Validation checks
        if not title and not image:
            messages.error(request, "Workspace title and image are required.")
            return render(request, "workspace.html")
        elif not title:
            messages.error(request, "Workspace title is required.")
            return render(request, "workspace.html")
        elif not image:
            messages.error(request, "Workspace image is required.")
            return render(request, "workspace.html")

        #  Restrict: max 2 workspaces as admin
        if Workspace.objects.filter(admin=request.user).count() >= 2:
            messages.error(request, "You can only be admin of 2 workspaces.")
            return redirect("profile")

        #  Create or update workspace
        workspace, created = Workspace.objects.get_or_create(
            title=title,
            admin=request.user,
            defaults={"description": description, "image": image},
        )

        if not created:
            # 🔄 Update existing workspace instead of creating duplicate
            workspace.description = description
            if image:
                workspace.image.delete(save=False)  # remove old image
                workspace.image = image
            workspace.save()
            messages.success(request, f"Workspace '{title}' updated successfully!")
        else:
            # 👑 Add admin membership if new
            WorkspaceMembership.objects.create(
                workspace=workspace, user=request.user, role="admin"
            )
            messages.success(request, f"Workspace '{title}' created successfully!")

        return redirect("chatui", workspace_id=workspace.id)

    return render(request, "workspace.html")

# Joining members to a workspace
@login_required
def join_workspace_manual(request):
    if request.method == "POST":
        #  Check limit: user can only belong to 2 workspaces (admin OR member)
        total_memberships = WorkspaceMembership.objects.filter(user=request.user).count()
        if total_memberships >= 2:
            messages.error(request, "You can only join up to 2 workspaces total.")
            return redirect("profile")

        admin_email = request.POST.get("admin_email")
        title = request.POST.get("title")

        try:
            admin = CustomUser.objects.get(email=admin_email)
            workspace = Workspace.objects.get(title=title, admin=admin)
        except (CustomUser.DoesNotExist, Workspace.DoesNotExist):
            messages.error(request, "Workspace not found.")
            return redirect("profile")

        #  Always join as member (admin can upgrade later if needed)
        membership, created = WorkspaceMembership.objects.get_or_create(
            workspace=workspace,
            user=request.user,
            defaults={"role": "member"}
        )

        if created:
            messages.success(request, f"Joined workspace {workspace.title} as Member!")
        else:
            messages.info(request, f"You are already a member of {workspace.title}.")

        #  Redirect to correct chatui (needs workspace_id)
        return redirect("chatui", workspace_id=workspace.id)
    
# adding members to workspace
@login_required
def add_member_manual(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)

    # Only admins can add members
    if not is_workspace_admin(request.user, workspace):
        messages.error(request, "Only admins can add members.")
        return redirect("chatui", workspace_id=workspace.id)

    if request.method == "POST":
        identifier = request.POST.get("identifier")  # username or email
        role = request.POST.get("role", "member")   # default to member

        try:
            user = CustomUser.objects.get(
                models.Q(username=identifier) | models.Q(email=identifier)
            )
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found. Ask them to signup first.")
            return redirect("chatui", workspace_id=workspace.id)

        #  Check if user is already part of 2 or more workspaces
        existing_memberships = WorkspaceMembership.objects.filter(user=user).count()
        if existing_memberships >= 2:
            messages.error(request, f"{user.username} is already part of 2 workspaces and cannot be added.")
            return redirect("chatui", workspace_id=workspace.id)

        # Add the user if they are eligible
        WorkspaceMembership.objects.get_or_create(
            workspace=workspace, user=user, defaults={"role": role}
        )
        messages.success(request, f"{user.username} added to workspace as {role}!")
        return redirect("chatui", workspace_id=workspace.id)

    # Default redirect (in case of GET request or fallback)
    return redirect("chatui", workspace_id=workspace.id)


#  Remove a user from workspace (admin only)
@login_required
def remove_member(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)

    # Only admins can remove members
    if not is_workspace_admin(request.user, workspace):
        messages.error(request, "Only admins can remove members.")
        return redirect("chatui", workspace_id=workspace.id)

    if request.method == "POST":
        username = request.POST.get("username")

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("chatui", workspace_id=workspace.id)

        # Prevent removing admin (yourself or other admins)
        membership = WorkspaceMembership.objects.filter(workspace=workspace, user=user).first()
        if not membership:
            messages.error(request, f"{username} is not in this workspace.")
        elif membership.role == "admin":
            messages.error(request, "Admins cannot be removed from workspace.")
        else:
            membership.delete()
            messages.success(request, f"{username} has been removed from {workspace.title}.")

        return redirect("chatui", workspace_id=workspace.id)

    return redirect("chatui", workspace_id=workspace.id)


# Delete workspace (admin only)
@login_required
def delete_workspace(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)

    # Only workspace admin can delete
    if workspace.admin != request.user:
        messages.error(request, "Only the workspace admin can delete this workspace.")
        return redirect("chatui", workspace_id=workspace.id)

    if request.method == "POST":
        confirm_title = request.POST.get("title")
        if confirm_title != workspace.title:
            messages.error(request, "Workspace title does not match. Cannot delete.")
            return redirect("chatui", workspace_id=workspace.id)

        workspace.delete()
        messages.success(request, f"Workspace '{confirm_title}' deleted successfully!")
        return redirect("profile")  # back to profile after deletion

    return redirect("chatui", workspace_id=workspace.id)
