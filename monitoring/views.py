from collections import defaultdict

from django.shortcuts import render

from .models import Logins, Users, Servers, UserEmails, UserPhones


def index(request):
    users = Users.objects.all()
    user_emails = UserEmails.objects.all()
    user_phones = UserPhones.objects.all()
    user_info = defaultdict(dict)
    for user in users:
        user_info[user.user]['name'] = user.name
        user_info[user.user]['email'] = ', '.join([e.email for e in user_emails
                                                   if e.user == user])
        user_info[user.user]['phone'] = ', '.join([p.phone for p in user_phones
                                                   if p.user == user])
    servers = Servers.objects.all()
    server_logins = []
    for server in sorted(servers, key=lambda x: x.name):
        server_info = {'ip': server.ip, 'name': server.name}
        login_info = []
        for user_object in sorted(users, key=lambda x: x.user):
            user = user_object.user
            try:
                login_object = Logins.objects.filter(
                    user=user, server=server.ip).latest('datetime')
            except Logins.DoesNotExist:
                continue
            if login_object:
                login_info.append(
                    {'user': user, 'name': user_info[user]['name'],
                     'datetime': login_object.datetime.replace('T', ' '),
                     'email': user_info[user]['email'],
                     'phone': user_info[user]['phone']})
        server_logins.append({'server': server_info, 'logins': login_info})
    context = {'logins': server_logins}
    return render(request, 'server_logins.html', context)
