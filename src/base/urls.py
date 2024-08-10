from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('signup/', views.sign_up, name="sign-up"),
    path('signin/', views.sign_in, name="sign-in"),
    path('logout/', views.logout, name="logout"),
    path('settings/', views.settings, name="settings"),
    path('upload/', views.upload, name="upload"),
    path('like/<str:post_id>/', views.like_post, name="like"),
    path('profile/<str:pk>/', views.profile, name="profile"),
    path('follow/', views.follow, name="follow"),
    path('search/', views.search, name="search"),
]
