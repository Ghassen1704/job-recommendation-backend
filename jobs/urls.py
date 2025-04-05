from django.urls import path
from .views import upload_resume, get_recommended_jobs,signup,login

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login, name="login"),
    path("upload_resume/", upload_resume, name="upload_resume"),
    path("recommendations/", get_recommended_jobs, name="recommended_jobs"),  # Fix the route
]
