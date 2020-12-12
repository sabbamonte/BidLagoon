from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new, name="new"),
    path("listing/<title>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("closed/<title>", views.closed, name="closed"),
    path("category/<title>", views.category, name="category"),
    path("won", views.won, name="won")
]
