from django.urls import path
from .import views

urlpatterns = [
    path('', views.shop, name="shop"),
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutUser, name="logout"),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist', views.wishlist, name="wishlist"),
]