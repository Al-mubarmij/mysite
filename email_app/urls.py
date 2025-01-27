from django.urls import path
from .views import login_view, emails, logout_view, chat

urlpatterns = [
    path('', emails, name='emails'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name="logout"),
    path('chat/', chat, name="chat"),
]