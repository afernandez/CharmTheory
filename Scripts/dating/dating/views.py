'''
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
'''

# Python Imports
import hashlib
import uuid
import binascii
from datetime import datetime, timedelta, date
import os

# Django Imports
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Local imports
from dating.models import User, UserPhoto

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
        return HttpResponse(json.dumps(res), content_type='application/json')

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
        return HttpResponse(json.dumps(res), content_type='application/json')

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
def profile_main(request):
    # This request should only be posting AJAX
    if request.is_ajax():
        user = User.get_from_nick(request.session["nick"])

        gender = request.POST.get("gender")
        orientation = request.POST.get("orientation")
        city = request.POST.get("city")
        print("%s. Gender: %s, Orientation: %s, City: %s" % (str(datetime.now()), str(gender), str(orientation), str(city)))

        year = request.POST.get("year")
        month = request.POST.get("month")
        day = request.POST.get("day")

        year = int(year) if year and year != "" else 0
        month = int(month) if month and month != "" else 0
        day = int(day) if day and day != "" else 0

        data = {}
        if user:
            user.update_main(gender, orientation, city)

            if year > 0 and month > 0 and day > 0:
                birthday = date(year, month, day)
                user.update_birthday(birthday)

            data = {"user": user}

        data["years"] = User.get_years()
        data["months"] = User.get_months()
        data["days"] = User.get_days()

        html = render_to_string("profile_main_ajax.html", data)
        res = {"html": html}
        return HttpResponse(json.dumps(res), content_type='application/json')

    # This code exists as a safety backup in case a GET or POST is ever done
    return redirect("/profile")

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
        height = request.POST.get("height")
        height = int(height) if height and height != "" else 0
        education = request.POST.get("education")
        college = request.POST.get("college")
        job = request.POST.get("job")
        income = request.POST.get("income")
        income = int(income) if income and income != "" else 0
        income = int(income) if income != "" else 0
        religion = request.POST.get("religion")
        politics = request.POST.get("politics")
        have_kids = request.POST.get("have_kids")
        want_kids = request.POST.get("want_kids")
        drink = request.POST.get("drink")
        smoke = request.POST.get("smoke")
        pet = request.POST.get("pet")

        user.update_stats(relationship, personality, humor, ethnicity, body, height, education,
                          college, job, income, religion, politics, have_kids, want_kids,
                          drink, smoke, pet)

        data = {}
        if user:
            data = {"user": user}

        html = render_to_string("profile_stats_ajax.html", data)
        res = {"html": html}
        return HttpResponse(json.dumps(res), content_type='application/json')

    # This code exists as a safety backup in case a GET or POST is ever done
    return redirect("/profile")

@requires_login
def profile_essay(request):
    # This request should only be posting AJAX
    if request.is_ajax():
        user = User.get_from_nick(request.session["nick"])

        title = request.POST.get("title")
        info = request.POST.get("info")

        data = {}
        if user:
            user.set_essay(title, info)
            data = {"user": user}

        html = render_to_string("profile_essay_ajax.html", data)
        res = {"html": html}
        return HttpResponse(json.dumps(res), content_type='application/json')

    # This code exists as a safety backup in case a GET or POST is ever done
    return redirect("/profile")

@requires_login
def profile(request):
    user = User.get_from_nick(request.session["nick"])
    data = {}
    if user:
        data = {"user": user}

    data["years"] = User.get_years()
    data["months"] = User.get_months()
    data["days"] = User.get_days()
    return render(request, "profile.html", data)

@requires_login
def photos(request):
    user = User.get_from_nick(request.session["nick"])
    data = {}
    if user:
        data = {"user": user}

    print("Viewing photos")
    return render(request, "photos.html", data)

@requires_login
def upload_photo(request):
    data = {}
    if request.method == "POST":
        user = User.get_from_nick(request.session["nick"])

        if user:
            data = {"user": user}
            # TODO, how to show error message
            file = request.FILES['file_path']
            filename = file._get_name()
            if user.get_photo_with_name(filename):
                data["error"] = "A photo with that name already exists."
            else:
                photo, error = user.add_photo(filename, file)
                if photo:
                    data["new_photo"] = filename
                else:
                    data["error"] = error
    return render(request, "photos.html", data)

@requires_login
def delete_photo(request):
    data = {}
    if request.method == "POST":
        user = User.get_from_nick(request.session["nick"])

        if user:
            data = {"user": user}

            filename = request.POST.get("file", "")
            if user.get_photo_with_name(filename):
                deleted = user.delete_photo(filename)
            else:
                data["error"] = "That photo doesn't exist"
    return render(request, "photos.html", data)

@requires_login
def reorder_photo(request):
    # This request should only be posting AJAX
    if request.is_ajax():
        user = User.get_from_nick(request.session["nick"])

        grid_json = request.POST.get("grid")
        data = {}
        if user:
            raw_grid = json.loads(grid_json)
            grid = {}
            for kv in raw_grid:
                # There's javascript code that sets these values
                grid[kv["index"]] = kv["id"]

            i = 0
            for k, v in sorted(grid.items()):
                #k is new index
                #v is the photo name
                UserPhoto.reorder_photo(user, v, i)
                i += 1
            data = {"user": user}

        html = render_to_string("photos_ajax.html", data)
        res = {"html": html}
        return HttpResponse(json.dumps(res), content_type='application/json')

    # This code exists as a safety backup in case a GET or POST is ever done
    return redirect("/photos")


def photo(request, cdn, cache, node, volume, image, size_ext):
    # E.g., http://localhost:8000/photo/a/b/c/01/01/dec2b092a63342d6a55e3810b9908d9f/m.jpeg
    path = "/".join(["", "static", "photo", "node" + node, "volume" + volume, image, size_ext])
    html = '<img src="%s" />' % (path)
    return HttpResponse(html)