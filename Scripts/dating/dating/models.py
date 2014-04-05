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
import os
import shutil

# Django Imports
from django.db import models
from django.conf import settings
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist

# Local Imports
from util import get_file_size_bytes, get_file_md5, scale_img_and_save, delete_files_with_suffix
from dating.exceptions import ImageDimensionException

# Third Party Imports
from PIL import Image

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
    pet = models.CharField(max_length=45)

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
    def get_from_id(cls, id):
        """
        @return: The user with the given id.
        """
        return User.objects.get(id=id)

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

    def user_photos(self):
        return self.photos.all()

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

    def get_photo_with_name(self, name):
        try:
            return self.photos.filter(name=name)[0]
        except IndexError:
            return None

    def main_photo(self):
        photos = self.photos.filter(order=0).all()

        if photos and len(photos) > 0:
            photo = photos[0]
            return photo.rel_path(size="l")

        picture = "man_face.gif" if self.gender == "male" else "woman_face.gif"
        return "/".join(["", "static", "images", picture])

    def add_photo(self, name, image):
        """
        @return: Returns a tuple with the new Image, and an error message.
        If an error exists, the Image is none.
        """
        return UserPhoto.create(self.id, name, image)

    def delete_photo(self, name):
        photo = self.get_photo_with_name(name)
        if photo:
            return UserPhoto.delete_instance(self, photo)
        return False


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

class UserPhoto(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="photos", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    path = models.CharField(max_length=256)
    bytes = models.IntegerField(blank=False, null=False)
    size = models.CharField(max_length=32, blank=False, null=False)
    tag = models.CharField(max_length=256, blank=True, null=True)
    hash_md5 = models.CharField(max_length=32, blank=False, null=False)
    order = models.SmallIntegerField(blank=False, null=False)

    class Meta:
         db_table = "user_photo"

    def __unicode__(self):
        return u'%s: %s' % (self.name, self.path)

    @classmethod
    def create(cls, user_id, name, image):
        """
        @param user_id: Foreign key to user
        @param name: Image name, including extension
        @param image: Actual image file
        """

        user = User.get_from_id(user_id)
        if user:
            photos = user.photos.all()
            # Order is zero-based index
            order = (max([x.order for x in photos]) + 1) if (photos and len(photos) > 0) else 0

            tmp_root = os.path.join(settings.TMP_MEDIA_ROOT, "users", user.nick)
            if not os.path.exists(tmp_root):
                os.makedirs(tmp_root)
            tmp_path = os.path.join(tmp_root, name)

            fd = None
            try:
                fd = open(tmp_path, "wb")
                for chunk in image.chunks():
                    fd.write(chunk)
            except IOError:
                return None, "Unable to save image"
            finally:
                if fd:
                    fd.close()

            try:
                img = Image.open(tmp_path)
                width, height = img.size

                print("Width: %d, Height: %d" % (width, height))

                # Want to keep a 4:3 frame ratio
                if width < 200 or height < 266:
                    raise ImageDimensionException("Dimensions are too small")

                hash_md5 = get_file_md5(tmp_path)
                size = get_file_size_bytes(tmp_path)

                # TODO, what if the user has a photo with the same size and hash?

                # Copy the image from the temp folder to the final folder
                root = os.path.join(settings.MEDIA_ROOT, "users", user.nick)
                if not os.path.exists(root):
                    os.makedirs(root)
                path = os.path.join(root, name)
                shutil.copy2(tmp_path, path)

                # Scale the image in 4 different sizes
                # xs 50x50 used in suggestions, chat, and user "profile" settings link
                # s 120x120 used in sliders
                # m 200x266 used in search to have 4 results per row
                # l 300x400 used in profile's main picture
                scale_img_and_save(img, 50.0, 50.0, name, "xs", root)
                scale_img_and_save(img, 120.0, 120.0, name, "s", root)
                scale_img_and_save(img, 200.0, 266.0, name, "m", root, crop=False)
                scale_img_and_save(img, 300.0, 400.0, name, "l", root, crop=False)

                # Must garbage collect once done using in order to be able to delete
                del img

                photo = UserPhoto(user_id=user_id, name=name, path=path, bytes=size, size="regular",
                                  hash_md5=hash_md5, order=order)
                photo.save()
                return photo, ""
            except Exception, err:
                print("Original exception: %s" % str(err))
                error = "Unable to save image"

                if type(err).__name__ == ImageDimensionException.__name__:
                    print("Dimensions are too small")
                    error = err
                return None, error
            finally:
                # Attempt to delete the temporary image and user directory
                try:
                    if os.path.isfile(tmp_path):
                        os.remove(tmp_path)

                    if os.path.isdir(os.path.dirname(tmp_path)):
                        shutil.rmtree(os.path.dirname(tmp_path))
                except Exception, err:
                    print("Exception while deleting temp file: %s" % str(err))

        return None, "Unable to save image"

    @classmethod
    def delete_instance(cls, user, photo):
        deleted = False

        # First, delete from the database, then, delete from storage.
        curr_order = photo.order
        photo.delete()
        deleted = True
        # Reshift photos with a greater order
        user.photos.filter(order__gt=curr_order).update(order=F('order') - 1)

        try:
            if os.path.isfile(photo.path):
                os.remove(photo.path)

            # Check each of the other photo sizes
            delete_files_with_suffix(photo.path, ["xs", "s", "m", "l"])
        except Exception, err:
            print("Unable to delete files. Error: %s" % str(err))
            pass
        return deleted

    @classmethod
    def reorder_photo(cls, user, photo_name, new_index):
        try:
            photo = user.photos.get(name=photo_name)
            photos = user.photos.all()
            old_index = photo.order

            if new_index >= 0 and new_index < len(photos):
                if new_index > old_index:
                    # Moving down, get all photos in-between
                    user.photos.filter(order__range=(old_index, new_index)).update(order=F('order') - 1)
                else:
                    # Moving up, get all photos in-between
                    user.photos.filter(order__range=(new_index, old_index)).update(order=F('order') + 1)

                photo.order = new_index
                photo.save()
        except ObjectDoesNotExist, err:
            print("Exception occurred. Unable to reorder photos. %s" % str(err))

    def set_tag(self, tag):
        try:
            self.tag = tag
            self.save()
        except Exception, err:
            pass

    def rel_path(self, size=""):
        name = self.name
        if size != "":
            name_and_ext = os.path.splitext(self.name)
            name = name_and_ext[0] + "_" + size + name_and_ext[1]

        return "/".join(["", "static", "dropbox", "users", self.user.nick, name])

    def rel_path_l(self):
        return self.rel_path("l")

    def rel_path_m(self):
        return self.rel_path("m")

    def rel_path_s(self):
        return self.rel_path("s")

    def rel_path_xs(self):
        return self.rel_path("xs")

