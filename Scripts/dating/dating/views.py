from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome Home")

def hello(request):
    return HttpResponse("Hello world")