from django.urls import path, include
from quiz import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup', views.signup_view, name='signup'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('afterlogin', views.afterlogin_view, name='afterlogin'),
    path('student/', include('student.urls')),
    path('teacher/', include('teacher.urls')),
]
