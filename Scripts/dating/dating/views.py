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
from django.shortcuts import render
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Local imports
from dating.models import User

# Third Party Imports

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
        MAX_ATTEMPTS = 3

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
            user = User.get_from_email(nick)
        else:
            user = User.get_from_nick(nick)

        if user is None:
            error = "Unable to find a user with that name and password."
            return render(request, "login.html", {"error": error,
                                                  "help": True})

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
            return render(request, "login.html", {"error": error,
                                                  "help": True})

        user = User.login(user.nick, password)
        if user is None:
            login_attempts += 1
            request.session["login_attempts"] = login_attempts
            error = "Unable to find a user with that name and password."
            return render(request, "login.html", {"error": error,
                                                  "help": True})
        # Save the nickname in the session
        request.session["nick"] = user.nick
        # Rest the login attempts and limit on logging in
        request.session["login_attempts"] = 0
        request.session["can_login_time"] = None

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
        raw_password = request.POST["password"] if "password" in request.POST else ""
        gender = request.POST["gender"] if "gender" in request.POST else ""
        partner = request.POST["partner"] if "partner" in request.POST else ""

        data = {"nick": nick, "first_name": first_name, "last_name": last_name, "email": email, "gender": gender,
                "partner": partner}

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
        if partner is None or partner == "":
            error = "Please select what partner(s) you're interested in."
            data["error"] = error
            return render(request, "signup.html", data)

        orientation = ""
        if partner == "both":
            orientation = "bisexual"
        elif (gender == "male" and partner == "women") or (gender == "female" and partner == "men"):
            orientation = "straight"
        else:
            orientation = "gay"

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