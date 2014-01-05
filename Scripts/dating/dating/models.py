"""
Django settings for dating project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
from django.db import models

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

    class Meta:
         db_table = "user"

    def __unicode__(self):
        return u'%s (%s %s)' % (self.nick, self.first_name, self.last_name)

    #TODO, add password
    @classmethod
    def create(cls, nick, first_name, last_name, gender):
        user = User(nick=nick, first_name=first_name, last_name=last_name, gender=gender)
        user.save()
        return user

    @classmethod
    def get_from_email(cls, email):
        """
        @return: The user with the given email.
        """
        return User.objects.get(email=email)

    @classmethod
    def login(cls, nick, password):
        """
        @return: The user if the password matches, otherwise, none.
        """
        try:
            user = User.objects.get(nick=nick)
            # TODO
            if user:  # and user.password == password:
                return user
        except User.DoesNotExist:
            return None
        return None