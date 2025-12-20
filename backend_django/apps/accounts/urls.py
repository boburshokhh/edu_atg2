from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("login", views.LoginView.as_view()),
    path("refresh", views.RefreshView.as_view()),
    path("logout", views.LogoutView.as_view()),
    path("me", views.MeView.as_view()),
    path("register-profile", views.RegisterProfileView.as_view()),  # POST for first-time registration
    path("ldap/test", views.LDAPTestView.as_view()),  # GET for config, POST for test auth
]





