"""
Django settings for dating project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
from django.db import models
import hashlib
import binascii
import re

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
        user.save()

        # TODO, send the user an email with the confirmation
        # Provide a way to resend the email.
        # Initially, the account will be disabled until they confirm that email.
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