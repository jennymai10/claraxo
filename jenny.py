import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
# Navigate to the directory above the one where you've put the Tic-Tac-Toe code
config_file_path = "/Users/jennymai/Desktop/it_proj/clara_tictactoe/clara_app/config.ini"

config_file_path = os.getenv('CLARA', '/Users/jennymai/Desktop/it_proj/clara_tictactoe/clara_app/config.ini')

# Import the game module
import clara_app.tictactoe_game as ttt

# Start a game between yourself and the GPT-4 player
asyncio.run(ttt.play_game_async('human_player', 'random_player', 'dummy_experiment', 0))


# LLAMA 2 API
# from transformers import LlamaForCausalLM, LlamaTokenizer

# # Load the converted model and tokenizer
# tokenizer = LlamaTokenizer.from_pretrained("/Users/jennymai/Desktop/it_proj/clara_tictactoe/llama/llama-2-7b-hf")
# model = LlamaForCausalLM.from_pretrained("/Users/jennymai/Desktop/it_proj/clara_tictactoe/llama/llama-2-7b-hf")

# # Example usage
# input_text = "Once upon a time"
# inputs = tokenizer(input_text, return_tensors="pt")
# outputs = model.generate(inputs.input_ids, max_length=20)

# print(tokenizer.decode(outputs[0], skip_special_tokens=True))