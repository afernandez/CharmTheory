from django.conf.urls import patterns, include, url
from django.contrib import admin
from dating.views import hours_ahead
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'dating.views.home', name='home'),
	url(r'^hello/$', 'dating.views.hello',  name='hello'),
	url(r'^time/$', 'dating.views.current_datetime', name='time'),
	url(r'^time/plus/(.+)/$', hours_ahead),
    url(r'^admin/', include(admin.site.urls))
)
