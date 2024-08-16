# views.py in a Django app (e.g., 'authentication' app)
from django.http import JsonResponse

def api_status(request):
    return JsonResponse({'status': 'Backend is running'})

from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Tic Tac Toe Game!")