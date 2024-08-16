from django.http import JsonResponse
from django.http import HttpResponse

def api_status(request):
    return JsonResponse({'apistatus': 'Backend is running'})

def home(request):
    return HttpResponse("Welcome to the Tic Tac Toe Back End!")