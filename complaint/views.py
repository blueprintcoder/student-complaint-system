from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Complaint
import re
from django.contrib import messages
import json
from .models import Feedback
from django.contrib.auth import update_session_auth_hash



def register(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("password")
        pass2 = request.POST.get("confirm_password")

        if not uname:
            messages.error(request, "Username cannot be empty")
            return render(request, "register.html")

        if pass1 != pass2:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")

        if len(pass1) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, "register.html")

        if not re.search(r"[A-Z]", pass1):
            messages.error(request, "Password must contain at least one uppercase letter")
            return render(request, "register.html")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pass1):
            messages.error(request, "Password must contain at least one symbol")
            return render(request, "register.html")

        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already exists")
            return render(request, "register.html")

        User.objects.create_user(
            username=uname,
            email=email,
            password=pass1
        )

        messages.success(request, "Registration successful!")
        return redirect("signin")

    return render(request, "register.html")

def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        pass1 = request.POST.get("password")
        
        user = authenticate(request, username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            return redirect("complaintreg")
        
        else:
            messages.error(request, "❌ Incorrect username or password")

    return render(request, "signin.html")

@login_required
def complaintreg(request):

    # 🔥 Department → Classes Mapping
    dept_classes = {
        "Computer Science": ["FY MCA", "SY MCA", "TY MCA", "FY BCA", "SY BCA", "TY BCA"],
        "Engineering": ["FE", "SE", "TE", "BE"],
        "Management": ["FY MBA", "SY MBA"],
        "Commerce": ["FY BCom", "SY BCom", "TY BCom"],
        "Arts": ["FY BA", "SY BA", "TY BA"]
    }

    # 🔥 Categories (Enhanced)
    categories = [
        "Academic Issue",
        "Faculty Complaint",
        "Exam Issue",
        "Infrastructure",
        "Hostel Problem",
        "Library Issue",
        "Technical Issue",
        "Other"
    ]

    complaints = Complaint.objects.filter(user=request.user)

    # ✅ FORM SUBMIT
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        department = request.POST.get("department")
        student_class = request.POST.get("student_class")
        category = request.POST.get("category")

        # 🔴 VALIDATION
        if not all([title, description, department, student_class, category]):
            messages.error(request, "All fields are required!")
        else:
            Complaint.objects.create(
                user=request.user,
                title=title,
                description=description,
                department=department,
                student_class=student_class,
                category=category,
                status="Pending"
            )

            messages.success(request, "Complaint submitted successfully!")
            return redirect("complaintreg")

    # 📊 DASHBOARD DATA
    total = complaints.count()
    pending = complaints.filter(status="Pending").count()
    resolved = complaints.filter(status="Resolved").count()

    recent_complaints = complaints.order_by('-id')[:5]

    return render(request, "complaintreg.html", {
# REMOVE json.dumps
        "dept_classes": dept_classes,
        "categories": categories,
        "total": total,
        "pending": pending,
        "resolved": resolved,
        "recent_complaints": recent_complaints
    })
    
def logout_fun(request):
    logout(request)
    return redirect("signin")

@login_required
def view_complaint(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, "view_complaint.html", {
        "complaint": complaints
    })
@login_required
def update(request, id):
    complaint = get_object_or_404(Complaint, id=id, user=request.user)

    # 🔥 Department → Classes Mapping (same as complaintreg)
    dept_classes = {
        "Computer Science": ["FY MCA", "SY MCA", "TY MCA", "FY BCA", "SY BCA", "TY BCA"],
        "Engineering": ["FE", "SE", "TE", "BE"],
        "Management": ["FY MBA", "SY MBA"],
        "Commerce": ["FY BCom", "SY BCom", "TY BCom"],
        "Arts": ["FY BA", "SY BA", "TY BA"]
    }

    # 🔥 Categories (same as complaintreg)
    categories = [
        "Academic Issue",
        "Faculty Complaint",
        "Exam Issue",
        "Infrastructure",
        "Hostel Problem",
        "Library Issue",
        "Technical Issue",
        "Other"
    ]

    # ✅ UPDATE FORM SUBMIT
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        department = request.POST.get("department")
        student_class = request.POST.get("student_class")
        category = request.POST.get("category")

        # 🔴 VALIDATION
        if not all([title, description, department, student_class, category]):
            messages.error(request, "All fields are required!")
        else:
            complaint.title = title
            complaint.description = description
            complaint.department = department
            complaint.student_class = student_class
            complaint.category = category
            complaint.save()

            messages.success(request, "Complaint updated successfully!")
            return redirect("view_complaint")

    return render(request, "update.html", {
        "complaint": complaint,
        "dept_classes": dept_classes,
        "categories": categories,
    })
@login_required
def delete(request, id):
    complaint = Complaint.objects.get(id=id)
    complaint.delete()
    return redirect("view_complaint")
@login_required
def about(request):

    if request.method == "POST":
        message = request.POST.get("message")

        if message:
            Feedback.objects.create(
                user=request.user,
                message=message
            )
            messages.success(request, "Feedback submitted successfully!")
        else:
            messages.error(request, "Please write something!")

    return render(request, "about.html")
@login_required
def profile(request):
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        # Update user details
        user.username = username
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully ✅")
        return redirect("profile")

    context = {
        "total": 0,
        "pending": 0,
        "resolved": 0,
        "recent": [],
    }

    return render(request, "profile.html", context)


def change_password(request):
    if request.method == "POST":
        old = request.POST.get("old_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        if new != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("profile")

        user = request.user
        if not user.check_password(old):
            messages.error(request, "Current password is incorrect")
            return redirect("profile")

        user.set_password(new)
        user.save()
        update_session_auth_hash(request, user)

        messages.success(request, "Password updated successfully")
        return redirect("profile")