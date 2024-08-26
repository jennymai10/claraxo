from django.shortcuts import render, redirect
from .forms import UserForm
from .models import TicTacToeUser

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