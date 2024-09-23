import requests
import time  # To calculate timing
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async  # For running blocking I/O in an async view

# Display the form
def index(request):
    return render(request, 'chat/index.html')

# Asynchronous view to process the input and get the response from Ollama
@csrf_exempt
async def get_response(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')

        # Set up the API request to Ollama (local server)
        ollama_url = 'http://127.0.0.1:11434/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            'model': 'llama2',  # Assuming you're using the llama2 model
            'messages': [
                {'role': 'user', 'content': user_input}
            ]
        }

        # Capture the start time
        start_time = time.time()

        # Send request to Ollama asynchronously
        try:
            # Wrap the blocking request in sync_to_async
            response = await sync_to_async(requests.post)(ollama_url, headers=headers, json=data)

            # Calculate the elapsed time
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                response_data = response.json()
                # Extract the response content from the Ollama API
                bot_response = response_data['choices'][0]['message']['content']
            else:
                bot_response = "Error: Could not fetch a response."
        except Exception as e:
            bot_response = f"Error: {str(e)}"
            elapsed_time = None  # No timing available if an error occurred

        # Prepare the final response with timing info
        if elapsed_time is not None:
            bot_response += f"\n\nResponse Time: {elapsed_time:.2f} seconds"

        # Render the template with the bot response and timing
        return render(request, 'chat/index.html', {'response': bot_response})

    return render(request, 'chat/index.html')
