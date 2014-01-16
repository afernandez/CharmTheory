"""
Django settings for dating project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Python Imports
import hashlib
import binascii
import re
from datetime import datetime

# Django Imports
from django.db import models
from django.conf import settings

# Local Imports

# Third Party Imports


'''
Useful constructs
models.EmailField(blank=True)

Date or Numeric fields require
.DateField(blank=True, null=True)

'''


class User(models.Model):
    id = models.AutoField(primary_key=True)
    nick = models.CharField(max_length=45, unique=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    gender = models.CharField(max_length=45)
    orientation = models.CharField(max_length=45)
    email = models.EmailField(max_length=64)
    password = models.BinaryField()
    salt = models.BinaryField()
    confirmation = models.CharField(max_length=64)
    active = models.SmallIntegerField()
    birthday = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=45)
    state = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    relationship = models.CharField(max_length=45)
    ethnicity = models.CharField(max_length=45)
    body = models.CharField(max_length=45)
    height = models.IntegerField(blank=True, null=True)
    education = models.CharField(max_length=45)
    college = models.CharField(max_length=128)
    religion = models.CharField(max_length=45)
    job = models.CharField(max_length=45)
    income = models.IntegerField(blank=True, null=True)
    humor = models.CharField(max_length=45)
    personality = models.CharField(max_length=45)
    politics = models.CharField(max_length=45)
    diet = models.CharField(max_length=45)
    have_kids = models.CharField(max_length=45)
    want_kids = models.CharField(max_length=45)
    drink = models.CharField(max_length=45)
    smoke = models.CharField(max_length=45)

    class Meta:
         db_table = "user"

    def __unicode__(self):
        return u'%s (%s %s : %s)' % (self.nick, self.first_name, self.last_name, self.email)

    @classmethod
    def create(cls, nick, first_name, last_name, gender, orientation, email, password, salt, confirmation):
        """
        @param password: binary data
        @param salt: binary data
        @param confirmation: suffix of the URL to confirm the user's account
        """
        user = User(nick=nick, first_name=first_name, last_name=last_name, gender=gender, orientation=orientation,
                    email=email, password=password, salt=salt, confirmation=confirmation)
        user.active = 0
        if settings.SKIP_VALIDATION:
            user.active = 1
        user.save()

        return user

    @classmethod
    def get_from_email(cls, email):
        """
        @return: The user with the given email.
        """
        return User.objects.get(email=email)

    @classmethod
    def get_from_nick(cls, nick):
        """
        @return: The user with the given nickname.
        """
        return User.objects.get(nick=nick)

    @classmethod
    def login(cls, nick, raw_password):
        """
        @return: The user if the password matches, otherwise, none.
        """
        try:
            user = User.objects.get(nick=nick)

            if user:
                m = hashlib.sha512()

                password_hex = binascii.b2a_hex(user.password)
                salt_hex = binascii.b2a_hex(user.salt)
                m.update(raw_password)
                m.update(salt_hex)
                hashed_password = m.hexdigest()

                if password_hex == hashed_password:
                    return user
        except User.DoesNotExist:
            return None
        return None

    # There's a corresponding javascript method that performs the same logic in the Signup page.
    @classmethod
    def validate_username(cls, nick):
        """
        Make sure the nickname only contains alpha numeric characters, underscores, and dashes.
        Specifically, spaces and ampersands are prohibited.
        @return: Return a tuple <nick, error> standardized nickname on success, otherwise, an empty nickname and message.
        """
        if nick and nick != "":
            nick = nick.strip()
            if len(nick) > 0:
                if re.match("^[A-z0-9_\-]+$", nick):
                    return nick, ""
                else:
                    return "", "Username can only contain letters, numbers, underscores, and dashes."
        return "", "Username must not be empty."

    def send_confirmation(self):
        """
        @return: Returns true if the email was sent, otherwie, false.
        """
        if self.active == 0:
            # TODO, send the email
            return True
        return False

    def ack_confirmation(self, confirmation):
        if self.active == 0 and self.confirmation == confirmation:
            self.active = 1
            self.save()
            return True
        return False

    def update_stats(self, relationship, personality, humor, ethnicity, body):
        self.relationship = relationship
        self.personality = personality
        self.humor = humor
        self.ethnicity = ethnicity
        self.body = body
        self.save()

    def update_age(self):
        # Should be called either by a daily process, or whenever a user's page is loaded, or the birthday is updated.
        if self.birthday:
            now = datetime.utcnow()
            age = int((now - self.birthday).days / 365.2425)
            self.age = age
            self.save()
            return True
        return False

    def update_birthday(self, birthday):
        self.birthday = birthday
        self.save()
        self.upate_age()
