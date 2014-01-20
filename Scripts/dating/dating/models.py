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
import calendar
import math

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

    def update_main(self, gender, orientation, city):
        self.gender = gender
        self.orientation = orientation
        self.city = city
        try:
            self.save()
        except Exception, e:
            print("Unable to save. %s" % str(e))
            pass

    def update_stats(self, relationship, personality, humor, ethnicity, body, height, education,
                     college, job, income, religion, politics, have_kids, want_kids,
                     drink, smoke, pet):
        self.relationship = relationship
        self.personality = personality
        self.humor = humor
        self.ethnicity = ethnicity
        self.body = body
        self.height = height
        self.education = education
        self.college = college
        self.job = job
        self.income = income
        self.religion = religion
        self.politics = politics
        self.have_kids = have_kids
        self.want_kids = want_kids
        self.drink = drink
        self.smoke = smoke
        self.pet = pet

        try:
            self.save()
        except Exception, e:
            print("Unable to save. %s" % str(e))
            pass

    def update_age(self):
        # Should be called either by a daily process, or whenever a user's page is loaded, or the birthday is updated.
        if self.birthday:
            now = datetime.utcnow()
            age = int((now.date() - self.birthday).days / 365.2425)
            self.age = age
            self.save()
            return True
        return False

    def update_birthday(self, birthday):
        now = datetime.utcnow()
        if birthday < now.date():
            self.birthday = birthday
            self.save()
            self.update_age()

    @classmethod
    def get_years(cls):
        years = range(datetime.now().year - 60, datetime.now().year)
        years = years[::-1]
        return years

    @classmethod
    def get_months(cls):
        # Tuple
        months = []
        for i in range(1, 13):
            months.append((i, calendar.month_name[i]))
        return months

    @classmethod
    def get_days(cls):
        return range(1, 32)

    def set_essay(self, title, info):
        """
        @return: Returns True if the essay was saved, otherwise, False.
        """
        if title and title != "":
            found = self.essays.filter(title=title).all()
            if not found or len(found) == 0:
                # Create a new one, provided that the value is non-empty
                if info and info != "":
                    user_essay = UserEssay.create(self.id, title, info)
                    return True
            elif found and len(found) == 1:
                try:
                    found[0].info = info        # Could be clearing the value
                    found[0].save()
                except Exception, e:
                    print("Error. %s" % str(e))
                    return False
                return True
            else:
                print("Error, found multiple essays for the title")

        return False

    def height_in_english(self):
        if self.height and self.height > 0:
            inches = int(math.ceil(self.height * 0.393701))
            rem_inches = inches % 12
            feet = int((inches - rem_inches) / 12)
            return "%d' %d''" % (feet, rem_inches)
        return None

    def story(self):
        try:
            return self.essays.filter(title="story")[0].info
        except IndexError:
            return ""

    def goals(self):
        try:
            return self.essays.filter(title="goals")[0].info
        except IndexError:
            return ""

    def talents(self):
        try:
            return self.essays.filter(title="talents")[0].info
        except IndexError:
            return ""

    def likes(self):
        try:
            return self.essays.filter(title="likes")[0].info
        except IndexError:
                return ""

    def message_me_if(self):
        try:
            return self.essays.filter(title="message_me_if")[0].info
        except IndexError:
            return ""

    def main_photo(self):
        node = "01"
        volume = "01"
        image = "dec2b092a63342d6a55e3810b9908d9f"
        size_ext = "m.jpeg"
        return "/".join(["", "static", "photo", "node" + node, "volume" + volume, image, size_ext])


class UserEssay(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    info = models.CharField(max_length=2048)
    user = models.ForeignKey(User, related_name="essays", on_delete=models.CASCADE)

    class Meta:
         db_table = "user_essay"

    def __unicode__(self):
        return u'%s: %s' % (self.title, self.info)


    @classmethod
    def create(cls, user_id, title, info):
        """
        @param user_id: Foreign key to user
        @param title: Field name, e.g., story, goals, talents
        @param info: Actual value
        """
        user_essay = UserEssay(user_id=user_id, title=title, info=info)
        user_essay.save()

        return user_essay
