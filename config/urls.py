from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from accounts.views import login_view, logout_view
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import pricing_view

# -------------------------
# PUBLIC HOME PAGE
# -------------------------
def home_view(request):
    return render(request, "public/home.html")




urlpatterns = [
   
    # -------------------------
    # PUBLIC HOME (NEW)
    # -------------------------
    path("", home_view, name="home"),
    path('pricing/', pricing_view, name='pricing'),

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