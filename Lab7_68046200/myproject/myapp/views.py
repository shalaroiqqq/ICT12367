from django.http import HttpResponse
from django.shortcuts import render

def contact(request):
    return HttpResponse("<h1>ติดต่อ 68046200 Sininat Chaemchu</h1>")

def form(request):
    return render(request, 'form.html')