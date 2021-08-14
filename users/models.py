from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.translation import ugettext_lazy as __
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(__('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(_('email address'),unique=True)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    date_joined=models.DateTimeField(default=timezone.now)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects=CustomUserManager()

    def __str__(self):
        return self.email
    
    def is_doctor(self):
        try:
            return Doctor.objects.get(user=self)
        except Doctor.DoesNotExist:
            return False
    
    def is_patient(self):
        try:
            return Patient.objects.get(user=self)
        except Patient.DoesNotExist:
            return False

class Patient(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE,primary_key=True)
    name=models.CharField(max_length=30)
    mobile=models.CharField(max_length=10)
    address=models.CharField(max_length=150)
    adhaar_no=models.CharField(max_length=12)
    dob=models.DateField()

    @property
    def age(self):
        return timezone.now().year-self.dob.year

    def __str__(self):
        return self.name

class Admin(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE,primary_key=True)

class Speciality(models.Model):
    name=models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
    def assigned_doctor(self):
        return Doctor.objects.get(speciality=self)

class OPTokenStatus(models.Model):
    current_token_no=models.IntegerField()
    def __str__(self):
        return str(self.current_token_no)
    
    def add_token(self):
        self.current_token_no+=1
        self.save()
    
    def reset_token(self):
        self.current_token_no=1
        self.save()

class OutpatientCoordinator(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE,primary_key=True)
    is_active=models.BooleanField(default=True)
    status=models.ForeignKey(OPTokenStatus,on_delete=models.CASCADE)

    def __str__(self):
        return 'OPCoordinator'

class OPToken(models.Model):
    name=models.CharField(max_length=20)
    age=models.IntegerField()
    mobile=models.CharField(max_length=10)
    token_no=models.IntegerField()
    is_done=models.BooleanField(default=False)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    is_absent=models.BooleanField(default=False)
    otp=models.CharField(max_length=6,null=True)
    is_reg_user=models.BooleanField(default=False)
    is_verified=models.CharField(max_length=6,null=True)

    def __str__(self):
        return self.name+'  ('+str(self.token_no)+')'

class Doctor(models.Model):
    name=models.CharField(max_length=30)
    mobile=models.CharField(max_length=10)
    address=models.CharField(max_length=150)
    dob=models.DateField()
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE,primary_key=True)
    speciality=models.OneToOneField(Speciality, on_delete=models.CASCADE)
    med_leave=models.IntegerField(default=30)
    p_leave=models.IntegerField(default=20)
    cs_leave=models.IntegerField(default=10)

    def __str__(self):
        return self.name
    
    @property
    def on_leave(self):
        now=timezone.now().date()
        leave=self.user.leave_period.filter(is_approved=True).filter(to_date__gte=now,from_date__lte=now)
        if leave:
            return leave[0]
        else:
            return False


class Designation(models.Model):
    
    name=models.CharField(max_length=30)

    def __str__(self):
        return self.name
    

class LeaveType(models.Model):
    name=models.CharField(max_length=30)
    
    def __str__(self):
        return self.name

class LeaveReq(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leave_period')
    l_type=models.ForeignKey(LeaveType, on_delete=models.CASCADE)

    from_date=models.DateField()
    to_date=models.DateField()
    desc=models.CharField(max_length=100)
    is_pending=models.BooleanField(default=True)
    is_approved=models.BooleanField(default=False)

    def __str__(self):
        return self.l_type.name
    
    @property
    def total_days(self):
        return (self.to_date-self.from_date).days

class DoctorAppointment(models.Model):
    TIMESLOT_LIST = [
        (0, '10:00–10:30'),
        (1, '10:30–11:00'),
        (2, '11:00–11:30'),
        (3, '11:30–12:00'),
        (4, '12:00–12:30'),
        (5, '12:30–13:00'),
        (6, '14:30–15:00'),
        (7, '15:00–15:30'),
        (8, '15:30–16:00'),
        (9, '16:00–16:30'),
        (10, '16:30–17:00'),
        (11, '17:00–17:30'),
        (12, '17:30–18:00'),
        (13, '18:00–18:30'),
        (14, '18:30–19:00'),
    ]
    TIMESLOT_STR_LIST=[i[1] for i in TIMESLOT_LIST]
    patient=models.ForeignKey(Patient,on_delete=models.CASCADE)
    department=models.ForeignKey(Speciality,on_delete=models.CASCADE)
    date=models.DateField()
    timeslot=models.IntegerField(choices=TIMESLOT_LIST)
    otp=models.CharField(max_length=6)
    is_verified=models.BooleanField(default=False)

    @property
    def time(self):
        return self.TIMESLOT_LIST[self.timeslot][1]

    def __str__(self):
        return self.patient.name+'('+self.department.__str__()+')'