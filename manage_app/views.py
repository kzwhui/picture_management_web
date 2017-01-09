#encoding=utf8
import json
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from models import *
from forms import *

# Create your views here.
def index(request):
    return render(request, 'manage_app/base.html')

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/hi/')

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False
    user_form = None
    profile_form = None

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save(using="default")

            # Update our variable to tell the template registration was successful.
            registered = True
            return render(request, 'manage_app/login.html', {"status_title" : "登录"})

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors.as_data(), profile_form.errors.as_data()

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
                  'manage_app/register.html',
                  {'registered' : registered,
                   'user_form' : user_form,
                   'profile_form' : profile_form} )

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/hi/')

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = auth.authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                auth.login(request, user)
                return HttpResponseRedirect('/hi/')
            else:
                # An inactive account was used - no logging in!
                return render(request, 'manage_app/login.html', {"status_title" : "请重新登录"})
        else:
            # Bad login details were provided. So we can't log the user in.
            return render(request, 'manage_app/login.html', {"status_title" : "请重新登录"})

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'manage_app/login.html', {"status_title" : "登录"})

@login_required
def logout(request):
    auth.logout(request)
    return render(request, 'manage_app/logout.html')

@login_required
def user_profile(request):
    is_modified = False
    user_form = None
    profile_form = None
    ip_address = request.META['HTTP_X_FORWARDED_FOR'] if request.META.has_key('HTTP_X_FORWARDED_FOR') else request.META['REMOTE_ADDR']

    if request.method == 'POST':
        user_form = UserExtraForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = request.user
            user.email = user_form.cleaned_data['email']
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            profile = UserProfile.objects.using('default').get(user_id=user.id)
            profile.website = profile_form.cleaned_data['website']

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save(using='default')
            #UserProfile.objects.using('default').filter(user_id=user.id)\
            #           .update(website=profile_form.cleaned_data['website'])
            is_modified = True
        else:
            print user_form.errors.as_data(), profile_form.errors.as_data()
    else:
        user_form = UserExtraForm()
        profile_form = UserProfileForm()
        user_form.data['username'] = request.user.username
        user_form.data['email'] = request.user.email
        profile_form.data['website'] = UserProfile.objects.using('default').get(user_id=request.user.id).website

    return render(request,
                  'manage_app/profile.html',
                  {'is_modified' : is_modified,
                   'ip_address' : ip_address,
                   'user_form' : user_form,
                   'profile_form' : profile_form} )
