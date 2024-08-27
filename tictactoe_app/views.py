from django.shortcuts import render, redirect
from .forms import UserForm
from .models import TicTacToeUser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('https://www.google.com/')  # Placeholder
    else:
        form = UserForm()
    return render(request, 'tictactoe_app/register.html', {'form': form})

def get_users(request):
    users = TicTacToeUser.objects.all()
    return render(request, 'tictactoe_app/users.html', {'users': users})

@csrf_exempt
def handle_login(request):
    if request.method == 'POST':  # 修复了'method'的拼写错误
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            # 硬编码的用户名和密码
            correct_username = 'my_username'
            correct_password = 'my_password'
            
            if username == correct_username and password == correct_password:
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'message': 'Login failed'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)