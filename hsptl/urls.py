"""hsptl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import notifications.urls
from django.contrib import admin
from django.urls import path,include
from users import views
from django.conf.urls import url


urlpatterns = [
    path('admin/', admin.site.urls),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),

    path('',views.HomeView.as_view(),name='home'),
    path('ap_success/<int:id>',views.ap_success,name='ap_success'),
    path('<int:pk>/',views.AppointmentUpdateView.as_view(),name='update_ap'),
    path('ajax/load_ts/',views.load_timeslots,name='ajax_load_ts'),
    path('token_success/',views.get_token,name='token_success'),

    path('users/', include('users.urls')),
    
    path('hsptl_admin/leave_requests/',views.admin_lreqs,name='a_lreqs'),
    path('hsptl_admin/leave_requests/approve/<int:id>',views.admin_lreq_approve,name='a_lreqs_approve'),
    path('hsptl_admin/leave_requests/reject/<int:id>',views.admin_lreq_reject,name='a_lreqs_reject'),
    path('hsptl_admin/patients_record/',views.admin_pr,name='a_pr'),
    path('hsptl_admin/patients_record/patient/<int:id>',views.p_profile,name='p_profile'),
    path('hsptl_admin/staff_records/',views.admin_sr,name='a_sr'),
    path('hsptl_admin/staff_records/add_new_staff/',views.AddNewStaffView.as_view(),name='a_sr_ans'),
    path('hsptl_admin/staff_records/dr_profile/<int:id>',views.dr_profile,name='dr_profile'),
    path('hsptl_admin/circular/',views.admin_cc,name='a_cc'),
    path('hsptl_admin/circular/post/',views.admin_cc_post,name='a_cc_post'),
    
    path('doctor/appointments/',views.doctor_ap,name='d_ap'),
    path('doctor/appointments/verify/<int:id>',views.doctor_pverify,name='p_verify'),
    path('doctor/leave_requests/',views.doctor_lreqs,name='d_lreqs'),
    path('doctor/leave_requests/revert/<int:id>',views.doctor_lreq_revert,name='d_lreqs_revert'),
    path('doctor/patient_records/',views.doctor_pr,name='d_pr'),
    path('doctor/apply_leave/',views.doctor_al,name='d_al'),

    path('opc/patient_records/',views.opc_pr,name='opc_pr'),
    path('opc/patient_tokens/',views.opc_pt,name='opc_pt'),
    path('opc/patient_tokens/reset',views.opc_reset,name='opc_reset'),
    path('opc/patient_tokens/active',views.opc_active,name='opc_active'),
    path('opc/patient_tokens/verify/<int:id>',views.opc_pin_verify,name='opc_verify'),
    path('opc/patient_tokens/done/<int:id>',views.opc_done,name='opc_done'),
    path('opc/patient_tokens/absent/<int:id>',views.opc_absent,name='opc_absent'),
]