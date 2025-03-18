from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

class SuperUserRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
  
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):

        return redirect('forbidden')

class SiteAdminRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):

        return redirect('forbidden')


class DoctorOrAdminRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
  
    def test_func(self):
        try:
            if self.request.user.is_staff:
                return self.request.user.is_staff
            if self.request.user.doctorprofile:
                return self.request.user.doctorprofile
                
        except:
            return False
    
    def handle_no_permission(self):

        return redirect('forbidden')


class PatientRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
  
    def test_func(self):

        try:
            self.request.user.patientprofile
            return self.request.user.patientprofile 
        except:
            return False
        
    def handle_no_permission(self):

        return redirect('forbidden')
        

class DoctorRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
  
    def test_func(self):

        try:
            self.request.user.doctorprofile
            return self.request.user.doctorprofile
        except:
            return False
    
    def handle_no_permission(self):

        return redirect('forbidden')