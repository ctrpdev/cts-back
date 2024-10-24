from django.urls import re_path
from . import apis

urlpatterns = [
    re_path('register/', apis.register, name='register'),
    re_path('verify_email/', apis.verify_email, name='verify_email'),
    re_path('login/', apis.login, name='login'),
    re_path('profile/', apis.profile, name='profile'),
    re_path('generate_winner/', apis.generate_winner, name='generate_winner'),
    re_path('check-email/', apis.check_email, name='check_email'),
]
