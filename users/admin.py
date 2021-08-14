from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import PatientUserCreationForm, CustomUserChangeForm
from .models import DoctorAppointment, CustomUser, OPTokenStatus, OutpatientCoordinator,Patient,Admin,Speciality,Doctor,Designation,LeaveType,LeaveReq,OPToken


class CustomUserAdmin(UserAdmin):
    add_form = PatientUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Patient)
admin.site.register(Admin)
admin.site.register(Speciality)

admin.site.register(Doctor)
admin.site.register(Designation)
admin.site.register(LeaveType)
admin.site.register(LeaveReq)
admin.site.register(DoctorAppointment)
admin.site.register(OutpatientCoordinator)
admin.site.register(OPToken)
admin.site.register(OPTokenStatus)