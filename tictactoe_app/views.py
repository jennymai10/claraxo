from django.shortcuts import render

def index(request):
    """
    Render the index page of the Tic Tac Toe application.

    This view handles the request to the root URL of the Tic Tac Toe application.
    It returns the rendered HTML template 'index.html', which serves as the 
    starting point for the user interface of the game.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'index.html' template.
    """
    return render(request, 'tictactoe_app/index.html')
