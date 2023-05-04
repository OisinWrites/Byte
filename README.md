Project set-up

    cmnd:  django-admin startproject 'project name' .

    Adding app for bookings
        cmnd:   python3 manage.py startapp 'app name'
        Register app name under installed_apps in settings.py

    Allauth set up
       cmnd: pip3 install allauth
        Add lines 
                    # `allauth` needs this from django
                    'django.template.context_processors.request',
        under templates in settings.py
        Add lines
                    'django.contrib.sites',

                    'allauth',
                    'allauth.account',
                    'allauth.socialaccount',
        under installed_apps in settings.py

        Create section in settings above templates
                    AUTHENTICATION_BACKENDS = [
                    # Needed to login by username in Django admin, regardless of `allauth`
                    'django.contrib.auth.backends.ModelBackend',

                    # `allauth` specific authentication methods, such as login by e-mail
                    'allauth.account.auth_backends.AuthenticationBackend',
                    ]
        Under installed apps
                    SITE_ID = 1
        In urls.py
                    from django.urls import path, include
                    from django.conf import settings


                    urlpatterns = [
                        path('accounts/', include('allauth.urls')),
                    ]
        
        allauth customisation

    To copy and paste folders and files from allauth site-packages first determine python version installed using cmnd: python --version In this case python3 3.8
    Create a folder, templates, and subfolder, allauth, from the project level directory
    Then run cmnd: 
    cp -r ../.pip-modules/lib/python3.8/site-packages/allauth/templates/* ./templates/allauth/

    Delete openid and tests folders, as unneeded for this project, deleting will revert use to site_packages templates for same.



UX/UI

Example sites for restaurant home pages
![example-site-mobile](static/media/model-site-mobile-min.jpg)
![example-site-midscreen-1](static/media/model-site-midscreen-min.jpg)
![example-site-midscreen-2](static/media/model-site-midscreen2-min.jpg)
![example-site-desktop](static/media/model-site-desktop-min.jpg)
Wireframes for project mock-up
![wireframe-mobile](static/media/mobile-wireframe-min.jpg)
![wireframe-desktop](static/media/desktop-wireframe-min.jpg)

Logic

Booking logic Flowchart
![booking-logic-flowchart](static/media/booking-logic-flowchart.jpg)

Plans for Models
![model-plans](static/media/model-plans.jpg)

Testing and Errors

    1
    Issue: Changes made to allauth html files take no effect on rendered pages in development server
    Resolve: Included the following lines in project settings:
        "TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')"
        "TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [TEMPLATES_DIR],
                ..."

    2
    Issue: Can't render home view. Attempting to run dev server from terminal results in: AttributeError: module 'home.views' has no attribute 'index'
    Resolve: Apps were not registered in project settings. Additional changes to settings made, including targeting media and static. Homepage functional.

    3.
    Issue: Bookings toggle the table model boolean of availability to a constant false. However, we only want this toggled for the time and day of a booking.
    Resolve: Create a new model to better handle identifying available times.

    4.
    Issue: Form only accepts party sizes that match the table size. We want a party of three to be assigned to a table of 4, but a party of 2 assigned to a table of 2 before a 4.
    Resolve: View now searches for tables with availability that have an occupancy greater or equal to the party size, and searches for the smallest possible table first.

    5.
    Issue: A booking can now be edited by a user, however their booking can interfer with a change. Say f a user has a particular booking of 4 people on a day. And all tables are reserved, but the user wants to amend their booking to three people the view tells them there is no table available, even though the change can be made on the table they already booked.

    6.
    Issue: Cancel anchor not activation view, or view not working.
    Resolve: Firstly, the url was not confirgured correctly, sharing, and therefore overridden by the edit url.
    Additionally, on successfuly deletion user was brought to an error page because the delete view redirect was sending them to the edit url for the now deleted object. To circumvent this the delete call is added to the bookings page, not edit page, and redirects to itself, which is not dependant on a object/id url.

    7.
    Issue: I'm trying to get the second div in bookings to disappear if there are no bookings for the current user. However it is currently working as only disappearing if there are no existing bookings for any user, i.e. booking in current booking.
    Resolve: Not resolved. The div exists because there are bookings in current bookings, and bookings by all customers exist in that list, not just the current user. To fix this later we would have to create a new list in the view of current users bookings in current_bookings and then run the template with if bookings in current user's bookings.

    8:
    Issue: When a table is edited by its start time it leaves behind the table availability instance, which only collapses with a delete.
    Resolve: The code I've tried is attempting to delete old instances of availability, but I believe its tracking them using the id of the edited booking which has changed from the original booking.
    - The table availability model doesn't take in the booking's id. In fact the booking only gets an id on its instansiation, which naturally is after the table availability instansiation since it is a requirement for the booking to exist. Maybe I can edit the table availability instance after the booking is created.
    - Changed the booking view block for making a table availability object. Table availability object now takes in the whole booking object and generates an attribute 'id_of_booking' from the objects id. The edit view now finds the objects that have that attribute = to its own booking objects id and deletes them before creating a new one. It does this now whether or not the edit involved the start date, and thus warrantd a new time slot in the form of the table availability object.


    env.py content

import os

os.environ.setdefault("SECRET_KEY", "Oisin")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("IP", "0.0.0.0.")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("DEVELOPMENT", "True")
os.environ.setdefault("DB_URL", "sqlite3:///byte")
os.environ.setdefault("ALLOWED_HOSTS", "localhost")
