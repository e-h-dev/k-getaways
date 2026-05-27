from .models import Contacts

def contacts(request):
    contacts = Contacts.objects.all()
    current_user_id = request.user.id
    my_contacts = Contacts.objects.filter(send_to=current_user_id)
    message_count = len(my_contacts)
    unread_messages = my_contacts.filter(read=False)
    unread_message_count = len(unread_messages)
    
    context = {
        'contacts': contacts,
        'message_count': message_count,
        'unread_message_count': unread_message_count
        }
    return context