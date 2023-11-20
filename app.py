from fastapi import FastAPI, Response
import uvicorn
import requests
import os

# FastAPI app instance
app = FastAPI()

# Retrieve the API key from environment variables
APP_API_KEY = os.getenv('CONVERTER_API_KEY', None)

# Define a route for the root endpoint
@app.get('/')
async def index():
    # Make a request to the exchange rate API using the API key
    r = requests.get(f'https://v6.exchangerate-api.com/v6/{APP_API_KEY}/latest/USD')
    
    # Return the API response as a JSON with a 200 status code
    return Response(r.content, status_code=200, media_type='application/json')

# Run the FastAPI app using Uvicorn if the script is executed directly
if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=5555, log_level='info', reload=True)
