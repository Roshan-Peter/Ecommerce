from django.shortcuts import redirect
from ECom.models import AdminUsers, Users


def loginCheck(username, password, request):
    try:
        user = AdminUsers.objects.get(username=username)
        if user.check_password(password):
            request.session['user_id'] = user.id
            request.session['user_username'] = username
            request.session['account'] = "priority"
            return "admin"
        else:
            return "Authentication failed"
    except AdminUsers.DoesNotExist:
        try:
            user = Users.objects.get(username=username)
            if user.check_password(password):
                request.session['user_id'] = user.id
                request.session['user_username'] = username
                request.session['account'] = "normal"
                return "user"
            else:
                return "Authentication failed"
        except AdminUsers.DoesNotExist:
            return "Authentication failed"