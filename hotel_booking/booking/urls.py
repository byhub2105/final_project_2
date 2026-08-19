from . import views
from django.urls import path

urlpatterns = [
    path('',views.home,name='home'),
    path('rooms/', views.room_type_list, name='room_type_list'),
    path('rooms/<int:pk>/', views.room_type_detail, name='room_type_detail'),
    path('session/<int:pk>/book/', views.book_session, name='book_session'),
    path('booking/<int:pk>/confirmation/', views.booking_confirmation, name='booking_confirmation'),
    path('login',views.login_view,name='login'),
    path('register',views.register_view,name='register'),
    path('logout',views.logout_view,name='logout'),
    path('profile',views.profile_view,name='profile'),
    path('minigame',views.game_view,name='minigame'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard')
]
