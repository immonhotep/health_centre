from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views.generic import View,ListView,DetailView
from .forms import UserRegisterForm,UserLoginForm,AdminForm,DoctorProfileForm,PatientProfileForm,UserForm,HospitalForm, \
    DoctorTimeTableForm,ExpertiseForm,ChangePasswordForm,PatientInformationForm,ResetPasswordForm,MessageForm,ReplyForm,CreateAdminForm,TwoFactorForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.views import PasswordResetView,PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .mixins import SuperUserRequiredMixin,SiteAdminRequiredMixin,DoctorRequiredMixin,PatientRequiredMixin,DoctorOrAdminRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
import re
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .models import User,DoctorHospitalInfo,DoctorTimeTable,Expertise,DoctorProfile,Appointment,PatientProfile,PatientHealtInformation,TimetableLog,Message, \
    ReplyMessage,Notification,LoginUpdate,DoctorsRatio,HospitalRatio,TwoFactorAuth
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from datetime import date,timedelta,datetime
from django.utils import timezone
from .decorators import user_is_siteadmin
from django.utils.decorators import method_decorator
from django.db.models import Q
from itertools import chain


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
#prevent error related force_text not found
from django.utils.encoding import force_str as force_text


import uuid
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from .utils import Calendar
import calendar




class DashboardView(LoginRequiredMixin,View):

    def get(self,request):

        if request.user.is_staff:

            L = request.GET.get('login')
            J = request.GET.get('join')

            if L:
                if L == "asc":
                    users = User.objects.all().order_by('last_login')
                    L  = "dsc"
                else:
                    users = User.objects.all().order_by('-last_login')
                    L = "asc"
            elif J:

                if J == "asc":
                    users = User.objects.all().order_by('date_joined')
                    J  = "dsc"              
                else:
                    users = User.objects.all().order_by('-date_joined')
                    J = "asc"
            else:
                users = User.objects.all().order_by('is_active')
           


            doctors = DoctorProfile.objects.all()
            patients = PatientProfile.objects.all()

            p = Paginator(users,6)
            page = self.request.GET.get('page')

            try:
                users = p.page(page)
            except PageNotAnInteger:
                users = p.page(1)
            except EmptyPage:
                users = p.page(p.num_pages)

            context={'doctors':doctors,'patients':patients,'users':users,'L':L,'J':J}


            return render(request,'main/admin_dashboard.html',context)
        
        elif request.user.type =="P":

            archived = Appointment.objects.filter(patient=request.user.patientprofile,archived=True)
            appointments = Appointment.objects.filter(patient=request.user.patientprofile,archived=False)
            all_doctors = DoctorProfile.objects.all()
            expertises = Expertise.objects.all()
            patient = request.user.patientprofile
            mydoctors =  []
            for appointment in patient.appointment_set.all():
                if appointment.doctor:
                    if not appointment.doctor in mydoctors:
                        mydoctors.append(appointment.doctor)

            p = Paginator(mydoctors,6)
            page = self.request.GET.get('page')

            try:
                mydoctors = p.page(page)
            except PageNotAnInteger:
                mydoctors = p.page(1)
            except EmptyPage:
                mydoctors = p.page(p.num_pages)

            context = {'expertises':expertises,'appointments':appointments,'archived':archived,'mydoctors':mydoctors,'all_doctors':all_doctors}
            return render(request,'main/patient_dashboard.html',context)
        
        elif request.user.type == "D":

            timetables = DoctorTimeTable.objects.filter(doctor=request.user.doctorprofile,occupied=False,archived=False)
            archived = DoctorTimeTable.objects.filter(doctor=request.user.doctorprofile,archived=True)
            all_patients = PatientProfile.objects.all()
            count = archived.count()
            patients = []
            doctor = request.user.doctorprofile

            current_day = date.today()
            current_day_tables=[]
            for table in timetables:
                if table.date == current_day:
                  current_day_tables.append(table)


            for appointment in doctor.appointment_set.all():
                if appointment.patient:
                    if not appointment.patient in patients:
                        patients.append(appointment.patient)

            p = Paginator(patients,6)
            page = self.request.GET.get('page')

            try:
                patients = p.page(page)
            except PageNotAnInteger:
                patients = p.page(1)
            except EmptyPage:
                patient = p.page(p.num_pages)

            context = {'current_day_tables':current_day_tables,'count':count,'patients':patients,'all_patients':all_patients}
            return render(request,'main/doctor_dashboard.html',context)



class UseregisterView(View):

    def get(self,request):

        if request.user.is_authenticated:
            return redirect('dashboard')

        form = UserRegisterForm()
        context={'form':form}
        return render(request,'main/register.html',context)

    def post(self,request):

        form = UserRegisterForm(request.POST)
        if form.is_valid():
           user = form.save(commit=False)
           user.is_active = False
           user.save()

           current_site = get_current_site(self.request)
           subject = 'Activate Your Account'
           message = render_to_string('settings/account_activation_email.html', {
            'user':user,
            'domain':current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),})
           
           try:
                user.email_user(subject=subject, message=message)
                messages.success(self.request,'To finish registration please check your mailbox including spam folder and follow instructions')
           except:
               messages.error(self.request,'Mail Server Connection problem, please turn to website admin')

           
        else:

            for key, error in list(form.errors.items()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, "You must pass the reCAPTCHA test")
                    continue
                messages.error(request, error) 

            return redirect('register')

        return redirect('login')
    


def account_activation(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
    except():
        pass

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Your registration finished now please login')
        return redirect('login')

    else:
        return render(request, 'settings/activation_invalid.html')



class UserLoginview(View):

    def get(self,request):

        if request.user.is_authenticated:
           return redirect('dashboard') 
        
        form = UserLoginForm()
        context={'form':form}
        return render(request,'main/login.html',context)

    def post(self,request):
        form = UserLoginForm(request,data=request.POST)
        if form.is_valid():
           username = form.cleaned_data['username']
           password = form.cleaned_data['password']
           user = authenticate(request,username=username,password=password)
           
           if user is not None:

            code = str(uuid.uuid4()).replace('-', '')[:8]
            auth, created = TwoFactorAuth.objects.get_or_create(user=user,code=code)
            current_site = get_current_site(self.request)
            subject = 'Your Login code for 2FA login - (This code only can use once, and will expire within 5 minutes)'
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            message = render_to_string('settings/twofactorlogin_email.html', {
            'user':user,
            'domain':current_site.domain,
            'uid': uid,
            'code':code})

            try:
                user.email_user(subject=subject, message=message)
                messages.success(self.request,'To finish login with 2FA authenticattion check your mailbox for code')
                return redirect('twofactor_login',uid)
            except:
               messages.error(self.request,'Mail Server Connection problem, please turn to website admin')  
               

        else:
            for key, error in list(form.errors.items()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, "You must pass the reCAPTCHA test")
                    continue
                messages.error(request, error)  
            
        return redirect('login')
        


class TwoFactorLogin(View):

    def archive_outdated_data(self,request):
        today = date.today()
        appointments = Appointment.objects.filter(doctor=request.user.doctorprofile,timetable__date__lt=today)
        timetables = DoctorTimeTable.objects.filter(doctor=request.user.doctorprofile,date__lt=today)
        if appointments.exists():
            for appointment in appointments:
                if appointment.archived != True:
                    appointment.archived = True
                    appointment.save()

        if timetables.exists():
            for timetable in timetables:
                if timetable.archived != True:
                    timetable.archived = True   
                    timetable.save()
                    entry="Time slot has been archived"
                    TimetableLog.objects.create(timetable=timetable,entry=entry)


    def maintenance_user(self,request):
        
        current_time = timezone.now()
        read_notes = Notification.objects.filter(user=request.user,read=True)
        read_notes.delete()
        
        expired = TwoFactorAuth.objects.filter(user=request.user,expiration__lt=current_time)
        expired.delete()

    def Check_Profile(self,request):

        if request.user.type == "A":
            profile = request.user.adminprofile
        elif request.user.type == "D":
            profile = request.user.doctorprofile     
        elif request.user.type == "P":
            profile = request.user.patientprofile
        
        fields  = profile._meta.concrete_fields
  
        empty_fields = []
        for field in fields:
            value = getattr(profile, field.name)
            if not value:
                empty_fields.append('field.name')
             
        if len(empty_fields) > 0:
            messages.info(request,'your profile is not complete please update it')
            return False
        return True

    def get(self,request,uidb64):

        if request.user.is_authenticated:
            return redirect('dashboard')


        form = TwoFactorForm()
        context = {'form':form,'uidb64':uidb64}
        return render(request,'settings/twofactorlogin.html',context)
    
    def post(self,request,uidb64):

        current_time = timezone.now()

        form = TwoFactorForm(request.POST)
        if form.is_valid():

            code = form.cleaned_data['code']
            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                try:
                    stored_code = TwoFactorAuth.objects.get(user=user,code=code)
                    if stored_code.expiration > current_time:
                        login(request,user)
                        self.maintenance_user(request)
                        complete = self.Check_Profile(request)
                        try:
                            if user.doctorprofile:
                                self.archive_outdated_data(request) 
                        except:
                            pass

                        stored_code.delete()
                        messages.success(request,f'{user} has been logged in')
                        if complete == True:
                            return redirect('dashboard')
                        else:
                            return redirect('update_profile')
                    else:
                        messages.error(request,'your 2FA code expired, try to login again to generate other one')
                       
                        return redirect('login')
                except:
                    messages.error(request,'Invalid 2FA code, try again')
            except:
                messages.error(request,'Invalid 2FA code, try again')      
        else:
            for key, error in list(form.errors.items()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, "You must pass the reCAPTCHA test")
                    continue
                messages.error(request, error)

         
        return redirect('twofactor_login',uidb64)

        
class UserLogoutview(LoginRequiredMixin,View):

    def post(self,request):
        logout(request)
        messages.info(request,'Logout successfull')
        return redirect('dashboard')


class UpdateProfile(LoginRequiredMixin,View):

    def get(self,request):

        user =  request.user

        if  user.is_staff:
            form = AdminForm(instance=user.adminprofile)
        elif user.type == "P":
            form = PatientProfileForm(instance=user.patientprofile)
        elif user.type == "D":
            form = DoctorProfileForm(instance=user.doctorprofile)

        user_form = UserForm(instance=user)
        context={'form':form,'user_form':user_form}
        return render(request,'main/update_profile.html',context)

    def post(self,request):

        user =  request.user

        if  user.is_staff:
            form = AdminForm(request.POST,request.FILES,instance=user.adminprofile)
        elif user.type == "P":
            form = PatientProfileForm(request.POST,request.FILES,instance=user.patientprofile)
        elif user.type == "D":
            form = DoctorProfileForm(request.POST,request.FILES,instance=user.doctorprofile)

        user_form = UserForm(request.POST,instance=user)
        
        if form.is_valid() and user_form.is_valid():
            form.save()
            user_form.save()
            messages.success(request,'Your profile has been updated')

        else:
            for error in list(form.errors.values()):
                messages.error(request,error)

            for error in list(user_form.errors.values()):
                messages.error(request,error)

        return redirect('update_profile')
    

class ManageAdmins(SuperUserRequiredMixin,View):

    def get(self,request):

        form = CreateAdminForm()
        context={'form':form}
        return render(request,'main/manage_admin.html',context)

    def post(self,request):

        form = CreateAdminForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.type = "A"
            user.is_staff = True
            user.is_superuser = False
            user.save()
            messages.success(request,f' new admin user: {user} has been created ')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
        return redirect('manage_admin')


class AdminDetail(LoginRequiredMixin,View):

    def get(self,request,pk):

        admin = get_object_or_404(User, pk=pk)
        context = {'admin':admin}
        return render(request,'main/admin_profile.html',context)
               

class UpdateHospitalInfo(DoctorRequiredMixin,View):

    def get(self,request):

        hospital = request.user.doctorprofile.hospital 
        form = HospitalForm(instance=hospital)
        context={'form':form}
        return render(request,'main/update_hospital_info.html',context)
    
    def post(self,request):

        hospital = request.user.doctorprofile.hospital
        doctor = request.user.doctorprofile
             
        form = HospitalForm(request.POST,request.FILES,instance=hospital)
        if form.is_valid():
            hospital = form.save()
            doctor.hospital = hospital
            doctor.save()
            messages.success(request,f'hospital: {hospital} data has been updated')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
        return redirect('hospital')
    
    def handle_no_permission(self):
        return redirect('forbidden')
    

class ListAllHospitals(LoginRequiredMixin,View):

    def get(self,request):

        hospitals = DoctorHospitalInfo.objects.all().order_by('-name')
        count = hospitals.count()
        

        p = Paginator(hospitals,4)
        page = self.request.GET.get('page')

        try:
            hospitals = p.page(page)
        except PageNotAnInteger:
            hospitals = p.page(1)
        except EmptyPage:
            hospitals = p.page(p.num_pages)

        context={'hospitals':hospitals,'count':count}
        return render(request,'main/hospitals.html',context)
    


class HospitalDetail(LoginRequiredMixin,DetailView):

    model = DoctorHospitalInfo  
    template_name = "main/hospital_detail.html"

      
    def get_context_data(self, *args, **kwargs):

        context = super(HospitalDetail,self).get_context_data(*args,**kwargs)
        hospital = get_object_or_404(DoctorHospitalInfo,pk=self.kwargs['pk'])
        try:
            ratio = HospitalRatio.objects.filter(hospital=hospital,patient=self.request.user.patientprofile)
        except:
            ratio = {}

        context['hospital'] = hospital
        context['ratio'] = ratio
        return context


class TimeTable(DoctorRequiredMixin,View):

    def get(self,request):

        doctor = request.user.doctorprofile 
        timetables = DoctorTimeTable.objects.filter(doctor=doctor,archived=False).order_by('-date')
        count = timetables.count()
        
        
        p = Paginator(timetables,6)
        page = self.request.GET.get('page')

        try:
            timetables = p.page(page)
        except PageNotAnInteger:
            timetables = p.page(1)
        except EmptyPage:
            timetables = p.page(p.num_pages)

        form = DoctorTimeTableForm()
        context={'form':form,'timetables':timetables,'count':count}
        return render(request,'main/timetable.html',context)
    
    def post(self,request):

        doctor = request.user.doctorprofile
        current_date = date.today()

        form = DoctorTimeTableForm(request.POST)
        if form.is_valid():
            data=form.save(commit=False)
            data.doctor = doctor
            if data.date < current_date:
                messages.error(request,'Unable to add date in the past')
            elif data.end_time <= data.start_time:
                messages.error(request,'Start time unable to set equal or greater than end time')
            else:
                data.save()
                entry=f"{data.doctor.user.first_name} {data.doctor.user.last_name} created time slot"
                TimetableLog.objects.create(timetable=data,entry=entry)
                messages.success(request,f'new time slot {data} has been created')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)

        return redirect('timetable')
    
    def handle_no_permission(self):
        return redirect('forbidden')
    

class TimeTableDetail(DoctorRequiredMixin,View):

    def get(self,request,pk):

        timetable = get_object_or_404(DoctorTimeTable,pk=pk)

        if timetable.archived :
            messages.info(request,'This time slot archived, you have no permission to modify')
            return redirect('forbidden')
            

        if timetable.doctor == request.user.doctorprofile:        
            form = DoctorTimeTableForm(instance=timetable)
            context={'form':form}
            return render(request,'main/timetable_detail.html',context)
        else:
            messages.error(request,f'This timetable belong to Dr. {timetable.doctor.user.first_name} {timetable.doctor.user.last_name}')

        return redirect('forbidden')
       
        
    def post(self,request,pk):
        timetable = get_object_or_404(DoctorTimeTable,pk=pk)
        current_date = date.today()
        if timetable.doctor == request.user.doctorprofile:
        
            form = DoctorTimeTableForm(request.POST,instance=timetable)
            if form.is_valid():
                data=form.save(commit=False)
                if data.date < current_date:
                    messages.error(request,'Unable to add date in the past')
                elif data.end_time <= data.start_time:
                    messages.error(request,'Start time unable to set equal or greater than end time')
                else:
                    entry=f'Dr. {data.doctor.user.first_name} {data.doctor.user.last_name} modified the timeslot'
                    data.save()
                    TimetableLog.objects.create(timetable=data,entry=entry)

                    try:
                        appointment = Appointment.objects.get(timetable=data)
                        if appointment:
                            Notification.objects.create(type="A",note=f'{entry}',user=appointment.patient.user)
                    except:
                        pass
                    messages.success(request,f'Time slot {data} has been modified')
            else:
                messages.error(request,'Ooops something went wrong')
              
            return redirect('timetable')
        else:
            return redirect('forbidden') 


class ListArchivedTimetables(DoctorRequiredMixin,View):

    def get(self,request):

        timetables = DoctorTimeTable.objects.filter(doctor=request.user.doctorprofile,archived=True).order_by('-date') 
        count = timetables.count()
        p = Paginator(timetables,10)
        page = self.request.GET.get('page')

        try:
            timetables = p.page(page)
        except PageNotAnInteger:
            timetables = p.page(1)
        except EmptyPage:
            timetables = p.page(p.num_pages)



        context={'timetables':timetables,'count':count} 
        return render(request,'main/archived_timetables.html',context)   
        
  

class DeleteTimeTable(DoctorRequiredMixin,UserPassesTestMixin,View):
    
    def post(self,request,pk):

        timetable = get_object_or_404(DoctorTimeTable,pk=pk)

        if timetable.doctor == request.user.doctorprofile:

            try:
                appointment = Appointment.objects.get(timetable=timetable)

                if appointment:
                    entry=f'Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name} deleted the time slot and cancelled the appointment with you'
                    Notification.objects.create(type="A",note=f'{entry}',user=appointment.patient.user)
            except:
                pass
    
            timetable.delete()
            messages.success(request,'timeslot has been removed')
            return redirect('timetable')
        else:
            return redirect('forbidden')
    

class ExpertiseView(LoginRequiredMixin,View):

    def get(self,request):

        expertises = Expertise.objects.all().order_by('-name')

        p = Paginator(expertises,6)
        page = self.request.GET.get('page')

        try:
            expertises = p.page(page)
        except PageNotAnInteger:
            expertises = p.page(1)
        except EmptyPage:
            expertises = p.page(p.num_pages)

        form = ExpertiseForm()
        context={'form':form,'expertises':expertises}
        return render(request,'main/expertise.html',context)

    
    @method_decorator(user_is_siteadmin)
    def post(self,request):
        
        form = ExpertiseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'expertise has been created')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
        return redirect('expertise')
    

class ExpertiseDetailView(SiteAdminRequiredMixin,View):

    def get(self,request,pk):

       expertise = get_object_or_404(Expertise,pk=pk)

       form = ExpertiseForm(instance=expertise)
       context={'form':form}
       return render(request,'main/expertise_detail.html',context)

    def post(self,request,pk):
        expertise = get_object_or_404(Expertise,pk=pk)
        form = ExpertiseForm(request.POST,instance=expertise)
        if form.is_valid():
            form.save()
            messages.success(request,'expertise updated')

        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
        return redirect('expertise')
    

class DeleteExpertise(SiteAdminRequiredMixin,View):
    
    def post(self,request,pk):

        expertise = get_object_or_404(Expertise,pk=pk)
        expertise.delete()
        messages.success(request,'expertise has been removed')
        return redirect('expertise')
    

class ManageUser(SiteAdminRequiredMixin,View):

    def post(self,request,pk):

        user = get_object_or_404(User,pk=pk)
        if not user.is_superuser:
            if user.is_active == True:

                user.is_active = False
            else:
                user.is_active = True

            user.save()
            messages.info(request,f'{user.first_name} {user.last_name} status has been modified ')
        return redirect(request.META.get('HTTP_REFERER'))



class ListDoctorsAsExpertise(LoginRequiredMixin,View):


    def get(self,request,pk):

        expertise = get_object_or_404(Expertise,pk=pk)
        doctors = expertise.doctorprofile_set.all().order_by('-user')
        count = doctors.count()

        p = Paginator(doctors,4)
        page = self.request.GET.get('page')

        try:
            doctors = p.page(page)
        except PageNotAnInteger:
            doctors = p.page(1)
        except EmptyPage:
            doctors = p.page(p.num_pages)

        context={'doctors':doctors,'count':count}
        return render(request,'main/doctors.html',context)


class ShowDoctorsProfile(LoginRequiredMixin,View):

    def get(self,request,pk):
        doctor = get_object_or_404(DoctorProfile,pk=pk)

        try:
            ratio = DoctorsRatio.objects.filter(doctor=doctor,patient=request.user.patientprofile)
        except:
            ratio = {}
       

        context={'doctor':doctor,'ratio':ratio}
        return render(request,'main/doctor_profile.html',context)
    

class ListAllDoctors(LoginRequiredMixin,View):

    def get(self,request):
        
        doctors = DoctorProfile.objects.all().order_by('-user')
        count = doctors.count()

        p = Paginator(doctors,4)
        page = self.request.GET.get('page')

        try:
            doctors = p.page(page)
        except PageNotAnInteger:
            doctors = p.page(1)
        except EmptyPage:
            doctors = p.page(p.num_pages)

        context={'doctors':doctors,'count':count}
        return render(request,'main/doctors.html',context)
 

class MakeAppointment(PatientRequiredMixin,View):
    
    def get(self,request,pk):
        
        doctor = get_object_or_404(DoctorProfile,pk=pk)
        timetables = DoctorTimeTable.objects.filter(doctor=doctor,occupied=False,archived=False).order_by('-date')
        count = timetables.count()

        p = Paginator(timetables,8)
        page = self.request.GET.get('page')

        try:
            timetables = p.page(page)
        except PageNotAnInteger:
            timetables = p.page(1)
        except EmptyPage:
            timetables = p.page(p.num_pages)

        context = {'timetables':timetables,'doctor':doctor,'count':count}
        return render(request,'main/appointment.html',context)
    
    def post(self,request,pk):

        timetable = get_object_or_404(DoctorTimeTable,pk=pk)
        doctor = timetable.doctor
        patient = request.user.patientprofile
        code = str(uuid.uuid4()).replace('-', '')[:8]


        appointment = Appointment.objects.filter(timetable=timetable,doctor=doctor)

        if appointment:
            messages.error(request,'This timeslot already booked choose another')
            return redirect('appointment',doctor.pk)


        appointment = Appointment.objects.create(timetable=timetable,doctor=doctor,patient=patient,code=code)
        timetable.occupied = True

        entry = f'{patient.user.first_name} {patient.user.last_name} has been booked the appointment'
        
        timetable.save()
        TimetableLog.objects.create(timetable=timetable,entry=entry)
        Notification.objects.create(type="A",note=f'{entry}',user=doctor.user)
        messages.success(request,'You successfully booked the appointment')
        return redirect('appointment',doctor.pk)
    


class ListPatientAppointments(PatientRequiredMixin,View):

    def get(self,request):

        appointments = Appointment.objects.filter(patient=request.user.patientprofile,archived=False).order_by('-timetable')
        context={'appointments':appointments}
        count = appointments.count()


        p = Paginator(appointments,6)
        page = self.request.GET.get('page')

        try:
            appointments = p.page(page)
        except PageNotAnInteger:
            appointments = p.page(1)
        except EmptyPage:
            appointments = p.page(p.num_pages)

        context = {'appointments':appointments,'title':'booked','count':count}
        return render(request,'main/list_patient_appointment.html',context)
    
    
    
class ListPatientArchivedAppointments(PatientRequiredMixin,View):

    def get(self,request):
        appointments = Appointment.objects.filter(patient=request.user.patientprofile,archived=True).order_by('-timetable')
        count = appointments.count()

        p = Paginator(appointments,6)
        page = self.request.GET.get('page')

        try:
            appointments = p.page(page)
        except PageNotAnInteger:
            appointments = p.page(1)
        except EmptyPage:
            appointments = p.page(p.num_pages)

        context = {'appointments':appointments,'title':'archived','count':count}
        return render(request,'main/list_patient_appointment.html',context)
    

class CancelPatientAppointment(PatientRequiredMixin,View):

    def post(self,request,pk):

        appointment = get_object_or_404(Appointment,pk=pk)

        if appointment.patient != request.user.patientprofile:
            return redirect('forbidden')

        timetable = appointment.timetable
        timetable.occupied = False
        timetable.save()
        

        entry=f'{appointment.patient.user.first_name} {appointment.patient.user.last_name} cancelled the appointment'
        TimetableLog.objects.create(timetable=timetable,entry=entry)
        Notification.objects.create(type="A",note=f'{entry}',user=appointment.doctor.user)

        appointment.delete()
        messages.success(request,f'You removed the appointment with {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}')
        return redirect('list_patient_appointment')
    

class ShowPatientProfile(DoctorOrAdminRequiredMixin,View):

    def get(self,request,pk):

        profile = get_object_or_404(PatientProfile,pk=pk)
        context={'profile':profile}
        return render(request,'main/patient_profile.html',context)
    

class ListPatients(DoctorOrAdminRequiredMixin,View):

    def get(self,request):

        patients = PatientProfile.objects.all().order_by('-user')
        count = patients.count()

        p = Paginator(patients,8)
        page = self.request.GET.get('page')

        try:
            patients = p.page(page)
        except PageNotAnInteger:
            patients = p.page(1)
        except EmptyPage:
            patients = p.page(p.num_pages)

        context={'patients':patients,'count':count}
        return render(request,'main/list_patients.html',context)


class PatientInformation(DoctorRequiredMixin,View):

    def get(self,request,pk):

        patient = get_object_or_404(PatientProfile,pk=pk)
        try:
            information = patient.patienthealtinformation
        except:
            information = PatientHealtInformation.objects.create(patient=patient) 

        form = PatientInformationForm(instance=information)
        context = {'form':form,'patient':patient}
        return render(request,'main/patient_information.html',context)
    
    def post(self,request,pk):

        patient = get_object_or_404(PatientProfile,pk=pk)
        information =  patient.patienthealtinformation

        form = PatientInformationForm(request.POST,instance=information)
        if form.is_valid():
            data = form.save(commit=False)
            data.patient = patient
            data.save()
            messages.success(request,'Information updated')
        else:
            for error in list(form.error.values()):
                messages.error(request,error)
        return redirect('patient_profile',patient.pk)
    

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):

    form_class = ResetPasswordForm
    template_name = 'settings/password_reset.html'
    email_template_name = 'settings/password_reset_email.html'
    subject_template_name = 'settings/password_reset_subject.txt'

    success_message = "We sent email for you with instructions to change your password." \
                      " if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    
    success_url = reverse_lazy('dashboard')


    def form_invalid(self, form):
        
        for key, error in list(form.errors.items()):

                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(self.request, "You must pass the reCAPTCHA test")
                    continue
                messages.error(self.request, error)
        return redirect('password_reset')
    

class ChangePasswordView(LoginRequiredMixin,SuccessMessageMixin,PasswordChangeView):

    template_name = 'main/change_password.html'
    form_class = ChangePasswordForm

    def get_success_message(self, cleaned_data):
        return "Your password has been changed"
    
    def get_success_url(self):
        return reverse_lazy('update_profile')
    
    def form_invalid(self, form) -> HttpResponse:
        return super().form_invalid(form)
        


class CalendarView(DoctorRequiredMixin,ListView):
    model = DoctorTimeTable
    template_name = 'main/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('day', None))
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(self.request,withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context
    

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return date.today()
    
def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month



class Search(LoginRequiredMixin,View):

    def get(self,request):

        search = request.GET.get('search',"")
        
        if search:

            hospital = DoctorHospitalInfo.objects.filter(Q(name__icontains=search)|Q(city__icontains=search)|Q(description__icontains=search))
            doctor = DoctorProfile.objects.filter(Q(user__first_name__icontains=search)|Q(user__last_name__icontains=search)|Q(bio__icontains=search))
            search_repo = chain(hospital,doctor)
            list_repo = list(search_repo)
            count = len(list_repo)
        
        else:
            messages.info(request,'Empty search')
            return redirect(request.META.get('HTTP_REFERER'))

        p = Paginator(list_repo,4)
        page = self.request.GET.get('page')

        try:
            list_repo = p.page(page)
        except PageNotAnInteger:
            list_repo = p.page(1)
        except EmptyPage:
            list_repo = p.page(p.num_pages)
            

        context={'search_repo':list_repo,'count':count}
        return render(request,'main/search.html',context)
    

class SendMessage(LoginRequiredMixin,View):

    def get(self,request,pk):

        sender = request.user
        receiver = get_object_or_404(User,pk=pk)
        if sender == receiver:
            return redirect('forbidden')

        messages = Message.objects.filter(Q(receiver=receiver,sender=sender)|Q(receiver=sender,sender=receiver)).order_by('-date')
        form = MessageForm()
        replyform = ReplyForm()

        p = Paginator(messages,4)
        page = self.request.GET.get('page')

        try:
            messages = p.page(page)
        except PageNotAnInteger:
            messages = p.page(1)
        except EmptyPage:
            messages = p.page(p.num_pages)
        
        
        
        context = {'form':form,'receiver':receiver,'messages':messages,'replyform':replyform}
        return render(request,'main/user_messages.html',context)
    
    def post(self,request,pk):

        receiver = get_object_or_404(User,pk=pk)
        sender = request.user
        form = MessageForm(request.POST)
       

        if form.is_valid():
            data = form.save(commit=False)
            data.sender = sender
            data.receiver = receiver
            data.save()
                  
        return redirect('send_message',pk)
    

class SendReplyMessage(LoginRequiredMixin,View):

    def post(self,request,pk):

        message = get_object_or_404(Message,pk=pk)

        replyform = ReplyForm(request.POST)

        if replyform.is_valid():
            data = replyform.save(commit=False)
            data.message = message
            data.sender = request.user
            data.receiver = message.sender   
            data.save()
        return redirect(request.META.get('HTTP_REFERER'))
    

class DeleteMessage(LoginRequiredMixin,View):

    def post(self,request,pk):
        message = get_object_or_404(Message,pk=pk)
        if message.sender == request.user:
           
            message.delete()  
            return redirect(request.META.get('HTTP_REFERER'))
                       
        else:
            return redirect('forbidden')
        
class ModifyMessage(LoginRequiredMixin,View):

    def get(self,request,pk):
        message = get_object_or_404(Message,pk=pk)
        if message.sender == request.user:
            form = MessageForm(instance=message)
            context={'form':form}
            return render(request,'main/modify_message.html',context)

        else:
            return redirect('forbidden')
        
    def post(self,request,pk):

        message = get_object_or_404(Message,pk=pk)
        if message.sender == request.user:
            form = MessageForm(request.POST,instance=message)
            if form.is_valid():
                form.save()
                return redirect('send_message',message.receiver.pk)
            
        else:
            return redirect('forbidden')
        

class ModifyReply(LoginRequiredMixin,View):

    def get(self,request,pk):
        reply = get_object_or_404(ReplyMessage,pk=pk)
        
        if reply.sender == request.user:
            form = ReplyForm(instance=reply)
            context={'form':form}
            return render(request,'main/modify_message.html',context)

        else:
            return redirect('forbidden')
        
    def post(self,request,pk):

        reply = get_object_or_404(ReplyMessage,pk=pk)
        if reply.sender == request.user:
            form = ReplyForm(request.POST,instance=reply)
            if form.is_valid():
                form.save()
                if reply.message.receiver == request.user:
                    return redirect('send_message',reply.message.sender.pk)
                else:
                    return redirect('send_message',reply.message.receiver.pk)

        else:
            return redirect('forbidden')


     
class DeleteReply(LoginRequiredMixin,View):

    def post(self,request,pk):
        reply = get_object_or_404(ReplyMessage,pk=pk)
        if reply.sender == request.user:     
            reply.delete() 
            return redirect(request.META.get('HTTP_REFERER'))
                       
        else:
            return redirect('forbidden')
    

class ReadNotes(LoginRequiredMixin,View):

    def get(self,request):
        notes = Notification.objects.filter(user=request.user,read=False)

        context={'notes':notes}
        return render(request,'main/notes.html',context)
    

class SetNotesToReaded(LoginRequiredMixin,View):

    def post(self,request):
        
        note_all = request.POST.get('note_all')
        note_id = request.POST.get('note_id')

        if note_id:        
            note = get_object_or_404(Notification,pk=note_id)
            if note.user == request.user:
                note.read = True
                note.save()
                messages.success(request,'Note has been set to readed')

        if note_all:

            notes = Notification.objects.filter(user=request.user,read=False)
            
            
            for note in notes:
                note.read = True
                note.save()
            messages.success(request,'All note set to readed')

        return redirect('read_notes')
    

class SendStarRating(PatientRequiredMixin,View):

    def post(self,request,pk):

        doctor = get_object_or_404(DoctorProfile,pk=pk)
        patient = request.user.patientprofile
        rating = DoctorsRatio.objects.filter(doctor=doctor,patient=patient)

        if not rating:
            
            star = self.request.POST.get('star')
            if star:
                rate_range, created = DoctorsRatio.objects.get_or_create(doctor=doctor,patient=patient,star_rating=star)
            
                if  created:
                    messages.success(self.request,'Your rating has been saved')
            else:
                messages.error(request,'You must select start rating')
                
        return redirect('show_doctor_profile',doctor.pk)
    


class HospitalStarRating(PatientRequiredMixin,View):

    def post(self,request,pk):

        hospital = get_object_or_404(DoctorHospitalInfo,pk=pk)
        patient = request.user.patientprofile
        rating = HospitalRatio.objects.filter(hospital=hospital,patient=patient)

        if not rating:
            
            star = self.request.POST.get('star')
            if star:
                rate_range, created = HospitalRatio.objects.get_or_create(hospital=hospital,patient=patient,star_rating=star)
            
                if  created:
                    messages.success(self.request,'Your rating has been saved')
            else:
                messages.error(request,'You must select start rating')
                
        return redirect('hospital_detail',hospital.pk)
    
      
class ActiveTimetable_Chart(DoctorRequiredMixin,View):

    def get(self,request):
        free = DoctorTimeTable.objects.filter(occupied=False,doctor=request.user.doctorprofile,archived=False).count()
        ocuppied = DoctorTimeTable.objects.filter(occupied=True,doctor=request.user.doctorprofile,archived=False).count()
 
        data = [free,ocuppied]
        labels = ['FREE','OCUPPIED']
    
        return JsonResponse(data={
            'labels': labels,
            'data': data,})


class TimeTableStatistic(DoctorRequiredMixin,View):

    def get(self,request):

        appointment = Appointment.objects.filter(doctor=request.user.doctorprofile)
        curr_month = datetime.now().strftime('%m')
        curr_year = datetime.now().year
        months = {  
            'January':'01',
            'February':'02',
            'March':'03',
            'April':'04',
            'May':'05',
            'June':'06',
            'July':'07',
            'August':'08',
            'September':'09',
            'October':'10',
            'November':'11',
            'December':'12'
            }

        labels=[]
        data=[]
        for key,value in months.items():
            appointment_count = appointment.filter(timetable__date__year=curr_year,timetable__date__month=value).count()
            labels.append(key)
            data.append(appointment_count)
            
          
            if curr_month == value:
                break
          


        return JsonResponse(data={
            'labels': labels,
            'data': data,})
    


class DoctorExpertiseChart(PatientRequiredMixin,View):

    def get(self,request):

        labels=[]
        data = []
        colors= []
        expertises = Expertise.objects.all()
        for expertise in expertises:
            doctors_num = expertise.doctorprofile_set.count()
            if doctors_num > 0:
                labels.append(expertise.name)
                data.append(doctors_num)
                colors.append(expertise.chart_color)
              
        return JsonResponse(data={
            'labels': labels,
            'data': data,
            'colors':colors,
            })


class DoctorAppointmentChart(PatientRequiredMixin,View):

    def get(self,request):
        
        labels = []
        data = [] 
        colors = []
        doctors = DoctorProfile.objects.all()
        for doctor in doctors:
            labels.append(f'{doctor.user.first_name} {doctor.user.last_name}')
            appointments = Appointment.objects.filter(doctor=doctor).count()
            data.append(appointments)
        
        return JsonResponse(data={
            'labels': labels,
            'data': data,
            })
        

class UserJoinedStatistic(SiteAdminRequiredMixin,View):

    def get(self,request):

        users = User.objects.all()
        curr_month = datetime.now().strftime('%m')
        curr_year = datetime.now().year
        months = {  
            'January':'01',
            'February':'02',
            'March':'03',
            'April':'04',
            'May':'05',
            'June':'06',
            'July':'07',
            'August':'08',
            'September':'09',
            'October':'10',
            'November':'11',
            'December':'12'
            }

        labels=[]
        data=[]
        for key,value in months.items():
            user_count = User.objects.filter(date_joined__year=curr_year,date_joined__month=value).count()
            labels.append(key)
            data.append(user_count)
            
          
            if curr_month == value:
                break
          
      
        return JsonResponse(data={
            'labels': labels,
            'data': data,})
    

class UserLoginStatistic(SiteAdminRequiredMixin,View):

     def get(self,request):
        
        labels = []
        data = [] 
        users = User.objects.all()
        for user in users:
            labels.append(f'{user.first_name} {user.last_name}')
            try:
                logins = LoginUpdate.objects.get(action_user=user)
                data.append(logins.login_count)
            except:
                data.append('0')

        
       
        return JsonResponse(data={
            'labels': labels,
            'data': data,
            })


               
class ForbiddenAccess(View):

    def get(self,request):

        return render(request,'main/forbidden.html')

