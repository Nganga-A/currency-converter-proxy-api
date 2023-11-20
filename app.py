from fastapi import FastAPI,Response
import uvicorn
import requests
import os 

app = FastAPI()

APP_API_KEY = os.getenv('CONVERTER_API_KEY', None)

@app.get('/')
async def index():
    # return {"message": "Hello, World"}
    r = requests.get(f'https://v6.exchangerate-api.com/v6/{APP_API_KEY}/latest/USD')
    return Response(r.content, status_code=200, media_type='application.json')

if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=5555, log_level='info', reload=True)
