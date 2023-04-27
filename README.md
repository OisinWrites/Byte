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
![example-site-mobile](static/images/model-site-mobile-min.jpg)
![example-site-midscreen-1](static/images/model-site-midscreen-min.jpg)
![example-site-midscreen-2](static/images/model-site-midscreen2-min.jpg)
![example-site-desktop](static/images/model-site-desktop-min.jpg)
Wireframes for project mock-up
![wireframe-mobile](static/images/mobile-wireframe-min.jpg)
![wireframe-desktop](static/images/desktop-wireframe-min.jpg)

Logic

Booking logic Flowchart
![booking-logic-flowchart](static/images/booking-logic-flowchart.jpg)

Plans for Models
![model-plans](static/images/model-plans.jpg)

Testing and Errors