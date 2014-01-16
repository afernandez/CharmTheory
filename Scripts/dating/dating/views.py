'''
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
'''

# Python Imports
import hashlib
import uuid
import binascii
from datetime import datetime, timedelta

# Django Imports
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

# Local imports
from dating.models import User

# Third Party Imports

# Needed by AJAX
from annoying.decorators import ajax_request, render_to
import json


def requires_login(func):
    def inner(request, *args, **kwargs):
        if "nick" in request.session and request.session["nick"] != "":
            return func(request, *args, **kwargs)
        else:
            # First authenticate user
            data = {"next": request.path}
            return render(request, 'login.html', data)
    return inner


def home(request):
    return render(request, "index.html")


def login(request):
    if request.method == "GET":
        next = request.GET.get("next", "")
        data = {"next": next}
        return render(request, "login.html")
    else:
        # If the user is already logged in, process the form so they can log-in as another user.
        nick = request.POST.get("nick", "")
        password = request.POST.get("password", "")
        next = request.POST.get("next", "")
        MAX_ATTEMPTS = 3

        data = {"next": next}
        if nick is None or nick == "":
            error = "Please enter a username or E-mail"
            data["error"] = error
            return render(request, "login.html", data)
        if password is None or password == "":
            error = "Please enter a password"
            data["error"] = error
            return render(request, "login.html", data)

        # Check if the username is an email or nickname
        # If contains "@", find the user with that email.
        # Otherwise, attempt to find that username.
        if "@" in nick:
            user = User.get_from_email(nick)
        else:
            user = User.get_from_nick(nick)

        if user is None:
            error = "Unable to find a user with that name and password."
            data["error"] = error
            data["help"] = True
            return render(request, "login.html", data)

        login_attempts = request.session["login_attempts"] if "login_attempts" in request.session else 0
        can_login_time = request.session["can_login_time"] if "can_login_time" in request.session else None
        if can_login_time:
            can_login_time = datetime.strptime(json.loads(can_login_time), '%Y-%m-%dT%H:%M:%S.%f')

        if login_attempts >= MAX_ATTEMPTS and can_login_time is None:
            # Make the user wait a couple of minutes before they can login
            can_login_time = datetime.utcnow() + timedelta(minutes=1)
            request.session["can_login_time"] = json.dumps(can_login_time, cls=DjangoJSONEncoder)

        if login_attempts >= MAX_ATTEMPTS and can_login_time is not None and datetime.utcnow() < can_login_time:
            error = "Exceeded the number of login attempts. Please wait a minute before trying again."
            data["error"] = error
            data["help"] = True
            return render(request, "login.html", data)

        user = User.login(user.nick, password)
        if user is None:
            login_attempts += 1
            request.session["login_attempts"] = login_attempts
            error = "Unable to find a user with that name and password."
            data["error"] = error
            data["help"] = True
            return render(request, "login.html", data)

        # Save the nickname in the session
        request.session["nick"] = user.nick
        # Rest the login attempts and limit on logging in
        request.session["login_attempts"] = 0
        request.session["can_login_time"] = None

        if next and next != "":
            return redirect(next)

        return render(request, "index.html")


def logout(request):
    # Clear the nickname
    del request.session["nick"]
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
        raw_password = request.POST["password"] if "password" in request.POST else ""
        gender = request.POST["gender"] if "gender" in request.POST else ""
        orientation = request.POST["orientation"] if "orientation" in request.POST else ""

        data = {"nick": nick, "first_name": first_name, "last_name": last_name, "email": email, "gender": gender,
                "orientation": orientation}

        if nick is None or nick == "":
            error = "Please enter a username."
            data["error"] = error
            return render(request, "signup.html", data)
        if first_name is None or first_name == "":
            error = "Please enter a first name."
            data["error"] = error
            return render(request, "signup.html", data)
        if last_name is None or last_name == "":
            error = "Please enter a last name."
            data["error"] = error
            return render(request, "signup.html", data)
        if email is None or email == "":
            error = "Please enter an email."
            data["error"] = error
            return render(request, "signup.html", data)
        if raw_password is None or raw_password == "":
            error = "Please enter a password."
            data["error"] = error
            return render(request, "signup.html", data)
        if gender is None or gender == "":
            error = "Please select a gender."
            data["error"] = error
            return render(request, "signup.html", data)
        if orientation is None or orientation == "":
            error = "Please select an orientation."
            data["error"] = error
            return render(request, "signup.html", data)

        nick, error = User.validate_username(nick)
        if nick == "" and error != "":
            data["error"] = error
            return render(request, "signup.html", data)

        # Check that the username doesn't already exist, the email is valid, and the password meets the requirements.
        try:
            user = User.objects.get(nick=nick)
            error = "That username is already taken, please try another."
            data["error"] = error
            return render(request, "signup.html", data)
        except User.DoesNotExist:
            pass

        try:
            validate_email(email)
        except ValidationError:
            error = "Please enter a valid e-mail."
            data["error"] = error
            return render(request, "signup.html", data)

        try:
            user = User.objects.get(email=email)
            error = "That email is already taken, please try another."
            data["error"] = error
            return render(request, "signup.html", data)
        except User.DoesNotExist:
            pass

        if len(raw_password) < 4:
            error = "Please enter a stronger password."
            data["error"] = error
            return render(request, "signup.html", data)

        salt = uuid.uuid4().hex
        m = hashlib.sha512()
        m.update(raw_password)
        m.update(salt)
        hashed_password = m.hexdigest()
        hashed_password_bin = binascii.a2b_hex(hashed_password)
        salt_bin = binascii.a2b_hex(salt)

        confirmation = uuid.uuid4().hex
        # Create the user
        user = User.create(nick, first_name, last_name, gender, orientation, email, hashed_password_bin, salt_bin,
                           confirmation)

        request.session["nick"] = user.nick
        user.send_confirmation()
        return render(request, "confirmation.html")


def confirmation(request):
    if request.is_ajax():
        nick = request.POST["nick"] if "nick" in request.POST else ""
        last_confirmation_time = None
        error = None
        if nick and nick != "":
            user = User.get_from_nick(nick)
            if user:
                if user.send_confirmation():
                    last_confirmation_time = datetime.utcnow()
                else:
                    error = "Unable to send confirmation"
            else:
                error = "Unable to get user"
        else:
            error = "Unable to get username"
        data = {"last_confirmation_time": last_confirmation_time}
        html = render_to_string("confirmation_ajax.html", data)
        res = {"html": html}
        return HttpResponse(json.dumps(res), mimetype='application/json')

    if request.method == "GET":
        return render(request, "confirmation.html")


def ack_confirmation(request, nick, confirmation):
    user = User.get_from_nick(nick)
    if user:
        confirmed = user.ack_confirmation(confirmation)
        # Redirect to login page
        if confirmed:
            data = {"nick": user.nick}
            return render(request, "login.html", data)
    return render(request, "index.html")


@requires_login
def user(request, nick):
    if nick.lower() == request.session["nick"].lower():
        return redirect("/profile")

    user = User.get_from_nick(nick)
    data = {}
    if user:
        data = {"user": user}
    return render(request, "user.html", data)

@requires_login
def profile_stats(request):
    # This request should only be posting AJAX
    if request.is_ajax():
        user = User.get_from_nick(request.session["nick"])

        relationship = request.POST.get("relationship")
        personality = request.POST.get("personality")
        humor = request.POST.get("humor")
        ethnicity = request.POST.get("ethnicity")
        body = request.POST.get("body")

        user.update_stats(relationship, personality, humor, ethnicity, body)
        # TODO, add more
        data = {}
        if user:
            data = {"user": user}

        html = render_to_string("profile_stats_ajax.html", data)
        res = {"html": html}
        return HttpResponse(json.dumps(res), mimetype='application/json')

    # This code exists as a safety backup in case a GET or POST is ever done
    return redirect("/profile")

@requires_login
def profile(request):
    user = User.get_from_nick(request.session["nick"])
    data = {}
    if user:
        data = {"user": user}
    return render(request, "profile.html", data)