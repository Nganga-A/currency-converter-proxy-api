from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import os
import redis

# FastAPI app instance
app = FastAPI()

# Retrieve the API key from environment variables
APP_API_KEY = os.getenv('CONVERTER_API_KEY', None)

# Retrieve the Redis connection URL from the environment variable 'REDIS_URL'
REDIS_URL = os.getenv('REDIS_URL')
redis_connection = redis.from_url(REDIS_URL)

"""
Allow CORS for API requests
Read more here: https://fastapi.tiangolo.com/tutorial/cors/
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin to make cross-origin requests
    allow_credentials=True,  # Allow credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP request headers
)

# Define a route for the root endpoint
@app.get('/')
async def index():
    # Check if rates are cached and return cached values if possible
    conversion_rates = redis_connection.get('USD')
    if conversion_rates:
        return Response(conversion_rates, status_code=200, media_type='application/json')

    if not APP_API_KEY:
        raise HTTPException(
            status_code=500,
            detail='Server encountered an error. Please ensure that CONVERTER_API_KEY is set.'
        )
    else:
        # Make a request to the exchange rate API using the API key
        r = requests.get(f'https://v6.exchangerate-api.com/v6/{APP_API_KEY}/latest/USD')
        if r.status_code == 200:
            # Cache newly received rates
            redis_connection.set('USD', r.content)
            redis_connection.expire('USD', 43200)
            return Response(r.content, status_code=200, media_type='application/json')
        else:
            raise HTTPException(
                status_code=502,
                detail='Server is unable to complete the request at the moment. Please try again later.'
            )

# Define a route for the latest rates for the specified currency
@app.get('/rates/{base_currency}')
async def get_rates(base_currency):
    # Check if rates are cached and return cached values if possible
    conversion_rates = redis_connection.get(base_currency)
    if conversion_rates:
        return Response(conversion_rates, status_code=200, media_type='application/json')

    if not APP_API_KEY:
        raise HTTPException(
            status_code=500,
            detail='Server encountered an error and could unfortunately not complete the request'
        )
    else:
        r = requests.get(f'https://v6.exchangerate-api.com/v6/{APP_API_KEY}/latest/{base_currency}')
        if r.status_code == 200:
            # Cache newly received rates
            redis_connection.set(base_currency, r.content)
            redis_connection.expire(base_currency, 43200)
            return Response(r.content, status_code=200, media_type='application/json')
        else:
            raise HTTPException(
                status_code=502,
                detail='Server is unable to complete the request at the moment'
            )

# Define a route for the convert endpoint
@app.get('/convert/{base_currency}/{target_currency}/{amount}')
async def convert(base_currency: str, target_currency: str, amount: float):
    if not APP_API_KEY:
        # Raise HTTPException with a 500 status code
        raise HTTPException(
            status_code=500,
            detail='Server encountered an error. Please ensure that CONVERTER_API_KEY is set.'
        )

    # Make a request to the exchange rate API using the API key
    r = requests.get(f'https://v6.exchangerate-api.com/v6/{APP_API_KEY}/pair/{base_currency}/{target_currency}/{amount}')

    if r.status_code == 200:
        # Return the API response as JSON with a 200 status code
        return Response(r.content, status_code=200, media_type='application/json')
    else:
        # Raise HTTPException with a 502 status code
        raise HTTPException(
            status_code=502,
            detail='Server is unable to complete the request at the moment. Please try again later.'
        )

if __name__ == '__main__':
    # Retrieve the port from the environment variable 'PORT', defaulting to 10,000 if not set
    port = int(os.getenv('PORT', 10000))

    # Run the FastAPI app using Uvicorn
    uvicorn.run('app:app', host='0.0.0.0', port=port, log_level='info', reload=True)
