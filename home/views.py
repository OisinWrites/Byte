from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


def index(request):
    """ A view to return the index page """
    if request.method == 'POST' and 'superuser_btn' in request.POST:
        if not request.user.is_authenticated:
            # If not authenticated, attempt to sign in as superuser
            superuser = authenticate(username='SuperUser', password='superu8er')
            if superuser is not None:
                login(request, superuser)
                messages.success(request, 'Signed in as superuser.')
            else:
                messages.error(request, 'Failed to sign in as superuser.')
        elif not request.user.is_superuser:
            # If authenticated but not superuser, attempt to sign in as superuser
            superuser = authenticate(username='SuperUser', password='superu8er')
            if superuser is not None:
                login(request, superuser)
                messages.success(request, 'Signed in as superuser.')
            else:
                messages.error(request, 'Failed to sign in as superuser.')
        else:
            logout(request)
            messages.success(request, 'Signed out as superuser.')

    return render(request, 'home/index.html')



def contact(request):
    """ A view to return the contact page """

    return render(request, 'home/contact.html')


def menu(request):
    """ A view to return the menu page """

    return render(request, 'home/menu.html')
