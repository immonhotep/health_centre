from django.contrib import admin
from .models import DoctorProfile, PatientProfile,AdminProfile,Expertise,User,DoctorHospitalInfo,DoctorTimeTable,Appointment,PatientHealtInformation \
    ,TimetableLog,Message,ReplyMessage,Notification,LoginUpdate,DoctorsRatio,HospitalRatio,TwoFactorAuth

admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)
admin.site.register(AdminProfile)
admin.site.register(Expertise)
admin.site.register(User)
admin.site.register(TwoFactorAuth)
admin.site.register(DoctorHospitalInfo)
admin.site.register(DoctorTimeTable)
admin.site.register(Appointment)
admin.site.register(PatientHealtInformation)
admin.site.register(TimetableLog)
admin.site.register(Message)
admin.site.register(ReplyMessage)
admin.site.register(Notification)
admin.site.register(LoginUpdate)
admin.site.register(DoctorsRatio)
admin.site.register(HospitalRatio)



