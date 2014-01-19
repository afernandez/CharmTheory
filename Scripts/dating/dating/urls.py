from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'dating.views.home'),
                       url(r'^login', 'dating.views.login'),
                       url(r'^logout', 'dating.views.logout'),
                       url(r'^signup', 'dating.views.signup'),
                       url(r'^confirmation/(.+)/(.+)$', 'dating.views.ack_confirmation'),
                       url(r'^confirmation', 'dating.views.confirmation'),
                       url(r'^user/(.+)', 'dating.views.user'),
                       url(r'^profile/main', 'dating.views.profile_main'),      # Edit main profile settings
                       url(r'^profile/stats', 'dating.views.profile_stats'),    # Edit the stats
                       url(r'^profile', 'dating.views.profile'),
                       url(r'^admin/', include(admin.site.urls))    # Username: alejandro, Password: alejandro
)