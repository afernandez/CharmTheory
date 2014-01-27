from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

# The order is important
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
                       url(r'^profile/essay', 'dating.views.profile_essay'),    # Edit the essays
                       url(r'^profile', 'dating.views.profile'),
                       url(r'^photos/upload', 'dating.views.upload'),           # Upload a photo
                       url(r'^photos', 'dating.views.photos'),
                       url(r'^photo/(.*)/(.*)/(.*)/(.*)/(.*)/(.*)', 'dating.views.photo'),
                       url(r'^admin/', include(admin.site.urls))    # Username: alejandro, Password: alejandro
)
# Allow path to static files to be shown
urlpatterns += staticfiles_urlpatterns()