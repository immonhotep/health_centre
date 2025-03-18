from django import forms

from .models import User,AdminProfile, DoctorProfile, PatientProfile,Expertise,DoctorHospitalInfo,DoctorTimeTable, \
    PatientHealtInformation,Message,ReplyMessage,Notification,TwoFactorAuth

from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordResetForm,PasswordChangeForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from bootstrap_datepicker_plus.widgets import DatePickerInput,TimePickerInput
from colorfield.fields import ColorWidget





class UserRegisterForm(UserCreationForm):

    class Meta:

        model = User
        fields =('type','username','first_name','last_name','email','password1','password2')

    USER_TYPE=[
        ('D','Doctor'),
        ('P','Patient'),
    ]


    type = forms.ChoiceField(
        
        choices=USER_TYPE,
        widget=forms.Select(attrs={
         
            'class':'form-select form-control fw-bolder my-1'
            
        })

    )

    first_name = forms.CharField(label="First name",widget=forms.TextInput(attrs={

        "placeholder":"Enter your first name",
        "class":"form-control  my-1"
    }))

    last_name = forms.CharField(label="Last name",widget=forms.TextInput(attrs={

        "placeholder":"Enter your last name",
        "class":"form-control  my-1"
    }))



    email = forms.CharField(label="Email",widget=forms.EmailInput(attrs={

    "placeholder":"Enter your Email",
    "class":"form-control my-1"
    }))

    username = forms.CharField(label="Username",widget=forms.TextInput(attrs={

        "placeholder":"Enter your Username",
        "class":"form-control  my-1"
    }))

    password1 = forms.CharField(label="Password",widget=forms.PasswordInput(attrs={

        "placeholder":"Enter your password",
        "class":"form-control my-1"
    }))

    password2 = forms.CharField(label="Password confirmation",widget=forms.PasswordInput(attrs={

        "placeholder":"Repeat your password",
        "class":"form-control  my-1"
    }))

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())




class CreateAdminForm(UserCreationForm):

    class Meta:
        model = User
        fields =('username','first_name','last_name','email','password1','password2')

    first_name = forms.CharField(label="First name",widget=forms.TextInput(attrs={

        "placeholder":"Enter  first name",
        "class":"form-control  my-1"
    }))

    last_name = forms.CharField(label="Last name",widget=forms.TextInput(attrs={

        "placeholder":"Enter last name",
        "class":"form-control  my-1"
    }))

    email = forms.CharField(label="Email",widget=forms.EmailInput(attrs={

    "placeholder":"Enter Email",
    "class":"form-control my-1"
    }))

    username = forms.CharField(label="Username",widget=forms.TextInput(attrs={

        "placeholder":"Enter Username",
        "class":"form-control  my-1"
    }))

    password1 = forms.CharField(label="Password",widget=forms.PasswordInput(attrs={

        "placeholder":"Enter password",
        "class":"form-control my-1"
    }))

    password2 = forms.CharField(label="Password confirmation",widget=forms.PasswordInput(attrs={

        "placeholder":"Repeat password",
        "class":"form-control  my-1"
    }))





class UserLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
    
    username = forms.CharField(widget=forms.TextInput(
    attrs={'class':'form-control text-primary','placeholder':'Enter your email, or username'}),
    label="Email or Username")
        
    password = forms.CharField(widget=forms.PasswordInput(
    attrs={'class':'form-control text-primary', 'placeholder':'Password'}))

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

  
class TwoFactorForm(forms.ModelForm):

    class Meta:
        model = TwoFactorAuth

        fields = ('code',)

    code = forms.CharField(label="2FA authentication code",required=True,max_length=8,widget=forms.TextInput(attrs={

        "placeholder":"Enter your code",
        "class":"form-control form-control-sm my-1"
    }))

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username','first_name','last_name','email')

    username = forms.CharField(label="",widget=forms.TextInput(attrs={

        "placeholder":"Enter your username",
        "class":"form-control form-control-sm my-1"
    }))

    first_name = forms.CharField(label="",widget=forms.TextInput(attrs={

        "placeholder":"Enter your first name",
        "class":"form-control form-control-sm my-1"
    }))

    last_name = forms.CharField(label="",widget=forms.TextInput(attrs={

        "placeholder":"Enter your first name",
        "class":"form-control form-control-sm my-1"
    }))

    email = forms.CharField(label="",widget=forms.EmailInput(attrs={

    "placeholder":"Enter your Email",
    "class":"form-control form-control-sm py-1"
    }))

    


class DoctorProfileForm(forms.ModelForm):

    class Meta:

        model = DoctorProfile
        fields = ('image','bio','phone','expertise','hospital')



    expertise = forms.ModelMultipleChoiceField(
        queryset=Expertise.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={

         'class':'my-2 py-1'        
        })
    )


    phone = forms.CharField(label="",widget=forms.TextInput(attrs={

        "placeholder":"Enter your phone number",
        "class":"form-control form-control my-1"
    }),required=True)

    hospital = forms.ModelChoiceField(queryset=DoctorHospitalInfo.objects.all(),widget=forms.Select(attrs={
          'class':'form-select form-control fw-bolder my-1'
     }),required=False)


class PatientProfileForm(forms.ModelForm):

    class Meta:

        model = PatientProfile
        fields = ('image','age','gender','phone','city','address')

    GENDER=[
        ('M','Male'),
        ('F','Female'),
    ]


    gender = forms.ChoiceField(
        
        choices=GENDER,
        widget=forms.Select(attrs={
         
            'class':'form-select form-control fw-bolder my-1'
            
        })

    )

    phone = forms.CharField(label="",widget=forms.TextInput(attrs={

        "placeholder":"Enter your phone number",
        "class":"form-control  my-1"

    }))

    age = forms.IntegerField(label="Age",widget=forms.NumberInput(attrs={
        'placeholder': '0',
        'class':'form-control my-1'
    }))

    city = forms.CharField(label="",widget=forms.TextInput(attrs={

        "placeholder":"Enter your city",
        "class":"form-control my-1"

    }))
    
    address = forms.CharField(label="",widget=forms.TextInput(attrs={

        "placeholder":"Enter your address",
        "class":"form-control  my-1"

    }))

    


class AdminForm(forms.ModelForm):

    class Meta:
        model = AdminProfile
        fields=('image','bio','phone',)

   

    phone = forms.CharField(label="",widget=forms.TextInput(attrs={

        "placeholder":"Enter your phone number",
        "class":"form-control my-1"

    }))
    

class HospitalForm(forms.ModelForm):

    class Meta:
        model = DoctorHospitalInfo
        fields = ('name','city','address','phone','description','image')


    name = forms.CharField(widget=forms.TextInput(attrs={
            'placeholder':'Enter hospital name',
            'class':'form-control my-1'
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={
            'placeholder':'Enter city name',
            'class':'form-control my-1'
    }))
    address = forms.CharField(widget=forms.TextInput(attrs={
            'placeholder':'Enter address',
            'class':'form-control my-1'
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={
            'placeholder':'Enter phone number',
            'class':'form-control my-1'
    }))



    
class DoctorTimeTableForm(forms.ModelForm):

    class Meta:
        model = DoctorTimeTable
        fields = ('date','start_time','end_time')

    date = forms.DateField(widget=DatePickerInput(attrs={
        'class':'form-control '
    }))

    start_time = forms.TimeField(widget=TimePickerInput(attrs={
        'class':'form-control',
              
    }))
    end_time = forms.TimeField(widget=TimePickerInput(attrs={
        'class':'form-control',  
    }))



class ExpertiseForm(forms.ModelForm):

    class Meta:
        model = Expertise
        fields = ('name','description','chart_color')

    name = forms.CharField(widget=forms.TextInput(attrs={

        'class':'form-control',
        'placeholder':'Enter expertise name'

    }))

    chart_color = forms.CharField(label="Select chart color",required=False,widget=ColorWidget())

    


class PatientInformationForm(forms.ModelForm):

    class Meta:
        model = PatientHealtInformation
        fields =('height','weight','blood_type','known_sickness','medicines','surgeries')


    BLOOD=[

        ('A+', 'A+'),
        ('B+', 'B+'),
        ('AB+','AB+'),
        ('0+','0+'),
        ('A-', 'A-'),
        ('B-', 'B-'),
        ('AB-','AB-'),
        ('0-','0-'),

    ]


    blood_type = forms.ChoiceField(
        
        choices=BLOOD,
        widget=forms.Select(attrs={
         
            'class':'form-select form-control fw-bolder my-1'
            
        })

    )

    height = forms.IntegerField(label="height",widget=forms.NumberInput(attrs={
        'placeholder': '0',
        'class':'form-control my-1'
    }))
    
    weight = forms.IntegerField(label="weight",widget=forms.NumberInput(attrs={
        'placeholder': '0',
        'class':'form-control my-1'
    }))





class ResetPasswordForm(PasswordResetForm):

    def __init__(self,*args,**kwargs):
        super(ResetPasswordForm,self).__init__(*args,**kwargs)


    email = forms.CharField(label="",widget=forms.EmailInput(attrs={

        'placeholder':'Enter your email address',
        'class':'form-control my-3'

    }))

    captcha= ReCaptchaField(label="",widget=ReCaptchaV2Checkbox(
       
    ))


class ChangePasswordForm(PasswordChangeForm):

    old_password = forms.CharField(label="Old password",widget=forms.PasswordInput(attrs={
       'placeholder':'Enter your old password',
       'class':'form-control my-1' 
    }))

    new_password1 = forms.CharField(label="New password",widget=forms.PasswordInput(attrs={
       'placeholder':'Enter your new password',
       'class':'form-control my-1' 
    }))

    new_password2 = forms.CharField(label="Retype password",widget=forms.PasswordInput(attrs={
       'placeholder':'Repeat new password',
       'class':'form-control my-1' 
    }))




class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('body',)

    
   
class ReplyForm(forms.ModelForm):

    class Meta:
        model = ReplyMessage
        fields = ('reply_body',)



class NotificationForm(forms.ModelForm):

    class Meta:
        model = Notification
        fields=('read',)

        read = forms.BooleanField(label='Readed',required=False,widget=forms.CheckboxInput(attrs={
        
    }))
    
