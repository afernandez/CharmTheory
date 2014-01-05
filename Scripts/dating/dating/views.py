'''
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
'''

from django.http import HttpResponse
from django.shortcuts import render
from dating.models import User
from django.template.loader import render_to_string

# Needed by AJAX
from annoying.decorators import ajax_request, render_to
import json

# Some pages require the user to first login

def home(request):
    return render(request, "index.html")


def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    else:
        # If the user is already logged in, process the form so they can log-in as another user.
        nick = request.POST["nick"] if "nick" in request.POST else ""
        password = request.POST["password"] if "password" in request.POST else ""

        if nick is None or nick == "":
            error = "Please enter a username or E-mail"
            return render(request, "login.html", {"error": error})
        if password is None or password == "":
            error = "Please enter a password"
            return render(request, "login.html", {"error": error})

        # Check if the username is an email or nickname
        # If contains "@", find the user with that email.
        # Otherwise, attempt to find that username.
        if "@" in nick:
            nick = User.get_from_email(nick)
            if nick is None:
                error = "Unable to find a user with that name and password."
                return render(request, "login.html", {"error": error,
                                                      "help": True})

        user = User.login(nick, password)
        if user is None:
            error = "Unable to find a user with that name and password."
            return render(request, "login.html", {"error": error,
                                                  "help": True})

        # Save the nickname in the session
        request.session["nick"] = user.nick
        return render(request, "index.html")


def logout(request):
    # Clear the nickname
    request.session["nick"] = None
    return render(request, "index.html")


def signup(request):
    if request.is_ajax():
        valid_nick = False
        nick = request.POST["nick"] if "nick" in request.POST else ""
        if nick and nick != "":
            try:
                user = User.objects.get(nick=nick)
            except User.DoesNotExist:
                valid_nick = True
        data = {"valid_nick": valid_nick, "nick": nick}
        html = render_to_string("signup_ajax.html", data)
        res = {"html": html}
        return HttpResponse(json.dumps(res), mimetype='application/json')

    if request.method == "GET":
        return render(request, "signup.html")
    else:
        # If the user is already logged in, process the form so they can log-in as another user.
        nick = request.POST["nick"] if "nick" in request.POST else ""
        first_name = request.POST["first_name"] if "first_name" in request.POST else ""
        last_name = request.POST["last_name"] if "last_name" in request.POST else ""
        email = request.POST["email"] if "email" in request.POST else ""
        password = request.POST["password"] if "password" in request.POST else ""
        gender = request.POST["gender"] if "gender" in request.POST else ""

        if nick is None or nick == "":
            error = "Please enter a username."
            return render(request, "signup.html", {"error": error})
        if first_name is None or first_name == "":
            error = "Please enter a first name."
            return render(request, "signup.html", {"error": error})
        if last_name is None or last_name == "":
            error = "Please enter a last name."
            return render(request, "signup.html", {"error": error})
        if email is None or email == "":
            error = "Please enter an email."
            return render(request, "signup.html", {"error": error})
        if password is None or password == "":
            error = "Please enter a password."
            return render(request, "signup.html", {"error": error})
        if gender is None or gender == "":
            error = "Please select a gender."
            return render(request, "signup.html", {"error": error})

        # Check that the username doesn't already exist, the email is valid, and the password meets the requirements.
        try:
            user = User.objects.get(nick=nick)
            error = "That username is already taken, please try another."
            return render(request, "signup.html", {"error": error})
        except User.DoesNotExist:
            pass

        if "@" not in email:
            error = "Please enter a valid e-mail."
            return render(request, "signup.html", {"error": error})

        # TODO
        '''
        try:
            user = User.objects.get(email=email)
            error = "That email is already taken, please try another."
            return render(request, "signup.html", {"error": error})
        except User.DoesNotExist:
            pass
        '''
        if len(password) < 3:
            error = "Please enter a stronger password."
            return render(request, "signup.html", {"error": error})

        # Create the user
        user = User.create(nick, first_name, last_name, gender)

        request.session["nick"] = user.nick
        return render(request, "index.html")

