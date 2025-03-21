from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    path('',DashboardView.as_view(),name='dashboard'),
    path('user_register/',UseregisterView.as_view(),name='register'),
    path('user_login/',UserLoginview.as_view(),name='login'),
    path('user_logout/',UserLogoutview.as_view(),name='logout'),
    path('update_profile/',UpdateProfile.as_view(),name='update_profile'),
    path('update_hospital/',UpdateHospitalInfo.as_view(),name='hospital'),
    path('list_hospitals/',ListAllHospitals.as_view(),name="list_hopitals"),
    path('hospital_detail/<int:pk>/',HospitalDetail.as_view(),name='hospital_detail'),
    path('hospital_rating/<int:pk>/',HospitalStarRating.as_view(),name='hospital_rating'),
    path('timetable/',TimeTable.as_view(),name='timetable'),
    path('timetable_detail/<int:pk>/',TimeTableDetail.as_view(),name='timetable_detail'),
    path('delete_table/<int:pk>/',DeleteTimeTable.as_view(),name='delete_table'),
    path('archived_tables/',ListArchivedTimetables.as_view(),name='archived_tables'),
    path('expertise/',ExpertiseView.as_view(),name='expertise'),
    path('expertise_detail/<int:pk>/',ExpertiseDetailView.as_view(),name='expertise_detail'),
    path('delete_expertise/<int:pk>/',DeleteExpertise.as_view(),name='delete_expertise'),
    path('list_doctors/',ListAllDoctors.as_view(),name='list_doctors'),
    path('list_doctors_per_expertise/<int:pk>/',ListDoctorsAsExpertise.as_view(),name='list_doctors_per_expertise'),
    path('show_doctor_profile/<int:pk>/',ShowDoctorsProfile.as_view(),name='show_doctor_profile'),
    path('send_star_rating<int:pk>/',SendStarRating.as_view(),name='send_star_rating'),
    path('patient_profile/<int:pk>/',ShowPatientProfile.as_view(),name='patient_profile'),
    path('patient_information/<int:pk>/',PatientInformation.as_view(),name='patient_information'),
    path('list_patients/',ListPatients.as_view(),name='list_patients'),
    path('appointment/<int:pk>/',MakeAppointment.as_view(),name='appointment'),
    path('list_patient_appointment/',ListPatientAppointments.as_view(),name='list_patient_appointment'),
    path('list_patient_archived_appointment',ListPatientArchivedAppointments.as_view(),name='list_patient_archived_appointment'),
    path('cancel_appointment/<int:pk>/',CancelPatientAppointment.as_view(),name='cancel_appointment'),
    path('forbidden/',ForbiddenAccess.as_view(),name='forbidden'),
    path('search/',Search.as_view(),name='search'),
    path('send_message/<int:pk>/',SendMessage.as_view(),name='send_message'),
    path('reply_message/<int:pk>/',SendReplyMessage.as_view(),name='reply_message'),
    path('delete_message/<int:pk>/',DeleteMessage.as_view(),name='delete_message'),
    path('delete_reply/<int:pk>/',DeleteReply.as_view(),name='delete_reply'),
    path('modify_message/<int:pk>/',ModifyMessage.as_view(),name='modify_message'),
    path('modify_reply/<int:pk>/',ModifyReply.as_view(),name='modify_reply'),
    path('manage_user/<int:pk>/',ManageUser.as_view(),name='manage_user'),
    path('admin_profile/<int:pk>/',AdminDetail.as_view(),name="admin_profile"),
    path('manage_admin/',ManageAdmins.as_view(),name='manage_admin'),  
    path('read_notes/',ReadNotes.as_view(),name='read_notes'),
    path('set_notes_readed/',SetNotesToReaded.as_view(),name="set_notes_readed"),
    path('password_change/',ChangePasswordView.as_view(),name='change_password'),
    path('timetable_chart/',ActiveTimetable_Chart.as_view(),name="timetable_chart"),
    path('timetable_statistic/',TimeTableStatistic.as_view(),name="statistic_chart"),
    path('expertise_chart/',DoctorExpertiseChart.as_view(),name="expertise_chart"),
    path('appointment_chart/',DoctorAppointmentChart.as_view(),name='appointment_chart'),
    path('user_chart/',UserJoinedStatistic.as_view(),name='user_chart'),
    path('login_chart/',UserLoginStatistic.as_view(),name='login_chart'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='settings/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='settings/password_reset_complete.html'),name='password_reset_complete'),
    path('account_activation/<uidb64>/<token>', views.account_activation, name='account_activation'),
    path('twofactor_login/<uidb64>/',TwoFactorLogin.as_view(), name='twofactor_login'),
    path('calendar/',CalendarView.as_view(), name='calendar'),
]
