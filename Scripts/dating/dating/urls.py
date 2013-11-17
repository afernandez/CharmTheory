from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'dating.views.home', name='home'),
	url(r'^hello/$', 'dating.views.hello',  name='hello'),
    url(r'^admin/', include(admin.site.urls))
)
