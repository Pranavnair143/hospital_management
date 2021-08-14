from django.contrib.auth.forms import UserCreationForm, UserChangeForm,AuthenticationForm
from django.db.models import fields
from django.forms import widgets
from django.utils import timezone
from .models import CustomUser, OPToken,Patient,LeaveReq,DoctorAppointment, Speciality
from django import forms
import datetime
from django.contrib.auth import authenticate

class DateInput(forms.DateInput):
    input_type = 'date'

class PatientUserCreationForm(UserCreationForm):
    name=forms.CharField(max_length=30,widget=forms.TextInput(attrs={'id':'name','placeholder':'Your Full Name'}))
    mobile=forms.CharField(max_length=10,widget=forms.TextInput(attrs={'id':'name','placeholder':'Your Mobile Number'}))
    address=forms.CharField(max_length=150,widget=forms.TextInput(attrs={'id':'name','placeholder':'Your Address'}))
    adhaar_no=forms.CharField(max_length=12,widget=forms.NumberInput(attrs={'id':'name','placeholder':'Your Adhaar No.'}))
    dob=forms.DateField(widget=DateInput(attrs={'max': timezone.now().date}))
    class Meta:
        model = CustomUser
        fields = ('email',)
    
    def clean_email(self):
        email=self.cleaned_data['email'].lower()
        try:
            custom_user=CustomUser.objects.exclude(pk=self.instance.pk).get(email=email)
            print(custom_user)
        except CustomUser.DoesNotExist:
            return email
        raise forms.ValidationError("Email "+str(custom_user)+" is already in user.")
    
    def clean_mobile(self):
        mobile=self.cleaned_data['mobile']
        if len(mobile)!=10:
            print("HELOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            raise forms.ValidationError("Mobile no. should have only 10 digits.")
        print(mobile)
        return mobile
    
    def clean_adhaar_no(self):
        adhaar_no=self.cleaned_data['adhaar_no']
        if len(adhaar_no)!=12:
            raise forms.ValidationError("Adhaar card no. should have only 12 digits.")
        return adhaar_no

class DoctorUserCreationForm(UserCreationForm):
    error_css_class = "errorCss"
    name=forms.CharField(max_length=30,widget=forms.TextInput(attrs={'id':'name','placeholder':'Your Full Name','class':'form-control'}))
    mobile=forms.CharField(max_length=10,widget=forms.TextInput(attrs={'id':'name','placeholder':'Your Mobile Number','class':'form-control'}))
    address=forms.CharField(max_length=150,widget=forms.TextInput(attrs={'id':'name','placeholder':'Your Address','class':'form-control'}))
    dob=forms.DateField(widget=DateInput(attrs={'max': timezone.now().date}))
    speciality=forms.ModelChoiceField(queryset=Speciality.objects.all())
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2',)
    
    def clean_mobile(self):
        mobile=self.cleaned_data['mobile'].lower()
        if len(mobile)!=10:
            raise forms.ValidationError("Mobile no. should have only 10 digits.")
        return mobile

    def clean_email(self):
        email=self.cleaned_data['email'].lower()
        try:
            custom_user=CustomUser.objects.exclude(pk=self.instance.pk).get(email=email)
            print(custom_user)
        except CustomUser.DoesNotExist:
            return email
        raise forms.ValidationError("Email "+str(custom_user)+" is already in user.")
    
class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)


class CustomLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser

class DateInput(forms.DateInput):
    input_type = 'date'

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveReq
        fields = ['l_type','from_date','to_date','desc']
        widgets = {
            'l_type':forms.Select(attrs={'class':'form-control'}),
            'from_date': DateInput(),
            'to_date': DateInput(),
            'desc':forms.Textarea(attrs={"class":"form-control","rows":"3"}),
        }
    def __init__(self, *args, **kwargs): 
        super(LeaveRequestForm, self).__init__(*args, **kwargs)
        self.fields['l_type'].label = 'Leave Type'
        self.fields['from_date'].widget.attrs.update({'min': datetime.date.today()})
        self.fields['to_date'].widget.attrs.update({'min': datetime.date.today()})

class AppointmentForm(forms.ModelForm):
    class Meta:
        model=DoctorAppointment
        fields=['department','date','timeslot']
        widgets={
            'department':forms.Select(attrs={'class':'wp-form-control wpcf7-select'}),
            'date': DateInput(attrs={'min': timezone.now().date}),
            'timeslot':forms.Select(attrs={'class':'wp-form-control wpcf7-select'}),
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if 'date' in self.data and self.data.get('date')!='':
            try:
                date=self.data.get('date')
                department=self.data.get('department')
                self.fields['timeslot'].queryset=[i.timeslot for i in DoctorAppointment.objects.filter(date=date,department=department)]
            except (ValueError,TypeError):
                pass

class OPCEntryForm(forms.ModelForm):
    class Meta:
        model=OPToken
        fields=['name','age','mobile']
        widgets={
            'name':forms.TextInput(attrs={'id':'name','placeholder':"Patient's Name"}),
            'age':forms.NumberInput(attrs={'id':'name','placeholder':"Patient's Age"}),
            'mobile':forms.TextInput(attrs={'id':'name','placeholder':"Patient's Mobile No."})
        }
