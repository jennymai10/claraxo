import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# config_file_path = os.getenv('CLARA', '/Users/jennymai/Desktop/it_proj/clara_tictactoe/clara_app/config.ini')

# import clara_app.tictactoe_game as ttt

# asyncio.run(ttt.play_game_async('human_player', 'random_player', 'dummy_experiment', 0))


# import requests
# API_URL = "https://api-inference.huggingface.co/models/openai-community/gpt2-medium"
# headers = {"Authorization": f"Bearer {API_TOKEN}"}
# def query(payload):
#     response = requests.post(API_URL, headers=headers, json=payload)
    
#     # Check if the response was successful
#     if response.status_code == 200:
#         try:
#             return response.json()  # Try to parse the response as JSON
#         except requests.exceptions.JSONDecodeError:
#             return {"error": "Invalid JSON response"}  # Handle JSON parsing error
#     else:
#         # Log or handle errors if the request fails
#         return {"error": f"Request failed with status code {response.status_code}"}

# data = query({"inputs":
#     """
#     Given the current Tic-Tac-Toe board state, where the squares occupied by X and O, and the unoccupied squares, are given using chess algebraic notation:
#     Squares occupied by X: b2
#     Squares occupied by O:
#     Unoccupied squares: a1, b1, c1, a2, c2, a3, b3, c3
#     A player wins if they can occupy all three squares on one of the following eight lines:
#     Vertical:
#     a1, a2, a3
#     b1, b2, b3
#     c1, c2, c3
#     Horizontal:
#     a1, b1, c1
#     a2, b2, c2
#     a3, b3, c3
#     Diagonal:
#     a1, b2, c3
#     a3, b2, c1
#     Return the selected move in JSON format as follows:
#     ```json
#     {
#         "selected_move": "<move>"
#     }```
#     """})
# print(data)

import google.generativeai as genai
import os

genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(
    """
    Given the current Tic-Tac-Toe board state, where the squares occupied by X and O, and the unoccupied squares, are given using chess algebraic notation:
    Squares occupied by X: b2, c3
    Squares occupied by O: c1, a3
    Unoccupied squares: a1, b1, a2, c2, a3, b3
    A player wins if they can occupy all three squares on one of the following eight lines:
    Vertical:
    a1, a2, a3
    b1, b2, b3
    c1, c2, c3
    Horizontal:
    a1, b1, c1
    a2, b2, c2
    a3, b3, c3
    Diagonal:
    a1, b2, c3
    a3, b2, c1
    You are playing as O. Return the selected move in JSON format as follows, and do not return anything else:
    ```json
    {
        "selected_move": "<move>"
    }```
    """
)
print(response.text)