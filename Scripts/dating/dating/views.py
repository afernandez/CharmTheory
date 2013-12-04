from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
from django.shortcuts import render
import datetime

def home(request):
    return HttpResponse("Welcome Home")
	
def hello(request):
    return HttpResponse("Hello World")

def current_datetime(request):
    now = datetime.datetime.now()
    #t = get_template('current_datetime.html')
    #html = "<html><body>It is now %s.</body></html>" % now
    #html = t.render(Context({'current_date': now}))
    #return HttpResponse(html)
    return render(request, 'current_datetime.html', {'current_date': now, 'current_section': 'home'})
	
def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
    t = get_template('hours_ahead.html')
    html = t.render(Context({'hour_offset': offset, 'next_time': dt, 'current_section': 'future'}))
    return HttpResponse(html)