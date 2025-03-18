from django.db import models
from django.contrib.auth.models import User

from PIL import Image
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse
from datetime import date
from random import randbytes
from django.contrib.auth.signals import user_logged_in
from django.db.models import F

from django.conf import settings
from tinymce.models import HTMLField
from colorfield.fields import ColorField
from django.db.models import Avg,Count

import datetime
from django.utils import timezone


class User(AbstractUser):


    email = models.EmailField(unique=True)

    USER_TYPE = (

        ('D', 'Doctor'),
        ('P', 'Patient'),
        ('A', 'Admin'),
    )
    type = models.CharField(max_length = 1, choices=USER_TYPE)

    def __str__(self):
        return self.username
    

@receiver(pre_save, sender=User)
def set_admin_pre_save(sender, instance, **kwargs):

    if instance.is_superuser:
        if not instance.type:
            instance.type = "A"


class TwoFactorAuth(models.Model):
    code = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.code}'


@receiver(post_save, sender=TwoFactorAuth)
def handler_function(sender, instance, created, **kwargs):
    if  created:
        instance.expiration = timezone.now() + timezone.timedelta(minutes=5)
        instance.save()



class LoginUpdate(models.Model):
    
    login_count = models.IntegerField(default=0)
    action_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.action_user} login count: {self.login_count}'



@receiver(user_logged_in, sender=User)
def update_user_login(sender, **kwargs):
    user = kwargs.pop('user', None)
    user_login, created = LoginUpdate.objects.get_or_create(action_user=user)
    user_login.login_count = F('login_count') + 1
    user_login.save()
   

class Expertise(models.Model):

    name = models.CharField(max_length=250)
    description = HTMLField(blank=True,default="",max_length=3000)
    chart_color = models.CharField(max_length=7,blank=True,unique=True)

    def __str__(self):

        return self.name

# if admin not select any color get random one
@receiver(pre_save, sender=Expertise)
def expertise_pre_save(sender, instance, *args, **kwargs):
    color = f'#{randbytes(3).hex()}'
    if not instance.chart_color:
        instance.chart_color = color
    


class DoctorHospitalInfo(models.Model):


    name = models.CharField(max_length=200, unique=True)
    city = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    image = models.ImageField(null=True,blank=True, upload_to='images/doctors/hospital')
    description = HTMLField(blank=True,default="",max_length=3000)

  

    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    

    @property
    def averagerate(self):
        review = HospitalRatio.objects.filter(hospital=self).aggregate(average=Avg('star_rating'))
        avg=0
        if review["average"] is not None:
            avg=float(review["average"])
        return avg
    
    @property
    def countrate(self):
        reviews = HospitalRatio.objects.filter(hospital=self).aggregate(count=Count('id'))
        cnt=0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt



class DoctorProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to='images/doctors/avatar')
    bio = HTMLField(blank=True,default="",max_length=3000)
    phone = models.CharField(max_length=20)
    expertise = models.ManyToManyField(Expertise, blank=True)
    hospital = models.ForeignKey(DoctorHospitalInfo,on_delete=models.SET_NULL,blank=True,null=True)
    
    

    def __str__(self):

        return f'{self.user.first_name} {self.user.last_name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)


    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    

    @property
    def averagerate(self):
        review = DoctorsRatio.objects.filter(doctor=self).aggregate(average=Avg('star_rating'))
        avg=0
        if review["average"] is not None:
            avg=float(review["average"])
        return avg
    
    @property
    def countrate(self):
        reviews = DoctorsRatio.objects.filter(doctor=self).aggregate(count=Count('id'))
        cnt=0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt

    
class DoctorTimeTable(models.Model):

    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    occupied = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.doctor}-{self.date}-({self.start_time}-{self.end_time})'


    #to show patient appointment details in calendar
    @property
    def get_html_url(self):
        try:
            appointment = Appointment.objects.get(timetable=self.pk)
        except:
            appointment={}

        url = reverse('timetable_detail', args=(self.id,))
        if appointment:
            return f'<a href="/patient_profile/{appointment.patient.pk}/"><img data-toggle="tooltip" title="{appointment.patient.user.first_name} {appointment.patient.user.last_name}"  class="avatar avatar-lg ms-5 mt-2 border border-4 border-dark" src="{appointment.patient.imageURL}" /></a><a href="{url}">({self.start_time} - {self.end_time})</a>'
        else:
            return f'<a href="{url}">({self.start_time} - {self.end_time})</a>'


class PatientProfile(models.Model):

    
    GENDER = (
         
        ('M', 'Male'),
        ('F', 'Female'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to='images/patient/avatar')
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    age = models.PositiveIntegerField(null=True)
    gender = models.CharField(max_length=1,choices=GENDER,default="M")
   
    def __str__(self):

        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    


class TimetableLog(models.Model):

    date = models.DateTimeField(auto_now_add=True)
    entry = models.TextField(max_length=250)
    timetable = models.ForeignKey(DoctorTimeTable, on_delete=models.CASCADE)
    
    

    def __str__(self):
        return f'{self.date}-{self.entry}'
    

class PatientHealtInformation(models.Model):

    BLOOD = (
         
        ('A+', 'A+'),
        ('B+', 'B+'),
        ('AB+','AB+'),
        ('0+','0+'),
        ('A-', 'A-'),
        ('B-', 'B-'),
        ('AB-','AB-'),
        ('0-','0-'),
    )

    height = models.PositiveIntegerField(default="0")
    weight = models.PositiveIntegerField(default="0")
    blood_type = models.CharField(max_length=3,choices=BLOOD,default="0-")
    known_sickness = HTMLField(blank=True,default="",max_length=3000)
    medicines = HTMLField(blank=True,default="",max_length=3000)
    surgeries = HTMLField(blank=True,default="",max_length=3000)
    patient = models.OneToOneField(PatientProfile,on_delete=models.CASCADE,null=True)

 
class Appointment(models.Model):

    timetable = models.ForeignKey(DoctorTimeTable, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.PROTECT)
    patient = models.ForeignKey(PatientProfile, on_delete=models.PROTECT)
    code = models.CharField(max_length=8, null=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return  f'{self.doctor}-{self.patient}-{self.timetable}-{self.code}'
    

class Message(models.Model):

    sender = models.ForeignKey(User,related_name='sended',on_delete=models.CASCADE)
    receiver = models.ForeignKey(User,related_name='received',on_delete=models.CASCADE)
    body = HTMLField(blank=True,default="",max_length=3000)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender}-{self.receiver}'


@receiver(post_save, sender=Message)
def send_message_notification(sender, instance, created, **kwargs):

    url = settings.ABSOLUTE_URL_BASE

    if created:
        message = instance
        receiver = message.receiver
        sender = message.sender
        type = "M"
        note = f'{sender} sent you a new message: {message.body[:100]}'
        notification = Notification.objects.create(type=type,user=receiver,note=note,link=f'{url}/send_message/{sender.pk}')
        notification.save()



   
class ReplyMessage(models.Model):

    sender = models.ForeignKey(User,related_name='reply_sended',on_delete=models.CASCADE)
    receiver = models.ForeignKey(User,related_name='reply_received',on_delete=models.CASCADE)
    message = models.ForeignKey(Message,related_name='reply_to',on_delete=models.CASCADE)
    reply_body = HTMLField(blank=True,default="",max_length=3000)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'reply to: {self.message}'

 
@receiver(post_save, sender=ReplyMessage)
def send_reply_notification(sender, instance, created, **kwargs):

    url = settings.ABSOLUTE_URL_BASE
    
    if created:
        reply = instance
        receiver = reply.receiver
        sender = reply.sender
        message = reply.message
        reply_body = reply.reply_body
        type = "M"

        if sender != receiver:
            note = f'{sender.first_name} {sender.last_name} sent you a new reply: {reply_body[:100]}'
            notification = Notification.objects.create(type=type,user=receiver,note=note,link=f'{url}/send_message/{sender.pk}')
            
        else:
            note = f'{message.sender.first_name} {message.sender.last_name} sent you a new reply: {reply_body[:100]} '
            notification = Notification.objects.create(type=type,user=message.receiver,note=note,link=f'{url}/send_message/{message.sender.pk}')
            


        notification.save()




class Notification(models.Model):

    TYPE = (
         
        ('M', 'Message'),
        ('A', 'Appointment'),
        ('O','Other'),
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    note = models.CharField(max_length=250)
    type = models.CharField(max_length=1,choices=TYPE,default="O")
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    link = models.URLField(max_length=250,null=True, blank=True)
    

    def __str__(self):
        return f'{self.user}-{self.date}-{self.note}'



class AdminProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to='images/patient/avatar')
    bio = HTMLField(blank=True,default="",max_length=3000)
    phone = models.CharField(max_length=20)


    def __str__(self):

        return self.user.username
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)


    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


@receiver(post_save, sender=User)
def create_profile(sender, instance, **kwargs):

    if instance.is_staff:
        profile, created = AdminProfile.objects.get_or_create(user=instance)
    elif instance.type == "P":
        profile, created = PatientProfile.objects.get_or_create(user=instance)
    elif instance.type == "D":
        profile, created = DoctorProfile.objects.get_or_create(user=instance)




class DoctorsRatio(models.Model):

    doctor = models.ForeignKey(DoctorProfile, related_name="get_ration", on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(PatientProfile, related_name="send_ration", on_delete=models.CASCADE, null=True, blank=True)
    star_rating = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):

        return f'{self.patient.user.last_name}-{self.patient.user.first_name} to - {self.doctor.user.last_name}-{self.doctor.user.first_name}'


class HospitalRatio(models.Model):

    hospital = models.ForeignKey(DoctorHospitalInfo, related_name="hospital_get_ration", on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(PatientProfile, related_name="hospital_send_ration", on_delete=models.CASCADE, null=True, blank=True)
    star_rating = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):

        return f'{self.patient.user.last_name}-{self.patient.user.first_name} to - {self.hospital.name}'



