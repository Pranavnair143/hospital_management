from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.login_form, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('admin_login/',views.login_admin_form,name='alogin'),
    path('staff_login/',views.login_staff_form,name='slogin'),
]