from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from accounts.views import login_view, logout_view, intro_video_view
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import pricing_view

# -------------------------
# PUBLIC HOME PAGE
# -------------------------
def home_view(request):
    return render(request, "public/home.html")

def features_view(request):
    return render(request, "public/features.html")

def experiments_view(request):
    return render(request, "public/experiments.html")





urlpatterns = [

    # -------------------------
    # PUBLIC HOME (NEW)
    # ------------------------- # HOMEPAGE
    path("", home_view, name="home"),
    
    # AUTH
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("intro-video/", intro_video_view, name="intro-video"),

    # -------------------------
# PUBLIC PAGES
# -------------------------
path("features/", features_view, name="features"),
path("experiments/", experiments_view, name="experiments"),
path('about/', views.about, name='about'),

    # -------------------------
    # AUTH
    # -------------------------
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # -------------------------
    # APP ROUTES (DASHBOARDS + PRACTICALS)
    # -------------------------
    path("", include("experiments.urls")),

    # -------------------------
    # DJANGO ADMIN (OPTIONAL)
    # -------------------------
    path("admin/", admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)