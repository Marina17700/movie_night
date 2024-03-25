from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("watchlist/<str:username>", views.watchlist, name="watchlist"),
    path("profile/<str:username>/top", views.profile_top, name="top"),

    # API routes
    path('add', views.add, name='add'),
    path('remove', views.remove, name='remove'),
    path('rating', views.rating, name="rating"),
    path('search', views.search, name="search"),
]
