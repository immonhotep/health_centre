# Health Centre

Simple doctor/patient appointment booking application, backend code written in python, and django framework (mostly custom class based views), frontend made with free boostrap templates, elements and css. Charts made with chart.js

Application reason: only for educational purposes, pratice django python and bootstrap. 

Application able to do the following:
Separate registration, profile, dashboard features for Doctors, and Patients, and for site administrators. Time slot booking system, and simple communication between users.

Basic user functions:

- registration ( with email confirmation)
- login ( both with email and username)
- 2FA login with email confirmation (generating random 8 char code with 5 minutes expiration )
- logout
- password reset ( with login)
- password reset with email confirmation ( for users lost their passwords)
- separate user types have separate profiles, and can update this profile.
- users can list hospitals, and doctors, and site administrators, can search for hospitals, and doctors too.
- every user can send messages to administrators.
- every user got notifications about messages, and replies. Can set to read them.


Functions for Doctors:

- add/update hospital information, and select hospital from profile
- select multiple expertises
- send message to other doctors, patients, and admins.
- Function to publish,delete,update timeslots.
- automatic notifications for patients about the booked timeslots
- View timeslot log
- View free, and archived time slots
- View Calendar and update events witch still not archived from calendar
- List patients, view, update patients health information

Doctor dashboard:
- chart show appointments/months current year 
- chart show free/occupied timeslots
- datatable show doctor's own patients



Functions for patients:

- list expertises and list doctors/expertises
- list doctors, show doctors profile, send messages to doctors and admins
- list doctors free timeslots, book time slot.
- list appointments  and cancel booking
- automatic notifications for doctors about booked timeslot
- list archived appointments
- star rating to rate doctors
- star rating to rate hospitals

Patient dashboard:
- chart show doctors/expertises
- chart show doctors popularity by show doctors/appointment count
- datatable show own doctors

Function for administrators:

- Add, update, delete expertises, (update colors for expertise chart or get random colorsclear)
- List doctors
- list patients
- Activate or suspend user accounts
- Send message to doctors, patients, admins
- Superuser ( site first admin ) can create other admins

Admin dashboard:

- Chart show users login count
- Chart show how many user joined/month current year
- datatable show user information
- filter users ascending,descending by last login 
- filter users ascending,descending by date joined 


Extra functions:

- google reCAPTCHA integration
- Django tinyMCE 
- Django bootsrap datepicker plus
- django-colorfield


INSTALL:

- clone the repository ( git clone https://github.com/immonhotep/health_centre.git )
- Create python virtual environment and activate it ( depends on op system, example on linux: virtualenv venv  and source venv/bin/activate )
- Install the necessary packages and django  ( pip3 install -r requirements.txt )
- Create the database:( python3 manage.py makemigrations and then python3 manage.py migrate )
- Create a superuser ( python3 manage.py createsuperuser )
- Run the application ( python3 manage.py runserver )


IMPORTANT NOTE:

This site use email validated registration, password change, and also 2FA login with email validation (except django normal admin panel)
so for the usage need some kind of mail server at least for the testing, or need modify the settings.py to real email providers port, and credentials

very simple pre-installed method for tesing with fake mail server on localhost port 1025:

aiosmtpd version 1.4.6 installed within the virtual environment with the requirements.txt, so just run in a different terminal (in the same virtual environment) the following command to run fake mailserver:

python -m aiosmtpd -n -l localhost:1025

emails will appear in the terminal




