from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'dating.views.home', name='home'),
                       url(r'^login', 'dating.views.login', name='login'),
                       url(r'^logout', 'dating.views.logout', name='logout'),
                       url(r'^signup', 'dating.views.signup', name='signup'),
                       url(r'^admin/', include(admin.site.urls))    # Username: alejandro, Password: alejandro
)