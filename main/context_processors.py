from .models import Notification,User

def  notifications_context(request):
    
    if request.user.is_authenticated:
        user =  request.user
        unread_notes = Notification.objects.filter(user=user,read=False)
        admins = User.objects.filter(is_staff=True)
        
         

    else:
        unread_notes = {}
        admins = {}
  
    return {'unread_notes':unread_notes,'admins':admins}