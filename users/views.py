from datetime import date, datetime
from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from notifications.signals import notify
from django.contrib import messages

from django.http import HttpResponse, HttpResponseRedirect
from .forms import AppointmentForm, PatientUserCreationForm,DoctorUserCreationForm,CustomLoginForm,LeaveRequestForm, OPCEntryForm
from .models import CustomUser, DoctorAppointment, OPToken, OPTokenStatus, OutpatientCoordinator, Patient,Doctor,LeaveReq,DoctorAppointment
import math
import random

def ap_success(request,id):
    appointment=DoctorAppointment.objects.get(id=id)
    return render(request,'appointment_success.html',context={'Appointment':appointment})

def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)] 
    return OTP

@login_required(login_url='/login/')
def get_token(request):
    opc=OPTokenStatus.objects.all()[0]
    patient=Patient.objects.get(user=request.user)
    opc.add_token()
    ptoken=OPToken(name=patient.name,age=patient.age,mobile=patient.mobile,token_no=opc.current_token_no,otp=generateOTP(),is_reg_user=True,user=request.user,)
    ptoken.save()
    return render(request,'token_success.html',context={'ptoken':ptoken})

class HomeView(generic.CreateView):
    model=DoctorAppointment
    form_class=AppointmentForm
    template_name='index.html'

    def form_invalid(self,form):   
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.patient=self.request.user.is_patient()
        self.object.otp=generateOTP()
        self.object.save()
        return redirect('ap_success',id=self.object.id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opc']=OutpatientCoordinator.objects.all()[0]
        opts=OPTokenStatus.objects.all()[0].current_token_no
        if opts>0:
            context['OPCStatus']=str(opts)
        else:
            context['OPCStatus']='N/A'
        ot=OPToken.objects.filter(is_done=False,is_absent=False)
        if ot:
            context['ongoing_token']=ot.order_by('token_no')[0].token_no
        else:
            context['ongoing_token']='N/A'
        if self.request.user.is_authenticated:
            ht=OPToken.objects.filter(is_done=False,is_absent=False,user=self.request.user)
            if ht:
                context['having_token']=ht[0]
                if ot:
                    diff=ht[0].token_no-ot.order_by('token_no')[0].token_no
                    if diff>2:
                        context['status']=str(diff)+' tokens are before your turn'
                    elif diff>=1:
                        context['status']='Your turn is coming. Need to reach here.'
                    else:
                        context['status']='Its your turn'
            else:
                context['having_token']=False
        if self.request.user.is_authenticated and Patient.objects.filter(user=self.request.user):
            context["patient"] = Patient.objects.get(user=self.request.user)
        if self.request.user.is_authenticated and OPToken.objects.filter(user=self.request.user,is_absent=False,is_done=False):
            context['last_token']=OPToken.objects.get(user=self.request.user,is_absent=False,is_done=False)
        return context

class AppointmentUpdateView(generic.UpdateView):
    model=DoctorAppointment
    form_class=AppointmentForm
    success_url=reverse_lazy('home')
    template_name='index.html'

def load_timeslots(request):
    date=request.GET.get('date')
    department=request.GET.get('department')
    booked_timeslots=[i.timeslot for i in DoctorAppointment.objects.filter(date=date,department=department)]
    return render(request,'timeslot_dp.html',context={'booked_timeslots':booked_timeslots,'ts_list':DoctorAppointment.TIMESLOT_LIST})

@login_required(login_url='/users/admin_login/')
def admin_lreqs(request):
    reqs=LeaveReq.objects.filter(is_pending=True).all()
    return render(request,'admin_panel/leave_req_page.html',context={'reqs':reqs,'lreqs':True})

@login_required(login_url='/users/admin_login/')
def admin_lreq_approve(request,id):
    req=LeaveReq.objects.get(id=id)
    doc=req.user.is_doctor()
    if doc:
        if req.l_type.__str__()=='Casual Leave':
            doc.cs_leave-=req.total_days
        elif req.l_type.__str__()=='Privilege Leave':
            doc.p_leave-=req.total_days
        elif req.l_type.__str__()=='Medical':
            doc.med_leave-=req.total_days
        doc.save()
    req.is_pending=False
    req.is_approved=True
    req.save()
    notify.send(request.user,recipient=doc.user,verb='Leave request status',description="Your leave request from "+str(req.from_date)+" to "+str(req.to_date)+" is approved.")
    return HttpResponseRedirect('/hsptl_admin/leave_requests/')

@login_required(login_url='/users/admin_login/')
def admin_lreq_reject(request,id):
    req=LeaveReq.objects.get(id=id)
    req.is_pending=False
    req.is_approved=False
    req.save()
    notify.send(request.user,recipient=req.user,verb='Leave request status',description="Your leave request from "+str(req.from_date)+" to "+str(req.to_date)+" is rejected.")
    return HttpResponseRedirect('/hsptl_admin/leave_requests/')

@login_required(login_url='/users/admin_login/')
def admin_pr(request):
    patients=Patient.objects.all()
    return render(request,'admin_panel/patient_record_screen.html',context={'patients':patients,'pr':True})

@login_required(login_url='/users/admin_login/')
def admin_sr(request):
    print([i.user.id for i in Doctor.objects.all()])
    return render(request,'admin_panel/staff_records_screen.html',context={'doctors':Doctor.objects.all(),'sr':True})

@login_required(login_url='/users/admin_login/')
def admin_cc(request):
    return render(request,'admin_panel/circular_screen.html',context={'cc':True})


@login_required(login_url='/users/admin_login/')
def admin_cc_post(request):
    try:
        if request.method=='POST':
            sender=request.user
            receivers=Doctor.objects.all()
            for receiver in receivers:
                notify.send(sender,recipient=receiver.user,verb='Circular from Admin',description=request.POST['title'])
            return HttpResponseRedirect('/hsptl_admin/circular/')
    except Exception as e:
        print(e)

class AddNewStaffView(generic.CreateView):
    form_class = DoctorUserCreationForm
    template_name = 'admin_panel/add_new_staff.html'
    success_url=reverse_lazy('a_sr')

    def form_valid(self, form):
        user=form.save()
        
        doc=Doctor()
        doc.user=user
        doc.name=form.cleaned_data['name']
        doc.mobile=form.cleaned_data['mobile']
        print(form.cleaned_data['mobile'])
        doc.address=form.cleaned_data['address']
        doc.speciality=form.cleaned_data['speciality']
        doc.dob=form.cleaned_data['dob']
        doc.save()
        return super(AddNewStaffView, self).form_valid(form)

@login_required(login_url='/users/admin_login/')
def dr_profile(request,id):
    return render(request,'admin_panel/dr_profile_view.html',context={'doctor':Doctor.objects.get(user=id)})

@login_required(login_url='/users/admin_login/')
def p_profile(request,id):
    return render(request,'admin_panel/p_profile_view.html',context={'patient':Patient.objects.get(user=id)})

@login_required(login_url='/users/staff_login/')
def doctor_ap(request):
    appointments=DoctorAppointment.objects.filter(department=request.user.is_doctor().speciality,is_verified=False,date=timezone.now().date()).order_by('timeslot')
    return render(request,'doctor_panel/appointments_page.html',context={'Appointments':appointments,'doctor':Doctor.objects.get(user=request.user),'ap':True})

@login_required(login_url='/users/staff_login/')
def doctor_pverify(request,id):
    url=request.META.get('HTTP_REFERER')
    if request.method=='POST':
        otp=request.POST['pin']
        ap=DoctorAppointment.objects.get(id=id)
        if ap.otp==otp:
            ap.is_verified=True
            ap.save()
            return HttpResponseRedirect(url)    
        else:
            return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)

@login_required(login_url='/users/staff_login/')
def doctor_lreqs(request):
    reqs=LeaveReq.objects.filter(user=request.user).all().order_by('-from_date')
    doctor=request.user.is_doctor()
    return render(request,'doctor_panel/leave_req_page.html',context={'reqs':reqs,'doctor':doctor,'lreqs':True})

@login_required(login_url='/users/staff_login/')
def doctor_lreq_revert(request,id):
    LeaveReq.objects.get(id=id).delete()
    return HttpResponseRedirect('/doctor/leave_requests/')

@login_required(login_url='/users/staff_login/')
def doctor_pr(request):
    patients=Patient.objects.all()
    return render(request,'doctor_panel/patient_record_screen.html',context={'patients':patients,'doctor':Doctor.objects.get(user=request.user),'pr':True})

@login_required(login_url='/users/staff_login/')
def doctor_cmp(request):
    return render(request,'doctor_panel/index.html',context={'cmp':True})

@login_required(login_url='/users/staff_login/')
def doctor_al(request):
    user=request.user
    leave_map={
        'Privilege Leave':user.is_doctor().p_leave,
        'Medical':user.is_doctor().med_leave,
        'Casual Leave':user.is_doctor().cs_leave
    }
    if request.method == 'POST':
        form=LeaveRequestForm(request.POST)
        if form.is_valid():
            req=form.save(commit=False)
            if req.total_days<=leave_map[req.l_type.__str__()]:
                req.user=user
                req.save()
                return HttpResponseRedirect('/doctor/leave_requests/')
            else:
                return render(request,'doctor_panel/apply_leave_page.html',context={'form':form,'doctor':Doctor.objects.get(user=request.user),'lreqs':True})
        else:
            return render(request,'doctor_panel/apply_leave_page.html',context={'form':form,'doctor':Doctor.objects.get(user=request.user),'lreqs':True})
    else:
        form=LeaveRequestForm()
        return render(request,'doctor_panel/apply_leave_page.html',context={'form':form,'doctor':Doctor.objects.get(user=request.user),'lreqs':True})

@login_required(login_url='/users/staff_login/')
def opc_pr(request):
    patients=Patient.objects.all()
    return render(request,'opc_panel/patient_record_screen.html',context={'patients':patients,'pr':True})

@login_required(login_url='/users/staff_login/')
def opc_pt(request):
    tokens=OPToken.objects.filter(is_done=False,is_absent=False)
    if request.method=='POST':
        form=OPCEntryForm(request.POST)
        if form.is_valid():
            opc=OutpatientCoordinator.objects.get(user=request.user)
            opc.status.add_token()
            ptoken=form.save(commit=False)
            ptoken.token_no=opc.status.current_token_no
            ptoken.save()
            opc=OutpatientCoordinator.objects.get(user=request.user)
            return HttpResponseRedirect('/opc/patient_tokens/')
    form=OPCEntryForm()
    context={'tokens':tokens,'form':form,'opc':OutpatientCoordinator.objects.get(user=request.user),'pt':True}
    ot=OPToken.objects.filter(is_done=False,is_absent=False)
    if ot:
        context['ongoing_token']=ot.order_by('token_no')[0].token_no
    else:
        context['ongoing_token']='N/A'
    opts=OPTokenStatus.objects.all()[0].current_token_no
    if opts>0 and ot:
        context['OPCStatus']=str(opts)
    else:
        context['OPCStatus']='N/A'
    return render(request,'opc_panel/token_list.html',context=context)

@login_required(login_url='/users/staff_login/')
def opc_reset(request):
    url=request.META.get('HTTP_REFERER')
    opts=OutpatientCoordinator.objects.get(user=request.user)
    opts.current_token_no=0
    opts.save()
    for i in OPToken.objects.filter(is_done=False,is_absent=False):
        i.is_absent=True
        i.save()
    op=OPTokenStatus.objects.all()[0]
    op.current_token_no=0
    op.save()
    return HttpResponseRedirect(url)

@login_required(login_url='/users/staff_login/')
def opc_active(request):
    url=request.META.get('HTTP_REFERER')
    opts=OutpatientCoordinator.objects.get(user=request.user)
    opts.is_active=not(opts.is_active)
    opts.save()
    return HttpResponseRedirect(url)

@login_required(login_url='/users/staff_login/')
def opc_pin_verify(request,id):
    url=request.META.get('HTTP_REFERER')
    if request.method=='POST':
        otp=request.POST['pin']
        ap=OPToken.objects.get(id=id)
        if ap.otp==otp:
            ap.is_verified=True
            ap.save()
            return HttpResponseRedirect(url)    
        else:
            return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)

@login_required(login_url='/users/staff_login/')
def opc_done(request,id):
    url=request.META.get('HTTP_REFERER')
    opt=OPToken.objects.get(id=id)
    if opt.is_reg_user:
        if opt.is_verified:
            opt.is_done=True
            opt.save()
    else:
        opt.is_done=True
        opt.save()
    return HttpResponseRedirect(url)

@login_required(login_url='/users/staff_login/')
def opc_absent(request,id):
    url=request.META.get('HTTP_REFERER')
    opt=OPToken.objects.get(id=id)
    opt.is_absent=True
    opt.save()
    return HttpResponseRedirect(url)


class SignUpView(generic.CreateView):
    form_class = PatientUserCreationForm
    template_name = 'signup_page.html'
    success_url=reverse_lazy('login')

    def form_valid(self, form):
        user=form.save()
        data=Patient()
        data.user=user
        data.name=form.cleaned_data['name']
        data.mobile=form.cleaned_data['mobile']
        data.address=form.cleaned_data['address']
        data.adhaar_no=form.cleaned_data['adhaar_no']
        data.dob=form.cleaned_data['dob']
        data.save()
        return super(SignUpView, self).form_valid(form)

def login_form(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(request,email=email,password=password)
        if user is not None:
            print(user)
            if user.is_patient():
                login(request,user)
                return HttpResponseRedirect('/')
            else:
                messages.warning(request,"Not a patient's account")
                return HttpResponseRedirect('/users/login')
        else:
            messages.warning(request,'Login Failed..!!!Username or password incorrect.')
            return HttpResponseRedirect('/users/login')
    context={}
    return render(request,'signin_page.html',context)

def log_out(request):
    logout(request)
    return HttpResponseRedirect('/')

def login_admin_form(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(request,email=email,password=password)
        if user is not None:
            if user.is_staff:
                login(request,user)
                return HttpResponseRedirect('/hsptl_admin/leave_requests/')
            else:
                context={}
                messages.warning(request,'Not a admin account')
                return render(request,'admin_signin_page.html',context)
        else:
            context={}
            messages.warning(request,'Login Failed..!!!Username or password incorrect.')
            return render(request,'admin_signin_page.html',context)
    context={}
    return render(request,'admin_signin_page.html',context)


def login_staff_form(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(request,email=email,password=password)
        if user is not None:
            print(user)
            if OutpatientCoordinator.objects.filter(user=user):
                login(request,user)
                return HttpResponseRedirect('/opc/patient_tokens/')
            elif Doctor.objects.filter(user=user):
                login(request,user)
                return HttpResponseRedirect('/doctor/appointments/')
            else:
                context={}
                messages.warning(request,'Not a staff account')
                return render(request,'staff_signin_page.html',context)
        else:
            context={}
            messages.warning(request,'Login Failed..!!!Username or password incorrect.')
            return render(request,'staff_signin_page.html',context)
    context={}
    return render(request,'staff_signin_page.html',context)
