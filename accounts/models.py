from django.contrib.auth.models import AbstractUser
from django.db import models


# =====================================================
# COLLEGE MODEL (Each Admin = One College)
# =====================================================
class College(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 SOFT DELETE (Disable college instead of deleting)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


# =====================================================
# CUSTOM USER MODEL
# =====================================================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    # Role-based access
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    # 🔗 College ownership
    college = models.ForeignKey(
        College,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="users"
    )

    # 🔗 Track who created this user
    created_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_users"
    )

    # =====================================================
    # 🔥 NEW SAFE ADDITIONS (Student Extra Info)
    # =====================================================

    # Student Roll Number
    roll_no = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Student Roll Number"
    )

    # Mobile Number
    mobile = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="User Mobile Number"
    )

    # 🔥 SOFT DELETE FOR USERS
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# =====================================================
# 🔥 PRINCIPAL REGISTRATION REQUEST MODEL
# =====================================================
class PrincipalRequest(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)

    college_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fullname} - {self.college_name} ({self.status})"


# =====================================================
# 🔥 TEACHER REGISTRATION REQUEST MODEL
# =====================================================
class TeacherRequest(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="teacher_requests"
    )

    password = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fullname} - {self.college.name} ({self.status})"